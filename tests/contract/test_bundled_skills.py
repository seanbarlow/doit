"""Contract: every shipped skill under templates/skills/ meets the April 2026 spec.

Parametrized over every skill directory found. A new skill gets checked
automatically once its directory exists; no test file edit required.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from doit_cli.models.skill_template import (
    DESCRIPTION_CHAR_BUDGET,
    SKILL_MAX_LINES,
    SkillTemplate,
)
from doit_cli.services.skill_reader import SkillReader


def _bundled_skills() -> list[SkillTemplate]:
    return SkillReader().scan_bundled_skills()


SKILLS = _bundled_skills()


@pytest.mark.parametrize("skill", SKILLS, ids=lambda s: s.name)
class TestShippedSkillFrontmatter:
    """Every bundled skill obeys the April 2026 SKILL.md contract."""

    def test_required_fields_present(self, skill: SkillTemplate) -> None:
        assert skill.name, "frontmatter missing `name`"
        assert skill.description, "frontmatter missing `description`"

    def test_recommended_fields_present(self, skill: SkillTemplate) -> None:
        assert skill.when_to_use, (
            f"{skill.name}: missing `when_to_use` — Claude needs trigger "
            f"keywords to know when to load the skill automatically."
        )
        assert skill.allowed_tools, (
            f"{skill.name}: missing `allowed-tools` — without it, Claude "
            f"will prompt for every tool use."
        )

    def test_no_claude_frontmatter_leaks(self, skill: SkillTemplate) -> None:
        """handoffs and effort are doit-only / default-inherited and must not ship."""
        assert "handoffs" not in skill.frontmatter, (
            f"{skill.name}: frontmatter has `handoffs:` — that field isn't "
            f"native to Claude Code; inline a 'Next Steps' section instead."
        )
        assert "effort" not in skill.frontmatter, (
            f"{skill.name}: frontmatter hard-codes `effort:` — let it "
            f"inherit from the session."
        )

    def test_under_line_budget(self, skill: SkillTemplate) -> None:
        assert skill.skill_md_line_count <= SKILL_MAX_LINES, (
            f"{skill.name}: SKILL.md is {skill.skill_md_line_count} lines "
            f"(budget is {SKILL_MAX_LINES}); move detail into supporting files."
        )

    def test_under_description_budget(self, skill: SkillTemplate) -> None:
        assert skill.description_char_count <= DESCRIPTION_CHAR_BUDGET, (
            f"{skill.name}: description+when_to_use is "
            f"{skill.description_char_count} chars (budget is "
            f"{DESCRIPTION_CHAR_BUDGET})."
        )

    def test_validate_returns_no_issues(self, skill: SkillTemplate) -> None:
        """SkillTemplate.validate() catches all the above plus name length."""
        assert skill.validate() == []


def test_every_command_has_a_skill_counterpart() -> None:
    """For every doit.*.md command template, ensure a skill dir exists.

    This catches templates we forgot to migrate. Pilot phases will have
    gaps; when the gap closes, remove the `xfail` markers.
    """
    commands_dir = (
        Path(__file__).resolve().parents[2]
        / "src" / "doit_cli" / "templates" / "commands"
    )
    command_names = {p.stem for p in commands_dir.glob("doit.*.md")}
    skill_names = {s.name for s in SKILLS}

    # Record the migration status so the test fails loud when someone
    # adds a new command template without a skill counterpart.
    not_yet_migrated = command_names - skill_names
    expected_not_yet = {
        "doit.specit",
        "doit.researchit",
        "doit.documentit",
        "doit.scaffoldit",
    }
    assert not_yet_migrated == expected_not_yet, (
        f"Migration delta changed. Previously unmigrated: {expected_not_yet}. "
        f"Now unmigrated: {not_yet_migrated}. "
        f"Either finish the migration or update this test's expected set."
    )
