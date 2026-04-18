"""Data model for Agent Skills directory-based templates.

The Agent Skills standard (https://agentskills.io) represents a skill as a
**directory** containing a required `SKILL.md` plus optional supporting files.
This module parses such a directory into a `SkillTemplate` instance.

This model is parallel to `CommandTemplate` (which represents a single flat
`.md` file in the legacy `.claude/commands/` layout). Both formats are
supported during the deprecation window so users can migrate at their own
pace.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a hard dependency
    yaml = None  # type: ignore[assignment]


SKILL_ENTRYPOINT = "SKILL.md"

# Fields we enforce presence / shape on. Everything else is passed through.
REQUIRED_FRONTMATTER = ("name", "description")

# Per the April 2026 Claude Code docs, the combined description + when_to_use
# is truncated at this many characters in the skill listing.
DESCRIPTION_CHAR_BUDGET = 1_536

# Per Anthropic guidance, keep SKILL.md under this many lines. Supporting
# files absorb the overflow and are loaded on demand by Claude.
SKILL_MAX_LINES = 500


@dataclass
class SkillTemplate:
    """A parsed Agent-Skills-format skill directory.

    Use `SkillTemplate.from_directory(path)` to parse a skill on disk; the
    frontmatter is exposed via the typed attributes below and the full list
    of files (including supporting files like `examples/` or `reference.md`)
    is available via `supporting_files`.
    """

    name: str
    """Skill name (also the directory name). Becomes `/skill-name` at runtime."""

    directory: Path
    """Absolute path to the skill directory."""

    description: str
    """One-sentence summary of what the skill does."""

    modified_at: datetime
    """Last-modified timestamp of SKILL.md."""

    when_to_use: str = ""
    """Optional trigger keywords / example phrases."""

    allowed_tools: str = ""
    """Tool permission string (space-separated per Anthropic docs, or comma-
    separated — we preserve the user's form rather than re-normalizing)."""

    argument_hint: str = ""
    """Hint shown in the / menu autocomplete (e.g. `[issue-number]`)."""

    model: str = ""
    """Override model for this skill. Empty means inherit from session."""

    disable_model_invocation: bool = False
    """When True, only the user can invoke via `/name`."""

    user_invocable: bool = True
    """When False, hides from the / menu (Claude-only)."""

    frontmatter: dict[str, Any] = field(default_factory=dict, repr=False)
    """Full parsed frontmatter, including fields not modeled above."""

    body: str = field(default="", repr=False)
    """The SKILL.md content following the frontmatter block."""

    supporting_files: list[Path] = field(default_factory=list, repr=False)
    """All other files in the skill directory, as absolute paths."""

    # -- lifecycle --------------------------------------------------------

    @classmethod
    def from_directory(cls, directory: Path) -> SkillTemplate:
        """Parse a skill directory into a SkillTemplate.

        Raises:
            FileNotFoundError: the directory or SKILL.md is missing.
            ValueError: SKILL.md has no closing frontmatter delimiter or
                is missing required fields.
        """
        if not directory.is_dir():
            raise FileNotFoundError(f"Skill directory not found: {directory}")

        skill_md = directory / SKILL_ENTRYPOINT
        if not skill_md.is_file():
            raise FileNotFoundError(
                f"Skill is missing {SKILL_ENTRYPOINT}: {directory}"
            )

        raw = skill_md.read_text(encoding="utf-8")
        fm, body = _split_frontmatter(raw)
        modified_at = datetime.fromtimestamp(skill_md.stat().st_mtime)

        for field_name in REQUIRED_FRONTMATTER:
            if field_name not in fm:
                raise ValueError(
                    f"Skill {directory.name}/{SKILL_ENTRYPOINT} is missing "
                    f"required frontmatter key '{field_name}'."
                )

        supporting = sorted(
            p
            for p in directory.rglob("*")
            if p.is_file() and p.resolve() != skill_md.resolve()
        )

        return cls(
            name=str(fm["name"]),
            directory=directory,
            description=str(fm["description"]),
            when_to_use=str(fm.get("when_to_use", "")),
            allowed_tools=_flatten(fm.get("allowed-tools", "")),
            argument_hint=str(fm.get("argument-hint", "")),
            model=str(fm.get("model", "")),
            disable_model_invocation=bool(fm.get("disable-model-invocation", False)),
            user_invocable=bool(fm.get("user-invocable", True)),
            frontmatter=fm,
            body=body,
            supporting_files=supporting,
            modified_at=modified_at,
        )

    # -- validation -------------------------------------------------------

    @property
    def description_char_count(self) -> int:
        """Combined description + when_to_use length used by Claude's skill listing."""
        return len(self.description) + len(self.when_to_use)

    @property
    def skill_md_line_count(self) -> int:
        """Line count of SKILL.md — keep under SKILL_MAX_LINES per April 2026 guidance."""
        return self.body.count("\n") + 1

    def validate(self) -> list[str]:
        """Return a list of human-readable warnings. Empty list = clean.

        Checks enforced here mirror the constraints documented by Anthropic
        in https://code.claude.com/docs/en/skills as of April 2026.
        """
        issues: list[str] = []
        if self.description_char_count > DESCRIPTION_CHAR_BUDGET:
            issues.append(
                f"{self.name}: combined description+when_to_use is "
                f"{self.description_char_count} chars (budget is "
                f"{DESCRIPTION_CHAR_BUDGET} before Claude truncates)."
            )
        if self.skill_md_line_count > SKILL_MAX_LINES:
            issues.append(
                f"{self.name}: SKILL.md is {self.skill_md_line_count} lines "
                f"(target is <= {SKILL_MAX_LINES}; move detail into "
                f"supporting files)."
            )
        if len(self.name) > 64:
            issues.append(f"{self.name}: name exceeds 64-char limit.")
        return issues


# --------------------------------------------------------------------------
# helpers


def _flatten(value: Any) -> str:
    """Render an allowed-tools value as a string regardless of list vs string form."""
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value)


def _split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from the body. Returns ({}, raw) when no frontmatter."""
    if not raw.startswith("---"):
        return {}, raw

    try:
        end = raw.index("\n---", 3)
    except ValueError as exc:
        raise ValueError("SKILL.md has opening '---' but no closing delimiter.") from exc

    fm_text = raw[3:end].strip()
    body = raw[end + len("\n---") :].lstrip("\n")

    if yaml is None:  # pragma: no cover
        raise RuntimeError(
            "pyyaml is required to parse SKILL.md frontmatter but is not installed."
        )

    parsed = yaml.safe_load(fm_text) or {}
    if not isinstance(parsed, dict):
        raise ValueError("SKILL.md frontmatter must be a YAML mapping.")
    return parsed, body
