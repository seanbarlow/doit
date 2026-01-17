"""Parser for extracting requirements from spec.md files."""

import re
from pathlib import Path
from typing import Optional

from ..models.crossref_models import Requirement


class RequirementParser:
    """Parses spec.md files to extract functional requirements.

    This parser extracts FR-XXX requirements from specification files
    using the standard format: `- **FR-XXX**: Description text`
    """

    # Pattern to match: - **FR-XXX**: Description
    # Captures: group(1) = FR-XXX, group(2) = description
    REQUIREMENT_PATTERN = re.compile(
        r"^\s*-\s*\*\*(?P<id>FR-\d{3})\*\*:\s*(?P<description>.+)$",
        re.MULTILINE,
    )

    def __init__(self, spec_path: Optional[Path] = None) -> None:
        """Initialize parser with optional spec file path.

        Args:
            spec_path: Path to spec.md file. Can be set later via parse().
        """
        self.spec_path = spec_path

    def parse(self, spec_path: Optional[Path] = None) -> list[Requirement]:
        """Parse spec.md and extract all functional requirements.

        Args:
            spec_path: Path to spec.md file. Overrides constructor path.

        Returns:
            List of Requirement objects sorted by ID.

        Raises:
            FileNotFoundError: If spec file doesn't exist.
            ValueError: If no spec path provided.
        """
        path = spec_path or self.spec_path
        if path is None:
            raise ValueError("No spec path provided")

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {path}")

        content = path.read_text(encoding="utf-8")
        return self.parse_content(content, str(path))

    def parse_content(self, content: str, spec_path: str) -> list[Requirement]:
        """Parse content string and extract requirements.

        Args:
            content: Full content of spec.md file.
            spec_path: Path to associate with extracted requirements.

        Returns:
            List of Requirement objects sorted by ID.
        """
        requirements: list[Requirement] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            match = self.REQUIREMENT_PATTERN.match(line)
            if match:
                req = Requirement(
                    id=match.group("id"),
                    spec_path=spec_path,
                    description=match.group("description").strip(),
                    line_number=line_num,
                )
                requirements.append(req)

        # Sort by requirement ID (FR-001, FR-002, etc.)
        requirements.sort(key=lambda r: r.id)
        return requirements

    def get_requirement(
        self, requirement_id: str, spec_path: Optional[Path] = None
    ) -> Optional[Requirement]:
        """Get a specific requirement by ID.

        Args:
            requirement_id: The FR-XXX ID to find.
            spec_path: Path to spec.md file.

        Returns:
            Requirement if found, None otherwise.
        """
        requirements = self.parse(spec_path)
        for req in requirements:
            if req.id == requirement_id:
                return req
        return None

    def get_requirement_ids(self, spec_path: Optional[Path] = None) -> list[str]:
        """Get list of all requirement IDs in a spec.

        Args:
            spec_path: Path to spec.md file.

        Returns:
            List of FR-XXX IDs.
        """
        requirements = self.parse(spec_path)
        return [req.id for req in requirements]
