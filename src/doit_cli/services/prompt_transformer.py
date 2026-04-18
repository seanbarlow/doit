"""Transform doit command templates into GitHub Copilot `.prompt.md` files.

The source templates in `src/doit_cli/templates/commands/` are authored for
Claude Code (see https://code.claude.com/docs/en/skills) and carry Claude-
specific frontmatter fields: `allowed-tools`, `handoffs`, `effort`. VS Code
Copilot's `.prompt.md` spec (April 2026,
https://code.visualstudio.com/docs/copilot/customization/prompt-files)
recognizes a different set: `description`, `agent`, `tools`, `model`.

This transformer:

1. Rewrites frontmatter to the Copilot-native shape
   (`description`, `agent: agent`, `tools: [...]`).
2. Maps the Claude `allowed-tools` entries to VS Code tool identifiers via
   a table. GitHub CLI-heavy commands also get the `githubRepo` tool.
3. Rewrites `$ARGUMENTS` / `$N` placeholders to Copilot's `${input:...}`
   variable syntax so the prompt prompts the user at invocation time.

The body (markdown content below the frontmatter) is preserved verbatim
apart from the placeholder rewrite — instructions that work for Claude
generally work for Copilot once tool names are normalized.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a hard dependency
    yaml = None  # type: ignore[assignment]

from ..models.sync_models import CommandTemplate

# Mapping: Claude `allowed-tools` token -> Copilot tool identifier(s).
# Claude tools are coarse-grained verbs; Copilot tools are named after
# the VS Code feature they expose. Multiple Claude tools can map to the
# same Copilot tool — we deduplicate at the end.
_CLAUDE_TO_COPILOT_TOOLS: dict[str, tuple[str, ...]] = {
    "Read": ("editFiles",),
    "Write": ("editFiles",),
    "Edit": ("editFiles",),
    "Glob": ("search", "codebase"),
    "Grep": ("search", "codebase"),
    "Bash": ("runCommands",),
}

# If the body mentions the `gh` CLI, also grant githubRepo so Copilot can
# read issues/PRs directly. Heuristic; the alternative is per-template
# metadata which isn't worth the extra frontmatter in every file.
_GH_MARKERS = ("gh pr", "gh issue", "gh api", "gh auth")


class PromptTransformer:
    """Rewrites a Claude-format command template as a Copilot `.prompt.md`."""

    def transform(self, template: CommandTemplate) -> str:
        """Return the Copilot-native prompt content for `template`."""
        source_fm, body = _split_frontmatter(template.content)
        copilot_fm = self._build_copilot_frontmatter(source_fm, body)
        new_body = self._rewrite_placeholders(body)
        return _render(copilot_fm, new_body)

    # -- frontmatter -----------------------------------------------------

    def _build_copilot_frontmatter(
        self, source_fm: dict[str, object], body: str
    ) -> dict[str, object]:
        """Map Claude frontmatter to the VS Code Copilot schema.

        Drops: `allowed-tools`, `handoffs`, `effort` (not VS Code-recognized).
        Keeps: `description`, `model` (if present and valid).
        Adds: `agent: agent`, `tools: [...]` (derived from allowed-tools + body).
        """
        out: dict[str, object] = {}
        description = source_fm.get("description")
        if description:
            out["description"] = str(description).strip()

        out["agent"] = "agent"

        tools = self._derive_tools(source_fm.get("allowed-tools", ""), body)
        if tools:
            out["tools"] = tools

        # Pass through model if the source overrode it — VS Code accepts it.
        model = source_fm.get("model")
        if model:
            out["model"] = str(model)

        return out

    def _derive_tools(self, allowed_tools: object, body: str) -> list[str]:
        """Return the Copilot `tools:` list for this template."""
        tokens = _tokenize_allowed_tools(allowed_tools)
        mapped: list[str] = []
        for tok in tokens:
            for copilot_tool in _CLAUDE_TO_COPILOT_TOOLS.get(tok, ()):
                if copilot_tool not in mapped:
                    mapped.append(copilot_tool)

        if any(marker in body for marker in _GH_MARKERS) and "githubRepo" not in mapped:
            mapped.append("githubRepo")

        return mapped

    # -- body placeholders ----------------------------------------------

    def _rewrite_placeholders(self, body: str) -> str:
        """Convert Claude `$ARGUMENTS` / `$N` to Copilot `${input:...}` variables."""
        # The canonical user-input code block at the top of most templates.
        body = re.sub(
            r"```text\s*\n\$ARGUMENTS\s*\n```",
            "${input:args:Describe what you want to do for this command.}",
            body,
        )
        # Any remaining standalone $ARGUMENTS references.
        body = body.replace("$ARGUMENTS", "${input:args}")

        # Positional arguments: $0, $1, $2 -> ${input:argN}
        def positional_sub(match: re.Match[str]) -> str:
            index = int(match.group(1))
            return f"${{input:arg{index}}}"

        body = re.sub(r"\$(\d+)\b", positional_sub, body)
        return body


# --------------------------------------------------------------------------
# helpers


def _tokenize_allowed_tools(value: object) -> list[str]:
    """Normalize the `allowed-tools` value into a flat list of tool names.

    Claude Code accepts both comma-separated strings and YAML lists, and
    allows `Bash(pattern)` constraints; this strips the parenthesized
    constraints and returns just the tool name.
    """
    if isinstance(value, list):
        items: Iterable[str] = (str(v) for v in value)
    else:
        text = str(value).replace(",", " ")
        items = text.split()

    result: list[str] = []
    for item in items:
        name = re.sub(r"\(.*?\)", "", item).strip()
        if name and name not in result:
            result.append(name)
    return result


def _split_frontmatter(raw: str) -> tuple[dict[str, object], str]:
    """Split YAML frontmatter from the body. Returns ({}, raw) if absent."""
    if not raw.startswith("---"):
        return {}, raw

    try:
        end = raw.index("\n---", 3)
    except ValueError:
        return {}, raw  # malformed; leave body untouched

    fm_text = raw[3:end].strip()
    body = raw[end + len("\n---") :].lstrip("\n")

    if yaml is None:  # pragma: no cover
        return {}, body

    parsed = yaml.safe_load(fm_text) or {}
    if not isinstance(parsed, dict):
        return {}, body
    return parsed, body


def _render(frontmatter: dict[str, object], body: str) -> str:
    """Serialize frontmatter + body back into a `.prompt.md` string."""
    if yaml is None:  # pragma: no cover
        return body
    dumped = yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False).strip()
    return f"---\n{dumped}\n---\n\n{body.lstrip()}"
