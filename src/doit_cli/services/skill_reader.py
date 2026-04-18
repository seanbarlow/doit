"""Discover Agent-Skills-format skill directories bundled with the package.

`SkillReader.scan_bundled_skills()` returns one `SkillTemplate` per skill
found under `src/doit_cli/templates/skills/`. Both the top-level skill
directories and their supporting files are discovered here; writing them
to a project belongs to `SkillWriter`.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..models.skill_template import SKILL_ENTRYPOINT, SkillTemplate

logger = logging.getLogger(__name__)


class SkillReader:
    """Scans the bundled skills directory."""

    BUNDLED_RELATIVE_PATH = Path("templates") / "skills"

    def __init__(self, package_root: Path | None = None) -> None:
        """Initialize the reader.

        Args:
            package_root: Path to the `src/doit_cli/` package dir. Defaults
                to the directory containing the `doit_cli` package.
        """
        if package_root is None:
            # Walk up from this file: services/skill_reader.py -> services -> doit_cli
            package_root = Path(__file__).resolve().parent.parent
        self.package_root = package_root
        self.skills_root = package_root / self.BUNDLED_RELATIVE_PATH

    def scan_bundled_skills(self) -> list[SkillTemplate]:
        """Return every valid skill under the bundled skills root.

        A valid skill is any immediate child directory of `skills_root`
        whose name does not begin with `_` (reserved for `_shared/` etc.)
        and which contains a `SKILL.md` file.

        Invalid directories are logged and skipped, not raised — this lets
        the CLI keep working if one template has a parse error while we're
        editing it.
        """
        if not self.skills_root.is_dir():
            logger.debug("skills root does not exist: %s", self.skills_root)
            return []

        skills: list[SkillTemplate] = []
        for child in sorted(self.skills_root.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith("_"):
                continue
            if not (child / SKILL_ENTRYPOINT).is_file():
                logger.debug("skipping %s (no %s)", child, SKILL_ENTRYPOINT)
                continue
            try:
                skills.append(SkillTemplate.from_directory(child))
            except (OSError, ValueError) as exc:
                logger.warning("failed to parse skill %s: %s", child, exc)

        return skills

    def get_skill(self, name: str) -> SkillTemplate | None:
        """Return the skill with the given name, or None if not found."""
        for skill in self.scan_bundled_skills():
            if skill.name == name:
                return skill
        return None
