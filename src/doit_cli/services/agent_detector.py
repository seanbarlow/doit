"""Agent detector service for detecting existing AI agent configuration."""

from pathlib import Path
from typing import Optional

from ..models.agent import Agent
from ..models.project import Project


class AgentDetector:
    """Service for detecting which AI agents are configured in a project."""

    def __init__(self, project: Project):
        """Initialize agent detector.

        Args:
            project: Project to detect agents for
        """
        self.project = project

    def detect_agents(self) -> list[Agent]:
        """Detect which agents are already configured in the project.

        Detection order:
        1. Check for existing .claude/ directory -> Claude
        2. Check for existing .github/copilot-instructions.md -> Copilot
        3. Check for existing .github/prompts/ directory -> Copilot

        Returns:
            List of detected agents
        """
        detected = []

        if self._has_claude_setup():
            detected.append(Agent.CLAUDE)

        if self._has_copilot_setup():
            detected.append(Agent.COPILOT)

        return detected

    def _has_claude_setup(self) -> bool:
        """Check if project has Claude setup.

        Returns:
            True if .claude/ or .claude/commands/ exists
        """
        claude_dir = self.project.path / ".claude"
        claude_commands = claude_dir / "commands"

        return claude_dir.exists() or claude_commands.exists()

    def _has_copilot_setup(self) -> bool:
        """Check if project has Copilot setup.

        Returns:
            True if .github/copilot-instructions.md or .github/prompts/ exists
        """
        copilot_instructions = self.project.path / ".github" / "copilot-instructions.md"
        copilot_prompts = self.project.path / ".github" / "prompts"

        return copilot_instructions.exists() or copilot_prompts.exists()

    def has_claude(self) -> bool:
        """Check if project has Claude agent configured.

        Returns:
            True if Claude is configured
        """
        return self._has_claude_setup()

    def has_copilot(self) -> bool:
        """Check if project has Copilot agent configured.

        Returns:
            True if Copilot is configured
        """
        return self._has_copilot_setup()

    def detect_primary_agent(self) -> Optional[Agent]:
        """Detect the primary (most likely) agent for this project.

        Returns:
            Primary agent or None if none detected
        """
        agents = self.detect_agents()

        if not agents:
            return None

        # Prefer Claude if both are detected
        if Agent.CLAUDE in agents:
            return Agent.CLAUDE

        return agents[0]

    def get_agent_status(self) -> dict:
        """Get detailed status for each agent.

        Returns:
            Dict with agent status information
        """
        return {
            "claude": {
                "detected": self._has_claude_setup(),
                "directory": str(self.project.path / ".claude"),
                "commands_dir": str(self.project.command_directory(Agent.CLAUDE)),
                "has_commands": self._has_doit_commands(Agent.CLAUDE),
            },
            "copilot": {
                "detected": self._has_copilot_setup(),
                "instructions": str(self.project.path / ".github" / "copilot-instructions.md"),
                "prompts_dir": str(self.project.command_directory(Agent.COPILOT)),
                "has_prompts": self._has_doit_commands(Agent.COPILOT),
            },
        }

    def _has_doit_commands(self, agent: Agent) -> bool:
        """Check if project has any doit commands for an agent.

        Args:
            agent: Agent to check

        Returns:
            True if any doit-prefixed command files exist
        """
        cmd_dir = self.project.command_directory(agent)

        if not cmd_dir.exists():
            return False

        # Check for any doit-prefixed files
        for file in cmd_dir.iterdir():
            if file.is_file():
                if agent == Agent.CLAUDE:
                    if file.name.startswith("doit.") and file.name.endswith(".md"):
                        return True
                else:  # COPILOT
                    if file.name.startswith("doit.") and file.name.endswith(".prompt.md"):
                        return True

        return False

    def count_doit_commands(self, agent: Agent) -> int:
        """Count doit command files for an agent.

        Args:
            agent: Agent to count commands for

        Returns:
            Number of doit command files
        """
        cmd_dir = self.project.command_directory(agent)

        if not cmd_dir.exists():
            return 0

        count = 0
        for file in cmd_dir.iterdir():
            if file.is_file():
                if agent == Agent.CLAUDE:
                    if file.name.startswith("doit.") and file.name.endswith(".md"):
                        count += 1
                else:  # COPILOT
                    if file.name.startswith("doit.") and file.name.endswith(".prompt.md"):
                        count += 1

        return count
