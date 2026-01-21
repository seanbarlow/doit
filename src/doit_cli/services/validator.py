"""Validator service for checking project setup."""

from pathlib import Path
from typing import Optional

from ..models.agent import Agent
from ..models.project import Project
from ..models.results import VerifyResult, VerifyCheck, VerifyStatus
from ..models.template import DOIT_COMMANDS


class Validator:
    """Service for validating doit project setup."""

    def __init__(self, project: Project):
        """Initialize validator.

        Args:
            project: Project to validate
        """
        self.project = project
        self.checks: list[VerifyCheck] = []

    def check_doit_folder(self) -> VerifyCheck:
        """Check if .doit/ folder exists and has required subdirectories."""
        if not self.project.doit_folder.exists():
            return VerifyCheck(
                name="doit_folder",
                status=VerifyStatus.FAIL,
                message=".doit/ folder does not exist",
                suggestion="Run 'doit init' to create the project structure",
            )

        # Check subdirectories
        missing_subdirs = []
        for subdir in ["memory", "templates", "scripts"]:
            if not (self.project.doit_folder / subdir).exists():
                missing_subdirs.append(subdir)

        if missing_subdirs:
            return VerifyCheck(
                name="doit_folder",
                status=VerifyStatus.WARN,
                message=f".doit/ exists but missing subdirectories: {', '.join(missing_subdirs)}",
                suggestion="Run 'doit init --update' to restore missing directories",
            )

        return VerifyCheck(
            name="doit_folder",
            status=VerifyStatus.PASS,
            message=".doit/ folder structure is complete",
        )

    def check_agent_directory(self, agent: Agent) -> VerifyCheck:
        """Check if agent command directory exists.

        Args:
            agent: Agent to check
        """
        cmd_dir = self.project.command_directory(agent)

        if not cmd_dir.exists():
            return VerifyCheck(
                name=f"{agent.value}_directory",
                status=VerifyStatus.FAIL,
                message=f"{agent.display_name} command directory does not exist",
                suggestion=f"Run 'doit init --agent {agent.value}' to create it",
            )

        return VerifyCheck(
            name=f"{agent.value}_directory",
            status=VerifyStatus.PASS,
            message=f"{agent.display_name} command directory exists at {agent.command_directory}",
        )

    def check_command_files(self, agent: Agent) -> VerifyCheck:
        """Check if all required command files exist for an agent.

        Args:
            agent: Agent to check
        """
        cmd_dir = self.project.command_directory(agent)

        if not cmd_dir.exists():
            return VerifyCheck(
                name=f"{agent.value}_commands",
                status=VerifyStatus.FAIL,
                message=f"Cannot check commands - directory does not exist",
            )

        # Get expected file names
        if agent == Agent.CLAUDE:
            expected_files = {f"doit.{cmd}.md" for cmd in DOIT_COMMANDS}
        else:  # COPILOT
            expected_files = {f"doit.{cmd}.prompt.md" for cmd in DOIT_COMMANDS}

        # Get actual files
        actual_files = {f.name for f in cmd_dir.iterdir() if f.is_file()}

        # Check for missing
        missing = expected_files - actual_files

        if missing:
            return VerifyCheck(
                name=f"{agent.value}_commands",
                status=VerifyStatus.WARN,
                message=f"Missing {len(missing)} command files: {', '.join(sorted(missing)[:3])}{'...' if len(missing) > 3 else ''}",
                suggestion="Run 'doit init --update' to restore missing templates",
            )

        return VerifyCheck(
            name=f"{agent.value}_commands",
            status=VerifyStatus.PASS,
            message=f"All {len(DOIT_COMMANDS)} command files present",
        )

    def check_constitution(self) -> VerifyCheck:
        """Check if constitution.md exists in memory folder."""
        constitution_path = self.project.memory_folder / "constitution.md"

        if not constitution_path.exists():
            return VerifyCheck(
                name="constitution",
                status=VerifyStatus.WARN,
                message="Project constitution not found",
                suggestion="Run '/doit.constitution' to create project principles",
            )

        return VerifyCheck(
            name="constitution",
            status=VerifyStatus.PASS,
            message="Project constitution exists",
        )

    def check_roadmap(self) -> VerifyCheck:
        """Check if roadmap.md exists in memory folder."""
        roadmap_path = self.project.memory_folder / "roadmap.md"

        if not roadmap_path.exists():
            return VerifyCheck(
                name="roadmap",
                status=VerifyStatus.WARN,
                message="Project roadmap not found",
                suggestion="Run '/doit.roadmapit' to create a feature roadmap",
            )

        return VerifyCheck(
            name="roadmap",
            status=VerifyStatus.PASS,
            message="Project roadmap exists",
        )

    def check_copilot_instructions(self) -> VerifyCheck:
        """Check if copilot-instructions.md exists for Copilot projects."""
        instructions_path = self.project.path / ".github" / "copilot-instructions.md"
        prompts_dir = self.project.path / ".github" / "prompts"

        # Only check if Copilot appears to be configured
        if not prompts_dir.exists():
            return VerifyCheck(
                name="copilot_instructions",
                status=VerifyStatus.PASS,
                message="Copilot not configured (skipped)",
            )

        if not instructions_path.exists():
            return VerifyCheck(
                name="copilot_instructions",
                status=VerifyStatus.WARN,
                message="copilot-instructions.md not found",
                suggestion="Run 'doit init --agent copilot' to create it",
            )

        # Check if it has doit section
        content = instructions_path.read_text(encoding="utf-8")
        if "DOIT INSTRUCTIONS" not in content:
            return VerifyCheck(
                name="copilot_instructions",
                status=VerifyStatus.WARN,
                message="copilot-instructions.md missing doit section",
                suggestion="Run 'doit init --agent copilot --update' to add doit instructions",
            )

        return VerifyCheck(
            name="copilot_instructions",
            status=VerifyStatus.PASS,
            message="copilot-instructions.md configured correctly",
        )

    def run_all_checks(self, agents: Optional[list[Agent]] = None) -> VerifyResult:
        """Run all validation checks.

        Args:
            agents: List of agents to check (None = auto-detect)

        Returns:
            VerifyResult with all check results
        """
        self.checks = []

        # Core structure check
        self.checks.append(self.check_doit_folder())

        # Auto-detect agents if not specified
        if agents is None:
            agents = []
            if (self.project.path / ".claude").exists():
                agents.append(Agent.CLAUDE)
            if (self.project.path / ".github" / "prompts").exists():
                agents.append(Agent.COPILOT)

            # Default to Claude if nothing detected
            if not agents:
                agents = [Agent.CLAUDE]

        # Agent-specific checks
        for agent in agents:
            self.checks.append(self.check_agent_directory(agent))
            self.checks.append(self.check_command_files(agent))

        # Memory content checks
        self.checks.append(self.check_constitution())
        self.checks.append(self.check_roadmap())

        # Copilot-specific check
        if Agent.COPILOT in agents:
            self.checks.append(self.check_copilot_instructions())

        return VerifyResult(
            project=self.project,
            checks=self.checks,
        )
