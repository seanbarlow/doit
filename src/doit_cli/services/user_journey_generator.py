"""Generator for User Journey flowchart diagrams from user stories."""

from ..models.diagram_models import GeneratedDiagram, DiagramType, ParsedUserStory


class UserJourneyGenerator:
    """Generates Mermaid flowchart diagrams from user stories.

    Converts ParsedUserStory objects into a flowchart with subgraphs
    per story and nodes for each acceptance scenario.
    """

    def __init__(self, direction: str = "LR"):
        """Initialize generator.

        Args:
            direction: Flowchart direction (LR, TB, RL, BT)
        """
        self.direction = direction

    def generate(self, stories: list[ParsedUserStory]) -> str:
        """Generate Mermaid flowchart from user stories.

        Args:
            stories: List of parsed user stories

        Returns:
            Mermaid flowchart syntax
        """
        if not stories:
            return ""

        lines = [f"flowchart {self.direction}"]

        for story in stories:
            story_lines = self._generate_story_subgraph(story)
            lines.extend(story_lines)

        # Add story connections (story to story flow)
        connection_lines = self._generate_story_connections(stories)
        if connection_lines:
            lines.append("")
            lines.extend(connection_lines)

        return "\n".join(lines)

    def generate_diagram(self, stories: list[ParsedUserStory]) -> GeneratedDiagram:
        """Generate a GeneratedDiagram object from user stories.

        Args:
            stories: List of parsed user stories

        Returns:
            GeneratedDiagram with content and metadata
        """
        content = self.generate(stories)

        # Count nodes
        node_count = sum(
            len(story.scenarios) + 1 for story in stories  # +1 for entry node
        )

        return GeneratedDiagram(
            id="user-journey",
            diagram_type=DiagramType.USER_JOURNEY,
            mermaid_content=content,
            is_valid=True,
            node_count=node_count,
        )

    def _generate_story_subgraph(self, story: ParsedUserStory) -> list[str]:
        """Generate subgraph for a single user story.

        Args:
            story: Parsed user story

        Returns:
            List of Mermaid syntax lines
        """
        lines = []
        lines.append(f'    subgraph {story.subgraph_id}["{story.subgraph_label}"]')

        if not story.scenarios:
            # No scenarios - create a single placeholder node
            node_id = f"{story.subgraph_id}_A"
            lines.append(f'        {node_id}["{self._escape_label(story.title)}"]')
        else:
            # Create nodes for each scenario
            prev_node_id = None
            for i, scenario in enumerate(story.scenarios):
                letter = chr(ord("A") + i)
                node_id = f"{story.subgraph_id}_{letter}"

                # Generate node based on scenario
                given_label = self._truncate_label(scenario.given_clause, 50)
                when_label = self._truncate_label(scenario.when_clause, 50)
                then_label = self._truncate_label(scenario.then_clause, 50)

                # Create nodes for Given, When, Then
                given_node = f"{node_id}_G"
                when_node = f"{node_id}_W"
                then_node = f"{node_id}_T"

                lines.append(f'        {given_node}["{self._escape_label(given_label)}"]')
                lines.append(f'        {when_node}{{"{self._escape_label(when_label)}"}}')
                lines.append(f'        {then_node}["{self._escape_label(then_label)}"]')

                # Connect Given -> When -> Then
                lines.append(f"        {given_node} --> {when_node}")
                lines.append(f"        {when_node} --> {then_node}")

                # Connect to previous scenario
                if prev_node_id:
                    lines.append(f"        {prev_node_id} -.-> {given_node}")

                prev_node_id = then_node

        lines.append("    end")
        return lines

    def _generate_story_connections(self, stories: list[ParsedUserStory]) -> list[str]:
        """Generate connections between story subgraphs.

        Args:
            stories: List of parsed user stories

        Returns:
            List of connection lines
        """
        if len(stories) <= 1:
            return []

        lines = []
        lines.append("    %% Story flow connections")

        for i in range(len(stories) - 1):
            current_story = stories[i]
            next_story = stories[i + 1]

            # Connect last node of current story to first node of next
            if current_story.scenarios:
                last_letter = chr(ord("A") + len(current_story.scenarios) - 1)
                current_end = f"{current_story.subgraph_id}_{last_letter}_T"
            else:
                current_end = f"{current_story.subgraph_id}_A"

            if next_story.scenarios:
                next_start = f"{next_story.subgraph_id}_A_G"
            else:
                next_start = f"{next_story.subgraph_id}_A"

            # Use dotted line for cross-story connections
            lines.append(f"    {current_end} ==> {next_start}")

        return lines

    def _truncate_label(self, text: str, max_length: int = 40) -> str:
        """Truncate label to maximum length.

        Args:
            text: Original label text
            max_length: Maximum characters

        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def _escape_label(self, text: str) -> str:
        """Escape special characters for Mermaid labels.

        Args:
            text: Original label text

        Returns:
            Escaped text safe for Mermaid
        """
        # Escape quotes
        text = text.replace('"', "'")
        # Escape brackets that could be misinterpreted
        text = text.replace("[", "(")
        text = text.replace("]", ")")
        # Remove newlines
        text = text.replace("\n", " ")
        # Clean up whitespace
        text = " ".join(text.split())
        return text

    def generate_simple(self, stories: list[ParsedUserStory]) -> str:
        """Generate a simplified flowchart with one node per story.

        Args:
            stories: List of parsed user stories

        Returns:
            Simplified Mermaid flowchart syntax
        """
        if not stories:
            return ""

        lines = [f"flowchart {self.direction}"]

        for i, story in enumerate(stories):
            node_id = story.subgraph_id
            label = f"{story.id}: {self._truncate_label(story.title, 30)}"
            lines.append(f'    {node_id}["{self._escape_label(label)}"]')

            if i > 0:
                prev_id = stories[i - 1].subgraph_id
                lines.append(f"    {prev_id} --> {node_id}")

        return "\n".join(lines)
