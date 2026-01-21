"""Scaffolder service for creating doit project structure."""

from pathlib import Path
from typing import Optional

from ..models.agent import Agent
from ..models.project import Project
from ..models.results import InitResult


class Scaffolder:
    """Service for creating doit project directory structure."""

    # Subdirectories to create under .doit/
    DOIT_SUBDIRS = ["memory", "templates", "scripts", "config", "logs"]

    def __init__(self, project: Project):
        self.project = project
        self.created_directories: list[Path] = []
        self.created_files: list[Path] = []

    def create_doit_structure(self) -> InitResult:
        """Create the .doit/ directory structure.

        Creates:
        - .doit/
        - .doit/memory/
        - .doit/templates/
        - .doit/scripts/
        """
        try:
            # Create main .doit directory
            if not self.project.doit_folder.exists():
                self.project.doit_folder.mkdir(parents=True, exist_ok=True)
                self.created_directories.append(self.project.doit_folder)

            # Create subdirectories
            for subdir in self.DOIT_SUBDIRS:
                subdir_path = self.project.doit_folder / subdir
                if not subdir_path.exists():
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    self.created_directories.append(subdir_path)

            return InitResult(
                success=True,
                project=self.project,
                created_directories=self.created_directories.copy(),
                created_files=self.created_files.copy(),
            )

        except PermissionError as e:
            return InitResult(
                success=False,
                project=self.project,
                error_message=f"Permission denied: {e}",
            )
        except OSError as e:
            return InitResult(
                success=False,
                project=self.project,
                error_message=f"Failed to create directory: {e}",
            )

    def create_agent_directory(self, agent: Agent) -> bool:
        """Create the command directory for a specific agent.

        Args:
            agent: The agent to create directory for

        Returns:
            True if directory was created, False if it already existed
        """
        cmd_dir = self.project.command_directory(agent)

        if agent == Agent.COPILOT:
            # For Copilot, also ensure .github/ exists
            github_dir = self.project.path / ".github"
            if not github_dir.exists():
                github_dir.mkdir(parents=True, exist_ok=True)
                self.created_directories.append(github_dir)

        if not cmd_dir.exists():
            cmd_dir.mkdir(parents=True, exist_ok=True)
            self.created_directories.append(cmd_dir)
            return True

        return False

    def create_backup_directory(self, timestamp: str) -> Path:
        """Create a timestamped backup directory.

        Args:
            timestamp: Timestamp string for the backup folder name

        Returns:
            Path to the created backup directory
        """
        backup_dir = self.project.backups_folder / timestamp

        if not backup_dir.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
            self.created_directories.append(backup_dir)

        return backup_dir

    def is_doit_file(self, path: Path, agent: Agent) -> bool:
        """Check if a file is a doit-managed file for the given agent.

        Args:
            path: Path to check
            agent: Agent to check against

        Returns:
            True if file is doit-managed (matches doit.* or doit-* pattern)
        """
        filename = path.name
        if agent == Agent.CLAUDE:
            return filename.startswith("doit.") and filename.endswith(".md")
        else:  # COPILOT
            return filename.startswith("doit.") and filename.endswith(".prompt.md")

    def get_doit_files(self, agent: Agent) -> list[Path]:
        """Get all doit-managed files for an agent.

        Args:
            agent: Agent to get files for

        Returns:
            List of paths to doit-managed files
        """
        cmd_dir = self.project.command_directory(agent)
        if not cmd_dir.exists():
            return []

        return [f for f in cmd_dir.iterdir() if f.is_file() and self.is_doit_file(f, agent)]

    def get_custom_files(self, agent: Agent) -> list[Path]:
        """Get all custom (non-doit) files for an agent.

        Args:
            agent: Agent to get files for

        Returns:
            List of paths to custom files
        """
        cmd_dir = self.project.command_directory(agent)
        if not cmd_dir.exists():
            return []

        return [f for f in cmd_dir.iterdir() if f.is_file() and not self.is_doit_file(f, agent)]

    def get_preserved_paths(self) -> list[Path]:
        """Get list of paths that should be preserved during updates.

        These include:
        - .doit/memory/ (user-managed content)
        - Custom (non-doit-prefixed) command files

        Returns:
            List of paths to preserve
        """
        preserved = []

        # Always preserve memory folder contents
        memory_dir = self.project.memory_folder
        if memory_dir.exists():
            preserved.extend(f for f in memory_dir.rglob("*") if f.is_file())

        # Preserve custom command files for each agent
        for agent in [Agent.CLAUDE, Agent.COPILOT]:
            preserved.extend(self.get_custom_files(agent))

        return preserved

    def get_files_to_update(self, agent: Agent) -> list[Path]:
        """Get list of doit-managed files that can be updated.

        These are doit-prefixed files that will be overwritten during update.

        Args:
            agent: Agent to get files for

        Returns:
            List of paths that can be updated
        """
        return self.get_doit_files(agent)

    def should_preserve(self, path: Path) -> bool:
        """Check if a file should be preserved during update.

        Args:
            path: Path to check

        Returns:
            True if file should be preserved
        """
        # Preserve anything in memory folder
        try:
            path.relative_to(self.project.memory_folder)
            return True
        except ValueError:
            pass

        # Preserve custom (non-doit) command files
        for agent in [Agent.CLAUDE, Agent.COPILOT]:
            cmd_dir = self.project.command_directory(agent)
            try:
                path.relative_to(cmd_dir)
                # File is in command directory - check if it's doit-managed
                if not self.is_doit_file(path, agent):
                    return True
            except ValueError:
                continue

        return False
