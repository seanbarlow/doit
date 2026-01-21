"""Unit tests for Agent model."""

import pytest

from doit_cli.models.agent import Agent


class TestAgentProperties:
    """Tests for Agent enum properties."""

    def test_claude_display_name(self):
        """Test Claude display name."""
        assert Agent.CLAUDE.display_name == "Claude Code"

    def test_copilot_display_name(self):
        """Test Copilot display name."""
        assert Agent.COPILOT.display_name == "GitHub Copilot"

    def test_claude_command_directory(self):
        """Test Claude command directory."""
        assert Agent.CLAUDE.command_directory == ".claude/commands"

    def test_copilot_command_directory(self):
        """Test Copilot command directory."""
        assert Agent.COPILOT.command_directory == ".github/prompts"

    def test_claude_file_extension(self):
        """Test Claude file extension."""
        assert Agent.CLAUDE.file_extension == ".md"

    def test_copilot_file_extension(self):
        """Test Copilot file extension."""
        assert Agent.COPILOT.file_extension == ".prompt.md"

    def test_claude_file_pattern(self):
        """Test Claude file pattern."""
        assert Agent.CLAUDE.file_pattern == "doit.*.md"

    def test_copilot_file_pattern(self):
        """Test Copilot file pattern."""
        assert Agent.COPILOT.file_pattern == "doit.*.prompt.md"

    def test_claude_file_prefix(self):
        """Test Claude file prefix."""
        assert Agent.CLAUDE.file_prefix == "doit."

    def test_copilot_file_prefix(self):
        """Test Copilot file prefix."""
        assert Agent.COPILOT.file_prefix == "doit."


class TestTemplateDirectory:
    """Tests for template_directory property (unified templates)."""

    def test_claude_template_directory_returns_commands(self):
        """Test Claude template_directory returns 'commands'."""
        assert Agent.CLAUDE.template_directory == "commands"

    def test_copilot_template_directory_returns_commands(self):
        """Test Copilot template_directory also returns 'commands' (single source)."""
        assert Agent.COPILOT.template_directory == "commands"

    def test_both_agents_share_same_template_source(self):
        """Test both agents use the same template source directory."""
        assert Agent.CLAUDE.template_directory == Agent.COPILOT.template_directory


class TestNeedsTransformation:
    """Tests for needs_transformation property."""

    def test_claude_does_not_need_transformation(self):
        """Test Claude does not require transformation (direct copy)."""
        assert Agent.CLAUDE.needs_transformation is False

    def test_copilot_needs_transformation(self):
        """Test Copilot requires transformation from command format."""
        assert Agent.COPILOT.needs_transformation is True

    def test_only_copilot_needs_transformation(self):
        """Test only Copilot needs transformation among all agents."""
        agents_needing_transformation = [
            agent for agent in Agent if agent.needs_transformation
        ]
        assert agents_needing_transformation == [Agent.COPILOT]


class TestAgentEnumeration:
    """Tests for Agent enum functionality."""

    def test_agent_from_string_claude(self):
        """Test creating Agent from string value 'claude'."""
        assert Agent("claude") == Agent.CLAUDE

    def test_agent_from_string_copilot(self):
        """Test creating Agent from string value 'copilot'."""
        assert Agent("copilot") == Agent.COPILOT

    def test_agent_value_claude(self):
        """Test Claude enum value is 'claude'."""
        assert Agent.CLAUDE.value == "claude"

    def test_agent_value_copilot(self):
        """Test Copilot enum value is 'copilot'."""
        assert Agent.COPILOT.value == "copilot"

    def test_agent_iteration(self):
        """Test iterating over all agents."""
        agents = list(Agent)
        assert Agent.CLAUDE in agents
        assert Agent.COPILOT in agents
        assert len(agents) == 2
