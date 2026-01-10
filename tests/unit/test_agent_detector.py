"""Unit tests for AgentDetector service."""

import pytest
from pathlib import Path

from doit_cli.models.agent import Agent
from doit_cli.models.project import Project
from doit_cli.services.agent_detector import AgentDetector


class TestAgentDetector:
    """Tests for AgentDetector service."""

    def test_detect_no_agents(self, project_dir):
        """Test detection when no agents are present."""
        project = Project(path=project_dir)
        detector = AgentDetector(project)

        agents = detector.detect_agents()

        assert agents == []

    def test_detect_claude_agent(self, project_dir):
        """Test detection of Claude agent from .claude directory."""
        # Create .claude directory
        (project_dir / ".claude").mkdir()

        project = Project(path=project_dir)
        detector = AgentDetector(project)

        agents = detector.detect_agents()

        assert Agent.CLAUDE in agents

    def test_detect_copilot_agent_from_instructions(self, project_dir):
        """Test detection of Copilot agent from copilot-instructions.md."""
        # Create .github/copilot-instructions.md
        github_dir = project_dir / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text("# Instructions\n")

        project = Project(path=project_dir)
        detector = AgentDetector(project)

        agents = detector.detect_agents()

        assert Agent.COPILOT in agents

    def test_detect_copilot_agent_from_prompts(self, project_dir):
        """Test detection of Copilot agent from .github/prompts directory."""
        # Create .github/prompts directory
        prompts_dir = project_dir / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)

        project = Project(path=project_dir)
        detector = AgentDetector(project)

        agents = detector.detect_agents()

        assert Agent.COPILOT in agents

    def test_detect_both_agents(self, project_dir):
        """Test detection of both Claude and Copilot agents."""
        # Create both agent indicators
        (project_dir / ".claude").mkdir()
        github_dir = project_dir / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text("# Instructions\n")

        project = Project(path=project_dir)
        detector = AgentDetector(project)

        agents = detector.detect_agents()

        assert Agent.CLAUDE in agents
        assert Agent.COPILOT in agents
        assert len(agents) == 2

    def test_has_claude(self, project_dir):
        """Test has_claude method."""
        project = Project(path=project_dir)
        detector = AgentDetector(project)

        assert not detector.has_claude()

        (project_dir / ".claude").mkdir()
        assert detector.has_claude()

    def test_has_copilot(self, project_dir):
        """Test has_copilot method."""
        project = Project(path=project_dir)
        detector = AgentDetector(project)

        assert not detector.has_copilot()

        github_dir = project_dir / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text("# Instructions\n")
        assert detector.has_copilot()
