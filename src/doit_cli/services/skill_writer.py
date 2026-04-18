"""Write Agent-Skills-format skill directories to a target project.

Mirrors `CommandWriter`'s safe-copy pattern but at the directory level —
each skill becomes `<project>/.claude/skills/<name>/` with SKILL.md and
any supporting files copied verbatim.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from ..models.skill_template import SkillTemplate

logger = logging.getLogger(__name__)


@dataclass
class SkillWriteResult:
    """Outcome of writing a single skill."""

    skill_name: str
    target_dir: Path
    files_written: list[Path]
    was_overwrite: bool


class SkillWriter:
    """Writes bundled skills into a project's `.claude/skills/` directory."""

    DEFAULT_SKILLS_DIR = ".claude/skills"

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.skills_dir = self.project_root / self.DEFAULT_SKILLS_DIR

    def write_skill(self, skill: SkillTemplate, *, overwrite: bool = True) -> SkillWriteResult:
        """Copy a skill directory into the target project.

        Args:
            skill: Parsed SkillTemplate from the bundled source.
            overwrite: When False, raises FileExistsError if the target
                directory already exists. When True (default), the target
                is replaced atomically — existing user edits are lost,
                consistent with `.claude/commands/` behavior.
        """
        target_dir = self.skills_dir / skill.directory.name
        was_overwrite = target_dir.exists()

        if was_overwrite and not overwrite:
            raise FileExistsError(f"Skill already exists at {target_dir}")

        if was_overwrite:
            shutil.rmtree(target_dir)

        target_dir.mkdir(parents=True, exist_ok=True)

        files_written: list[Path] = []

        # Copy SKILL.md first so the entrypoint exists even if supporting
        # files fail partway.
        src_skill_md = skill.directory / "SKILL.md"
        dst_skill_md = target_dir / "SKILL.md"
        shutil.copy2(src_skill_md, dst_skill_md)
        files_written.append(dst_skill_md)

        for source in skill.supporting_files:
            rel = source.relative_to(skill.directory)
            dst = target_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dst)
            files_written.append(dst)

        logger.debug("wrote skill %s to %s (%d files)", skill.name, target_dir, len(files_written))
        return SkillWriteResult(
            skill_name=skill.name,
            target_dir=target_dir,
            files_written=files_written,
            was_overwrite=was_overwrite,
        )

    def write_all(
        self, skills: list[SkillTemplate], *, overwrite: bool = True
    ) -> list[SkillWriteResult]:
        """Write multiple skills, returning per-skill results."""
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        return [self.write_skill(s, overwrite=overwrite) for s in skills]
