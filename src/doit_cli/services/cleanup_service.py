"""Cleanup service for constitution/tech-stack separation.

This module provides the CleanupService that analyzes constitution.md,
extracts tech-stack sections, and creates a separate tech-stack.md file.
"""

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.cleanup_models import AnalysisResult, CleanupResult

logger = logging.getLogger(__name__)

# Section headers that indicate tech-stack content
TECH_SECTIONS = ["Tech Stack", "Infrastructure", "Deployment"]

# Keywords for fallback detection (if headers are non-standard)
TECH_KEYWORDS = [
    "language",
    "framework",
    "library",
    "hosting",
    "cloud",
    "database",
    "cicd",
    "ci/cd",
    "pipeline",
    "environment",
]

# Cross-reference text to add to constitution
CONSTITUTION_CROSS_REF = (
    "\n> **See also**: [Tech Stack](tech-stack.md) for languages, "
    "frameworks, and deployment details.\n"
)

# Cross-reference text to add to tech-stack
TECH_STACK_CROSS_REF = (
    "\n> **See also**: [Constitution](constitution.md) for project "
    "principles and governance.\n"
)

# Tech-stack template header
TECH_STACK_HEADER = """# {project_name} Tech Stack
{cross_ref}
"""


class CleanupService:
    """Service for cleaning up constitution files.

    Analyzes constitution.md to identify tech-stack sections,
    creates backups, and extracts content to tech-stack.md.
    """

    def __init__(self, project_root: Path):
        """Initialize CleanupService.

        Args:
            project_root: Root directory of the project.
        """
        self.project_root = project_root
        self.memory_dir = project_root / ".doit" / "memory"
        self.constitution_path = self.memory_dir / "constitution.md"
        self.tech_stack_path = self.memory_dir / "tech-stack.md"

    def analyze(self) -> AnalysisResult:
        """Analyze constitution content to identify tech sections.

        Returns:
            AnalysisResult with categorized sections.
        """
        if not self.constitution_path.exists():
            logger.warning(f"Constitution not found: {self.constitution_path}")
            return AnalysisResult()

        content = self.constitution_path.read_text()
        return self._parse_sections(content)

    def _parse_sections(self, content: str) -> AnalysisResult:
        """Parse markdown content into sections by H2 headers.

        Args:
            content: Full markdown content.

        Returns:
            AnalysisResult with categorized sections.
        """
        result = AnalysisResult()

        # Extract header (everything before first H2)
        parts = re.split(r"^(## .+)$", content, flags=re.MULTILINE)

        if parts:
            result.header_content = parts[0].strip()

        # Process sections (header, content pairs)
        for i in range(1, len(parts), 2):
            if i + 1 >= len(parts):
                break

            header = parts[i].strip()
            body = parts[i + 1].strip() if i + 1 < len(parts) else ""

            # Extract section name from header
            section_name = header.replace("## ", "").strip()

            # Full section content including header
            section_content = f"{header}\n\n{body}"

            # Categorize section
            if self._is_tech_section(section_name, body):
                result.tech_sections[section_name] = section_content
            elif self._is_unclear_section(section_name, body):
                result.unclear_sections[section_name] = section_content
            else:
                result.preserved_sections[section_name] = section_content

        return result

    def _is_tech_section(self, header: str, content: str) -> bool:
        """Determine if a section is tech-stack content.

        Prioritizes header matching over keyword analysis.

        Args:
            header: Section header text.
            content: Section body content.

        Returns:
            True if section should be extracted to tech-stack.
        """
        # Check exact header match first
        header_lower = header.lower()
        for tech_section in TECH_SECTIONS:
            if tech_section.lower() in header_lower:
                return True

        # Fallback to keyword analysis
        combined = (header + " " + content).lower()
        keyword_count = sum(1 for kw in TECH_KEYWORDS if kw in combined)
        return keyword_count >= 3

    def _is_unclear_section(self, header: str, content: str) -> bool:
        """Determine if a section needs manual review.

        Args:
            header: Section header text.
            content: Section body content.

        Returns:
            True if section categorization is unclear.
        """
        # Sections with some tech keywords but not enough for auto-extraction
        combined = (header + " " + content).lower()
        keyword_count = sum(1 for kw in TECH_KEYWORDS if kw in combined)
        return 1 <= keyword_count < 3

    def create_backup(self) -> Optional[Path]:
        """Create timestamped backup of constitution.md.

        Returns:
            Path to backup file, or None if backup failed.
        """
        if not self.constitution_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.constitution_path.with_suffix(f".{timestamp}.bak")

        try:
            shutil.copy2(self.constitution_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except OSError as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def cleanup(
        self,
        dry_run: bool = False,
        merge_existing: bool = False,
    ) -> CleanupResult:
        """Perform constitution cleanup operation.

        Args:
            dry_run: If True, only analyze without making changes.
            merge_existing: If True, merge with existing tech-stack.md.

        Returns:
            CleanupResult with operation details.
        """
        result = CleanupResult()

        # Check if constitution exists
        if not self.constitution_path.exists():
            result.error_message = f"Constitution not found: {self.constitution_path}"
            return result

        result.constitution_size_before = self.constitution_path.stat().st_size

        # Analyze content
        analysis = self.analyze()

        if not analysis.has_tech_content:
            result.preserved_sections = list(analysis.preserved_sections.keys())
            result.unclear_sections = list(analysis.unclear_sections.keys())
            return result

        result.extracted_sections = list(analysis.tech_sections.keys())
        result.preserved_sections = list(analysis.preserved_sections.keys())
        result.unclear_sections = list(analysis.unclear_sections.keys())

        if dry_run:
            return result

        # Create backup
        backup_path = self.create_backup()
        if backup_path:
            result.backup_path = backup_path
        else:
            result.error_message = "Failed to create backup"
            return result

        # Check for existing tech-stack.md
        existing_tech_stack = None
        if self.tech_stack_path.exists():
            if not merge_existing:
                result.error_message = (
                    f"tech-stack.md already exists at {self.tech_stack_path}. "
                    "Use --merge to combine content."
                )
                return result
            existing_tech_stack = self.tech_stack_path.read_text()
            result.tech_stack_merged = True

        # Extract project name from header
        project_name = self._extract_project_name(analysis.header_content)

        # Build new tech-stack content
        tech_stack_content = self._build_tech_stack(
            project_name,
            analysis.tech_sections,
            existing_tech_stack,
        )

        # Build new constitution content
        constitution_content = self._build_constitution(
            analysis.header_content,
            analysis.preserved_sections,
        )

        # Write files
        try:
            self.tech_stack_path.write_text(tech_stack_content)
            result.tech_stack_created = True
            logger.info(f"Created tech-stack.md: {self.tech_stack_path}")

            self.constitution_path.write_text(constitution_content)
            result.constitution_size_after = self.constitution_path.stat().st_size
            logger.info(f"Updated constitution.md: {self.constitution_path}")

        except OSError as e:
            result.error_message = f"Failed to write files: {e}"
            return result

        return result

    def _extract_project_name(self, header: str) -> str:
        """Extract project name from constitution header.

        Args:
            header: Header content from constitution.

        Returns:
            Project name or default placeholder.
        """
        # Try to find "# ProjectName Constitution" pattern
        match = re.search(r"^#\s+(.+?)\s+Constitution", header, re.MULTILINE)
        if match:
            return match.group(1)

        # Try to find any H1 header
        match = re.search(r"^#\s+(.+)$", header, re.MULTILINE)
        if match:
            name = match.group(1).replace("Constitution", "").strip()
            if name:
                return name

        return "[PROJECT_NAME]"

    def _build_tech_stack(
        self,
        project_name: str,
        tech_sections: dict[str, str],
        existing_content: Optional[str] = None,
    ) -> str:
        """Build tech-stack.md content.

        Args:
            project_name: Name of the project.
            tech_sections: Dict of section name to content.
            existing_content: Existing tech-stack content to merge.

        Returns:
            Complete tech-stack.md content.
        """
        lines = [
            f"# {project_name} Tech Stack",
            TECH_STACK_CROSS_REF,
        ]

        # Add extracted sections
        for _section_name, content in tech_sections.items():
            lines.append(content)
            lines.append("")

        # If merging, add existing content that isn't duplicate
        if existing_content:
            # Skip header and cross-reference from existing
            existing_lines = existing_content.split("\n")
            skip_until_section = True
            for line in existing_lines:
                if skip_until_section:
                    if line.startswith("## "):
                        skip_until_section = False
                        lines.append(line)
                else:
                    lines.append(line)

        return "\n".join(lines)

    def _build_constitution(
        self,
        header: str,
        preserved_sections: dict[str, str],
    ) -> str:
        """Build updated constitution.md content.

        Args:
            header: Original header content.
            preserved_sections: Dict of section name to content.

        Returns:
            Complete constitution.md content.
        """
        lines = []

        # Add header with cross-reference
        if header:
            # Insert cross-reference after first H1
            header_lines = header.split("\n")
            for i, line in enumerate(header_lines):
                lines.append(line)
                if line.startswith("# ") and not line.startswith("## "):
                    lines.append(CONSTITUTION_CROSS_REF)
        else:
            lines.append("# Constitution")
            lines.append(CONSTITUTION_CROSS_REF)

        lines.append("")

        # Add preserved sections
        for _section_name, content in preserved_sections.items():
            lines.append(content)
            lines.append("")

        return "\n".join(lines)
