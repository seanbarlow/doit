"""Tests for SkillTemplate parsing and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from doit_cli.models.skill_template import (
    DESCRIPTION_CHAR_BUDGET,
    SKILL_MAX_LINES,
    SkillTemplate,
)


def _write_skill(tmp_path: Path, name: str, skill_md: str, extra: dict[str, str] | None = None) -> Path:
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(skill_md)
    if extra:
        for rel, contents in extra.items():
            p = skill_dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(contents)
    return skill_dir


class TestSkillTemplateParsing:
    """Frontmatter + body splitting."""

    def test_parses_minimal_skill(self, tmp_path: Path) -> None:
        src = _write_skill(
            tmp_path,
            "doit.simple",
            "---\nname: doit.simple\ndescription: Minimal pilot skill.\n---\n\nHello.\n",
        )
        skill = SkillTemplate.from_directory(src)

        assert skill.name == "doit.simple"
        assert skill.description == "Minimal pilot skill."
        assert skill.body.strip() == "Hello."
        assert skill.when_to_use == ""

    def test_parses_all_declared_frontmatter(self, tmp_path: Path) -> None:
        fm = """---
name: doit.full
description: Everything populated.
when_to_use: When the user asks foo.
allowed-tools: Read Write
argument-hint: "[issue-number]"
model: sonnet
disable-model-invocation: true
user-invocable: false
---

Body.
"""
        src = _write_skill(tmp_path, "doit.full", fm)
        skill = SkillTemplate.from_directory(src)

        assert skill.when_to_use == "When the user asks foo."
        assert skill.allowed_tools == "Read Write"
        assert skill.argument_hint == "[issue-number]"
        assert skill.model == "sonnet"
        assert skill.disable_model_invocation is True
        assert skill.user_invocable is False

    def test_flattens_list_form_allowed_tools(self, tmp_path: Path) -> None:
        fm = """---
name: doit.list-tools
description: YAML list form.
allowed-tools:
  - Read
  - Write
  - Edit
---

x
"""
        src = _write_skill(tmp_path, "doit.list-tools", fm)
        skill = SkillTemplate.from_directory(src)
        assert skill.allowed_tools == "Read Write Edit"

    def test_discovers_supporting_files(self, tmp_path: Path) -> None:
        src = _write_skill(
            tmp_path,
            "doit.big",
            "---\nname: doit.big\ndescription: Has supporting files.\n---\n\nBody.\n",
            extra={
                "reference.md": "# Reference\n",
                "examples/sample.md": "# Example\n",
            },
        )
        skill = SkillTemplate.from_directory(src)
        names = {p.name for p in skill.supporting_files}
        assert names == {"reference.md", "sample.md"}

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            SkillTemplate.from_directory(tmp_path / "nope")

    def test_raises_on_missing_skill_md(self, tmp_path: Path) -> None:
        (tmp_path / "empty").mkdir()
        with pytest.raises(FileNotFoundError, match=r"missing SKILL\.md"):
            SkillTemplate.from_directory(tmp_path / "empty")

    def test_raises_on_unclosed_frontmatter(self, tmp_path: Path) -> None:
        src = _write_skill(tmp_path, "doit.bad", "---\nname: doit.bad\n")
        with pytest.raises(ValueError, match="closing delimiter"):
            SkillTemplate.from_directory(src)

    def test_raises_on_missing_required_field(self, tmp_path: Path) -> None:
        src = _write_skill(tmp_path, "doit.missing", "---\nname: doit.missing\n---\n\nBody\n")
        with pytest.raises(ValueError, match="description"):
            SkillTemplate.from_directory(src)


class TestSkillTemplateValidation:
    """The validate() lint — counts + name constraints."""

    def _make(self, tmp_path: Path, body: str, when_to_use: str = "") -> SkillTemplate:
        fm_when = f'when_to_use: "{when_to_use}"\n' if when_to_use else ""
        raw = f"---\nname: doit.v\ndescription: ok\n{fm_when}---\n\n{body}"
        src = _write_skill(tmp_path, "doit.v", raw)
        return SkillTemplate.from_directory(src)

    def test_clean_skill_has_no_warnings(self, tmp_path: Path) -> None:
        skill = self._make(tmp_path, "one line\n")
        assert skill.validate() == []

    def test_flags_oversized_description(self, tmp_path: Path) -> None:
        long_when = "x" * (DESCRIPTION_CHAR_BUDGET + 10)
        skill = self._make(tmp_path, "body\n", when_to_use=long_when)
        issues = skill.validate()
        assert any("description+when_to_use" in i for i in issues)

    def test_flags_oversized_skill_md(self, tmp_path: Path) -> None:
        body = "\n".join(["filler"] * (SKILL_MAX_LINES + 5)) + "\n"
        skill = self._make(tmp_path, body)
        issues = skill.validate()
        assert any(str(SKILL_MAX_LINES) in i for i in issues)
