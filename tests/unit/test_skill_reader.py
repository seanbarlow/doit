"""Tests for SkillReader (bundled skills discovery)."""

from __future__ import annotations

from pathlib import Path

import pytest

from doit_cli.models.skill_template import SkillTemplate
from doit_cli.services.skill_reader import SkillReader


class TestSkillReader:
    """Discovery of skill directories bundled with the package."""

    def _fixture_reader(self, tmp_path: Path) -> SkillReader:
        """Create a SkillReader rooted at a tmp templates/skills layout."""
        skills_root = tmp_path / "templates" / "skills"
        skills_root.mkdir(parents=True)
        return SkillReader(package_root=tmp_path)

    def _write(self, reader: SkillReader, name: str, fm_extra: str = "", body: str = "x") -> Path:
        skill_dir = reader.skills_root / name
        skill_dir.mkdir()
        content = f"---\nname: {name}\ndescription: Test skill.\n{fm_extra}---\n\n{body}\n"
        (skill_dir / "SKILL.md").write_text(content)
        return skill_dir

    def test_empty_root_returns_empty_list(self, tmp_path: Path) -> None:
        reader = self._fixture_reader(tmp_path)
        assert reader.scan_bundled_skills() == []

    def test_missing_root_returns_empty_list(self, tmp_path: Path) -> None:
        reader = SkillReader(package_root=tmp_path / "does-not-exist")
        assert reader.scan_bundled_skills() == []

    def test_discovers_multiple_skills(self, tmp_path: Path) -> None:
        reader = self._fixture_reader(tmp_path)
        self._write(reader, "doit.a")
        self._write(reader, "doit.b")
        self._write(reader, "doit.c")

        skills = reader.scan_bundled_skills()
        assert [s.name for s in skills] == ["doit.a", "doit.b", "doit.c"]

    def test_skips_underscore_prefixed_dirs(self, tmp_path: Path) -> None:
        """`_shared/` etc. are reserved for fragment files, not skills."""
        reader = self._fixture_reader(tmp_path)
        shared = reader.skills_root / "_shared"
        shared.mkdir()
        (shared / "fragment.md").write_text("# fragment\n")

        self._write(reader, "doit.ok")

        skills = reader.scan_bundled_skills()
        assert [s.name for s in skills] == ["doit.ok"]

    def test_skips_dirs_without_skill_md(self, tmp_path: Path) -> None:
        reader = self._fixture_reader(tmp_path)
        empty = reader.skills_root / "doit.empty"
        empty.mkdir()
        self._write(reader, "doit.good")

        skills = reader.scan_bundled_skills()
        assert [s.name for s in skills] == ["doit.good"]

    def test_continues_past_parse_errors(self, tmp_path: Path) -> None:
        """A malformed SKILL.md must not crash the whole scan."""
        reader = self._fixture_reader(tmp_path)
        bad = reader.skills_root / "doit.bad"
        bad.mkdir()
        (bad / "SKILL.md").write_text("---\nname: doit.bad\n")  # unclosed fm

        self._write(reader, "doit.good")

        skills = reader.scan_bundled_skills()
        assert [s.name for s in skills] == ["doit.good"]

    def test_get_skill_by_name(self, tmp_path: Path) -> None:
        reader = self._fixture_reader(tmp_path)
        self._write(reader, "doit.x")
        self._write(reader, "doit.y")

        found = reader.get_skill("doit.x")
        assert found is not None
        assert isinstance(found, SkillTemplate)
        assert found.name == "doit.x"

    def test_get_skill_returns_none_when_absent(self, tmp_path: Path) -> None:
        reader = self._fixture_reader(tmp_path)
        self._write(reader, "doit.x")
        assert reader.get_skill("doit.missing") is None


class TestBundledConstitutionPilot:
    """Integration smoke test: the shipped constitution skill parses cleanly."""

    def test_constitution_skill_exists_and_parses(self) -> None:
        reader = SkillReader()  # points at real src/doit_cli/templates/skills
        skill = reader.get_skill("doit.constitution")
        if skill is None:
            pytest.skip("constitution skill not yet bundled in this build")

        assert skill.description
        assert skill.when_to_use
        assert skill.allowed_tools
        # Frontmatter hygiene the plan enforces
        assert "handoffs" not in skill.frontmatter
        assert "effort" not in skill.frontmatter
        # Must stay under the 500-line SKILL.md budget
        assert skill.skill_md_line_count <= 500, (
            f"SKILL.md has {skill.skill_md_line_count} lines; move detail into supporting files."
        )
        # Description budget per Claude docs
        assert skill.description_char_count <= 1536
