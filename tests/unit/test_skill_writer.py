"""Tests for SkillWriter (copies skill dirs into a target project)."""

from __future__ import annotations

from pathlib import Path

import pytest

from doit_cli.models.skill_template import SkillTemplate
from doit_cli.services.skill_writer import SkillWriter


def _make_source_skill(root: Path, name: str, with_extras: bool = False) -> SkillTemplate:
    src = root / name
    src.mkdir()
    (src / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test.\n---\n\nBody.\n"
    )
    if with_extras:
        (src / "reference.md").write_text("# reference\n")
        examples = src / "examples"
        examples.mkdir()
        (examples / "sample.md").write_text("# sample\n")
    return SkillTemplate.from_directory(src)


class TestSkillWriter:
    def test_writes_skill_md_and_supporting_files(self, tmp_path: Path) -> None:
        source_root = tmp_path / "src"
        source_root.mkdir()
        skill = _make_source_skill(source_root, "doit.fancy", with_extras=True)

        project = tmp_path / "project"
        writer = SkillWriter(project_root=project)
        result = writer.write_skill(skill)

        target_dir = project / ".claude" / "skills" / "doit.fancy"
        assert target_dir.is_dir()
        assert (target_dir / "SKILL.md").is_file()
        assert (target_dir / "reference.md").is_file()
        assert (target_dir / "examples" / "sample.md").is_file()
        assert result.was_overwrite is False
        assert len(result.files_written) == 3

    def test_overwrite_true_replaces_existing(self, tmp_path: Path) -> None:
        source_root = tmp_path / "src"
        source_root.mkdir()
        skill = _make_source_skill(source_root, "doit.rewrite")

        project = tmp_path / "project"
        target_dir = project / ".claude" / "skills" / "doit.rewrite"
        target_dir.mkdir(parents=True)
        (target_dir / "stale.md").write_text("stale\n")

        writer = SkillWriter(project_root=project)
        result = writer.write_skill(skill, overwrite=True)

        assert result.was_overwrite is True
        assert not (target_dir / "stale.md").exists()
        assert (target_dir / "SKILL.md").is_file()

    def test_overwrite_false_raises_on_existing(self, tmp_path: Path) -> None:
        source_root = tmp_path / "src"
        source_root.mkdir()
        skill = _make_source_skill(source_root, "doit.safe")

        project = tmp_path / "project"
        target_dir = project / ".claude" / "skills" / "doit.safe"
        target_dir.mkdir(parents=True)

        writer = SkillWriter(project_root=project)
        with pytest.raises(FileExistsError):
            writer.write_skill(skill, overwrite=False)

    def test_write_all_iterates(self, tmp_path: Path) -> None:
        source_root = tmp_path / "src"
        source_root.mkdir()
        skills = [
            _make_source_skill(source_root, "doit.one"),
            _make_source_skill(source_root, "doit.two"),
        ]

        project = tmp_path / "project"
        writer = SkillWriter(project_root=project)
        results = writer.write_all(skills)

        assert [r.skill_name for r in results] == ["doit.one", "doit.two"]
        for r in results:
            assert (r.target_dir / "SKILL.md").is_file()
