"""Contract: every shipped .github/prompts/*.prompt.md matches the April 2026 Copilot spec.

If this test fails after editing a source template, regenerate the
prompts with `doit sync-prompts` (or run the transformer directly) and
commit the result — the two directories must stay in sync.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from doit_cli.models.sync_models import CommandTemplate
from doit_cli.services.prompt_transformer import PromptTransformer

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"
COMMANDS_DIR = REPO_ROOT / "src" / "doit_cli" / "templates" / "commands"

# Fields VS Code recognizes per https://code.visualstudio.com/docs/copilot/customization/prompt-files
# (April 2026). Anything else in the frontmatter is considered a leak.
ALLOWED_COPILOT_FIELDS = {"description", "agent", "tools", "model", "mode"}
FORBIDDEN_CLAUDE_FIELDS = {"allowed-tools", "handoffs", "effort", "argument-hint", "when_to_use"}


def _collect_prompts() -> list[Path]:
    return sorted(PROMPTS_DIR.glob("doit.*.prompt.md"))


@pytest.mark.parametrize("prompt_path", _collect_prompts(), ids=lambda p: p.name)
class TestCopilotPromptFrontmatter:
    """Per-file assertions on the shipped prompts."""

    def test_has_frontmatter(self, prompt_path: Path) -> None:
        content = prompt_path.read_text(encoding="utf-8")
        assert content.startswith("---\n"), f"{prompt_path.name} is missing frontmatter"

    def test_frontmatter_only_uses_allowed_fields(self, prompt_path: Path) -> None:
        fm = _load_frontmatter(prompt_path)
        unknown = set(fm) - ALLOWED_COPILOT_FIELDS
        assert not unknown, (
            f"{prompt_path.name} frontmatter has fields VS Code doesn't "
            f"recognize: {sorted(unknown)}"
        )

    def test_frontmatter_has_no_claude_leaks(self, prompt_path: Path) -> None:
        fm = _load_frontmatter(prompt_path)
        leaks = set(fm) & FORBIDDEN_CLAUDE_FIELDS
        assert not leaks, (
            f"{prompt_path.name} frontmatter still contains Claude-specific fields: {sorted(leaks)}"
        )

    def test_agent_is_agent_mode(self, prompt_path: Path) -> None:
        fm = _load_frontmatter(prompt_path)
        assert fm.get("agent") == "agent", (
            f"{prompt_path.name} should declare `agent: agent` so Copilot "
            f"can auto-select tools; got {fm.get('agent')!r}"
        )

    def test_has_description(self, prompt_path: Path) -> None:
        fm = _load_frontmatter(prompt_path)
        assert fm.get("description"), f"{prompt_path.name} is missing description"

    def test_no_dollar_arguments_leak(self, prompt_path: Path) -> None:
        content = prompt_path.read_text(encoding="utf-8")
        assert "$ARGUMENTS" not in content, (
            f"{prompt_path.name} still contains Claude's $ARGUMENTS "
            f"placeholder; Copilot uses ${{input:args}} instead."
        )


def test_every_command_has_a_matching_prompt() -> None:
    """Each source command template has a regenerated prompt counterpart."""
    commands = {p.stem for p in COMMANDS_DIR.glob("doit.*.md")}
    prompts = {p.name.removesuffix(".prompt.md") for p in _collect_prompts()}
    missing = commands - prompts
    assert not missing, f"Missing .prompt.md for: {sorted(missing)}"


def test_prompts_match_transformer_output() -> None:
    """Shipped prompts equal what the current transformer would emit.

    If this fails: the transformer changed but the .github/prompts/
    directory wasn't regenerated. Run the transformer or invoke
    `doit sync-prompts --agent copilot` and commit the result.
    """
    transformer = PromptTransformer()
    mismatches: list[str] = []

    for src in sorted(COMMANDS_DIR.glob("doit.*.md")):
        template = CommandTemplate.from_path(src)
        expected = transformer.transform(template)
        dst = PROMPTS_DIR / f"{src.stem}.prompt.md"
        if not dst.exists():
            mismatches.append(f"{dst.name}: missing")
            continue
        actual = dst.read_text(encoding="utf-8")
        if actual != expected:
            mismatches.append(f"{dst.name}: out of sync with transformer output")

    assert not mismatches, "\n".join(mismatches)


def _load_frontmatter(path: Path) -> dict[str, object]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    end = content.index("\n---", 3)
    fm_text = content[3:end].strip()
    parsed = yaml.safe_load(fm_text) or {}
    assert isinstance(parsed, dict), f"frontmatter must be a YAML mapping in {path.name}"
    return parsed
