"""Parser for AUTO-GENERATED sections in markdown files."""

import re
from typing import Optional

from ..models.diagram_models import DiagramSection


class SectionParser:
    """Parses AUTO-GENERATED sections from markdown files.

    Finds and extracts content between BEGIN and END markers:
    <!-- BEGIN:AUTO-GENERATED section="name" -->
    [content]
    <!-- END:AUTO-GENERATED -->
    """

    # Regex pattern for BEGIN marker with section name
    BEGIN_PATTERN = re.compile(
        r'<!--\s*BEGIN:AUTO-GENERATED\s+section="([^"]+)"\s*-->', re.IGNORECASE
    )

    # Regex pattern for END marker
    END_PATTERN = re.compile(r"<!--\s*END:AUTO-GENERATED\s*-->", re.IGNORECASE)

    def find_sections(self, content: str) -> list[DiagramSection]:
        """Find all AUTO-GENERATED sections in content.

        Args:
            content: File content to parse

        Returns:
            List of DiagramSection objects with section details
        """
        sections = []
        lines = content.split("\n")

        current_section: Optional[DiagramSection] = None
        section_content_lines: list[str] = []

        for line_num, line in enumerate(lines, start=1):
            # Check for BEGIN marker
            begin_match = self.BEGIN_PATTERN.search(line)
            if begin_match:
                # Start new section
                section_name = begin_match.group(1)
                current_section = DiagramSection(
                    section_name=section_name,
                    start_line=line_num,
                    end_line=0,  # Will be set when END found
                    content="",
                )
                section_content_lines = []
                continue

            # Check for END marker
            if current_section is not None and self.END_PATTERN.search(line):
                # Complete current section
                current_section.end_line = line_num
                current_section.content = "\n".join(section_content_lines)
                sections.append(current_section)
                current_section = None
                section_content_lines = []
                continue

            # Accumulate content within section
            if current_section is not None:
                section_content_lines.append(line)

        return sections

    def find_section(self, content: str, section_name: str) -> Optional[DiagramSection]:
        """Find a specific AUTO-GENERATED section by name.

        Args:
            content: File content to parse
            section_name: Name of section to find (e.g., "user-journey")

        Returns:
            DiagramSection if found, None otherwise
        """
        sections = self.find_sections(content)
        for section in sections:
            if section.section_name == section_name:
                return section
        return None

    def replace_section_content(
        self, content: str, section_name: str, new_content: str
    ) -> tuple[str, bool]:
        """Replace content within an AUTO-GENERATED section.

        Args:
            content: Original file content
            section_name: Name of section to update
            new_content: New content to insert (without markers)

        Returns:
            Tuple of (updated content, success boolean)
        """
        section = self.find_section(content, section_name)
        if section is None:
            return content, False

        lines = content.split("\n")

        # Build new content: before + marker + new + marker + after
        before_lines = lines[: section.start_line]  # Includes BEGIN marker line
        after_lines = lines[section.end_line - 1 :]  # Starts from END marker line

        # Ensure new content has proper newlines
        new_content_clean = new_content.strip()

        # Reconstruct
        result_lines = before_lines + [new_content_clean] + after_lines

        return "\n".join(result_lines), True

    def insert_section_markers(
        self,
        content: str,
        section_name: str,
        after_heading: str,
        initial_content: str = "",
    ) -> tuple[str, bool]:
        """Insert new AUTO-GENERATED section markers after a heading.

        Args:
            content: Original file content
            section_name: Name for the new section
            after_heading: Heading text to insert after (e.g., "## User Journey")
            initial_content: Initial content to place between markers

        Returns:
            Tuple of (updated content, success boolean)
        """
        # Check if section already exists
        if self.find_section(content, section_name) is not None:
            return content, False  # Section already exists

        lines = content.split("\n")
        heading_pattern = re.compile(
            rf"^#+\s*{re.escape(after_heading)}\s*$", re.IGNORECASE
        )

        insert_index = -1
        for i, line in enumerate(lines):
            if heading_pattern.match(line.strip()):
                insert_index = i + 1
                break

        if insert_index == -1:
            return content, False  # Heading not found

        # Build marker block
        begin_marker = f'<!-- BEGIN:AUTO-GENERATED section="{section_name}" -->'
        end_marker = "<!-- END:AUTO-GENERATED -->"

        marker_block = [
            "",
            begin_marker,
            initial_content if initial_content else "",
            end_marker,
            "",
        ]

        # Insert after heading
        result_lines = lines[:insert_index] + marker_block + lines[insert_index:]

        return "\n".join(result_lines), True

    def extract_mermaid_from_section(self, section: DiagramSection) -> Optional[str]:
        """Extract Mermaid diagram content from a section.

        Args:
            section: DiagramSection to extract from

        Returns:
            Mermaid content without code fences, or None if not found
        """
        content = section.content

        # Look for ```mermaid ... ``` block
        mermaid_pattern = re.compile(
            r"```mermaid\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE
        )
        match = mermaid_pattern.search(content)

        if match:
            return match.group(1).strip()

        return None

    def has_section(self, content: str, section_name: str) -> bool:
        """Check if a section exists in content.

        Args:
            content: File content to check
            section_name: Name of section to look for

        Returns:
            True if section exists, False otherwise
        """
        return self.find_section(content, section_name) is not None
