"""Parser for user stories from spec.md files."""

import re
from typing import Optional

from ..models.diagram_models import AcceptanceScenario, ParsedUserStory


class UserStoryParser:
    """Parses user stories from spec.md content.

    Extracts user story headers, descriptions, and acceptance scenarios
    following the doit spec template format.
    """

    # Pattern for user story header: ### User Story N - Title (Priority: PN)
    STORY_HEADER_PATTERN = re.compile(
        r"^###\s+User\s+Story\s+(\d+)\s*[-–—]\s*(.+?)\s*\(Priority:\s*(P\d+)\)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    # Pattern for Given/When/Then acceptance scenarios
    # Supports both bold and plain text formats
    SCENARIO_PATTERN = re.compile(
        r"^\d+\.\s+\*?\*?(?:Given)\*?\*?\s+(.+?),\s*\*?\*?(?:When)\*?\*?\s+(.+?),\s*\*?\*?(?:Then)\*?\*?\s+(.+)$",
        re.IGNORECASE | re.MULTILINE,
    )

    # Alternative pattern for bold keywords
    SCENARIO_BOLD_PATTERN = re.compile(
        r"^\d+\.\s+\*\*Given\*\*\s+(.+?),\s*\*\*When\*\*\s+(.+?),\s*\*\*Then\*\*\s+(.+)$",
        re.IGNORECASE | re.MULTILINE,
    )

    def parse(self, content: str) -> list[ParsedUserStory]:
        """Parse all user stories from spec content.

        Args:
            content: Full content of spec.md file

        Returns:
            List of ParsedUserStory objects
        """
        stories = []

        # Find all story headers and their positions
        header_matches = list(self.STORY_HEADER_PATTERN.finditer(content))

        if not header_matches:
            return stories

        # Extract each story's content
        for i, match in enumerate(header_matches):
            story_number = int(match.group(1))
            title = match.group(2).strip()
            priority = match.group(3).strip().upper()

            # Determine story content boundaries
            start_pos = match.end()
            if i + 1 < len(header_matches):
                end_pos = header_matches[i + 1].start()
            else:
                # Last story - find next major section or end of file
                next_section = self._find_next_section(content, start_pos)
                end_pos = next_section if next_section else len(content)

            story_content = content[start_pos:end_pos].strip()

            # Extract description and scenarios
            description = self._extract_description(story_content)
            scenarios = self._extract_scenarios(story_content, story_number)

            story = ParsedUserStory(
                id=f"US{story_number}",
                story_number=story_number,
                title=title,
                priority=priority,
                description=description,
                scenarios=scenarios,
                raw_text=content[match.start() : end_pos],
            )
            stories.append(story)

        return stories

    def parse_single(self, content: str) -> Optional[ParsedUserStory]:
        """Parse a single user story from content.

        Args:
            content: Content containing one user story

        Returns:
            ParsedUserStory if found, None otherwise
        """
        stories = self.parse(content)
        return stories[0] if stories else None

    def _extract_description(self, story_content: str) -> str:
        """Extract user story description from content.

        The description is typically the narrative before acceptance scenarios.

        Args:
            story_content: Content of a single user story section

        Returns:
            Description text
        """
        lines = story_content.split("\n")
        description_lines = []

        for line in lines:
            stripped = line.strip()

            # Stop at acceptance scenarios or numbered lists
            if stripped.startswith("1.") or "**Given**" in stripped:
                break

            # Skip empty lines at the start
            if not stripped and not description_lines:
                continue

            # Stop at sub-headers
            if stripped.startswith("##"):
                break

            description_lines.append(stripped)

        return " ".join(description_lines).strip()

    def _extract_scenarios(
        self, story_content: str, story_number: int
    ) -> list[AcceptanceScenario]:
        """Extract acceptance scenarios from story content.

        Args:
            story_content: Content of a single user story section
            story_number: The story number for generating IDs

        Returns:
            List of AcceptanceScenario objects
        """
        scenarios = []

        # Try bold pattern first (more specific)
        matches = list(self.SCENARIO_BOLD_PATTERN.finditer(story_content))

        # Fall back to general pattern
        if not matches:
            matches = list(self.SCENARIO_PATTERN.finditer(story_content))

        for scenario_num, match in enumerate(matches, start=1):
            given = self._clean_clause(match.group(1))
            when = self._clean_clause(match.group(2))
            then = self._clean_clause(match.group(3))

            scenario = AcceptanceScenario(
                id=f"US{story_number}_S{scenario_num}",
                scenario_number=scenario_num,
                given_clause=given,
                when_clause=when,
                then_clause=then,
                raw_text=match.group(0),
            )
            scenarios.append(scenario)

        return scenarios

    def _clean_clause(self, text: str) -> str:
        """Clean a Given/When/Then clause.

        Args:
            text: Raw clause text

        Returns:
            Cleaned text with markdown removed
        """
        # Remove bold markers
        text = text.replace("**", "")
        # Remove trailing punctuation
        text = text.rstrip(".,;")
        # Clean whitespace
        text = " ".join(text.split())
        return text.strip()

    def _find_next_section(self, content: str, start_pos: int) -> Optional[int]:
        """Find the position of the next major section.

        Args:
            content: Full file content
            start_pos: Position to start searching from

        Returns:
            Position of next section header, or None if not found
        """
        # Look for ## or ### headers that aren't user stories
        section_pattern = re.compile(r"^##\s+[^#]", re.MULTILINE)
        match = section_pattern.search(content, start_pos)

        if match:
            return match.start()

        return None

    def get_story_by_number(
        self, content: str, story_number: int
    ) -> Optional[ParsedUserStory]:
        """Get a specific user story by number.

        Args:
            content: Spec content to parse
            story_number: Story number to find (1, 2, 3...)

        Returns:
            ParsedUserStory if found, None otherwise
        """
        stories = self.parse(content)
        for story in stories:
            if story.story_number == story_number:
                return story
        return None

    def count_stories(self, content: str) -> int:
        """Count user stories in content without full parsing.

        Args:
            content: Spec content to check

        Returns:
            Number of user stories found
        """
        return len(self.STORY_HEADER_PATTERN.findall(content))
