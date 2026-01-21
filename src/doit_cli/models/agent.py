"""Agent enum and configuration for supported AI coding assistants."""

from enum import Enum


class Agent(str, Enum):
    """Supported AI coding agents."""

    CLAUDE = "claude"
    COPILOT = "copilot"

    @property
    def display_name(self) -> str:
        """Human-readable name for display."""
        names = {
            Agent.CLAUDE: "Claude Code",
            Agent.COPILOT: "GitHub Copilot",
        }
        return names[self]

    @property
    def command_directory(self) -> str:
        """Relative path to command/prompt directory."""
        directories = {
            Agent.CLAUDE: ".claude/commands",
            Agent.COPILOT: ".github/prompts",
        }
        return directories[self]

    @property
    def template_directory(self) -> str:
        """Relative path within bundled templates.

        All agents now use commands/ as the single source of truth.
        Copilot prompts are generated dynamically via transformation.
        """
        return "commands"

    @property
    def needs_transformation(self) -> bool:
        """Whether templates need transformation for this agent.

        Returns:
            True for Copilot (requires transformation from command format),
            False for Claude (direct copy).
        """
        return self == Agent.COPILOT

    @property
    def file_extension(self) -> str:
        """File extension for command files."""
        extensions = {
            Agent.CLAUDE: ".md",
            Agent.COPILOT: ".prompt.md",
        }
        return extensions[self]

    @property
    def file_pattern(self) -> str:
        """Glob pattern for doit-managed files."""
        patterns = {
            Agent.CLAUDE: "doit.*.md",
            Agent.COPILOT: "doit.*.prompt.md",
        }
        return patterns[self]

    @property
    def file_prefix(self) -> str:
        """Filename prefix for doit commands."""
        prefixes = {
            Agent.CLAUDE: "doit.",
            Agent.COPILOT: "doit.",
        }
        return prefixes[self]
