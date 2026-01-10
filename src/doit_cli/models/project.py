"""Project model representing a directory being initialized for doit workflow."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .agent import Agent


# Unsafe paths that require confirmation before initialization
UNSAFE_PATHS = [
    Path.home(),
    Path("/"),
    Path("/usr"),
    Path("/etc"),
    Path("/var"),
    Path("/opt"),
    Path("/bin"),
    Path("/sbin"),
]


@dataclass
class Project:
    """Represents a project being initialized for doit workflow."""

    path: Path
    initialized: bool = False
    doit_version: Optional[str] = None
    created_at: Optional[datetime] = None
    agents: list[Agent] = field(default_factory=list)

    @property
    def doit_folder(self) -> Path:
        """Path to .doit/ directory."""
        return self.path / ".doit"

    @property
    def memory_folder(self) -> Path:
        """Path to .doit/memory/ directory."""
        return self.doit_folder / "memory"

    @property
    def templates_folder(self) -> Path:
        """Path to .doit/templates/ directory."""
        return self.doit_folder / "templates"

    @property
    def scripts_folder(self) -> Path:
        """Path to .doit/scripts/ directory."""
        return self.doit_folder / "scripts"

    @property
    def backups_folder(self) -> Path:
        """Path to .doit/backups/ directory."""
        return self.doit_folder / "backups"

    def command_directory(self, agent: Agent) -> Path:
        """Path to command directory for given agent."""
        return self.path / agent.command_directory

    def is_safe_directory(self) -> bool:
        """Check if project path is safe for initialization."""
        resolved = self.path.resolve()
        return resolved not in UNSAFE_PATHS

    def has_doit_setup(self) -> bool:
        """Check if project has any doit setup."""
        return self.doit_folder.exists()

    def has_agent_setup(self, agent: Agent) -> bool:
        """Check if project has setup for specific agent."""
        return self.command_directory(agent).exists()

    def detect_agents(self) -> list[Agent]:
        """Detect which agents are already configured in this project."""
        detected = []

        # Check for Claude setup
        claude_dir = self.path / ".claude"
        if claude_dir.exists():
            detected.append(Agent.CLAUDE)

        # Check for Copilot setup
        copilot_instructions = self.path / ".github" / "copilot-instructions.md"
        copilot_prompts = self.path / ".github" / "prompts"
        if copilot_instructions.exists() or copilot_prompts.exists():
            detected.append(Agent.COPILOT)

        return detected
