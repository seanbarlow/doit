"""Service to transform command templates to GitHub Copilot prompt format."""

import re

from ..models.sync_models import CommandTemplate


class PromptTransformer:
    """Transforms doit command templates to GitHub Copilot prompt format."""

    def transform(self, template: CommandTemplate) -> str:
        """Transform a command template to Copilot prompt format.

        Transformation rules (from research.md):
        - Remove YAML frontmatter entirely (Copilot prompts are plain markdown)
        - Replace $ARGUMENTS with natural language
        - Preserve ## Outline, ## Key Rules, and other sections

        Args:
            template: The command template to transform.

        Returns:
            Transformed content suitable for Copilot prompt file.
        """
        content = template.content

        # Step 1: Strip YAML frontmatter
        content = self._strip_yaml_frontmatter(content)

        # Step 2: Add description as header if available
        if template.description:
            header = f"# {self._title_from_name(template.name)}\n\n{template.description}\n\n"
            content = header + content.lstrip()

        # Step 3: Replace $ARGUMENTS placeholder with natural language
        content = self._replace_arguments_placeholder(content)

        return content.strip() + "\n"

    def _strip_yaml_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content.

        Args:
            content: Markdown content potentially with YAML frontmatter.

        Returns:
            Content with frontmatter removed.
        """
        if not content.startswith("---"):
            return content

        # Find the closing ---
        try:
            end_idx = content.index("---", 3)
            # Skip the closing --- and any trailing newline
            return content[end_idx + 3:].lstrip("\n")
        except ValueError:
            # No closing ---, return original
            return content

    def _replace_arguments_placeholder(self, content: str) -> str:
        """Replace $ARGUMENTS placeholder with natural language.

        Args:
            content: Content potentially containing $ARGUMENTS.

        Returns:
            Content with placeholder replaced.
        """
        # Replace the code block containing $ARGUMENTS
        pattern = r"```text\s*\n\$ARGUMENTS\s*\n```"
        replacement = "Consider any arguments or options the user provides."
        content = re.sub(pattern, replacement, content)

        # Also replace standalone $ARGUMENTS references
        content = content.replace("$ARGUMENTS", "the user's input")

        return content

    def _title_from_name(self, name: str) -> str:
        """Convert command name to title case.

        Args:
            name: Command name like "doit.checkin".

        Returns:
            Title like "Doit Checkin".
        """
        # doit.checkin -> Doit Checkin
        parts = name.replace("doit.", "").split(".")
        return "Doit " + " ".join(p.title() for p in parts)
