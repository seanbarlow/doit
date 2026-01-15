"""Integration tests for AI context injection.

Tests end-to-end context loading functionality for doit commands.
"""

import subprocess
import pytest
from pathlib import Path


class TestContextShowCommand:
    """Integration tests for doit context show command."""

    @pytest.fixture
    def project_with_context(self, tmp_path: Path):
        """Create a project with context files."""
        # Create .doit/memory directory with constitution and roadmap
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)

        # Create constitution.md
        constitution = memory_dir / "constitution.md"
        constitution.write_text(
            "# Project Constitution\n\n"
            "## Core Principles\n\n"
            "1. Quality over speed\n"
            "2. Test-driven development\n"
            "3. Clear documentation\n\n"
            "## Tech Stack\n\n"
            "- Python 3.11+\n"
            "- pytest for testing\n"
        )

        # Create roadmap.md
        roadmap = memory_dir / "roadmap.md"
        roadmap.write_text(
            "# Project Roadmap\n\n"
            "## P1 - Critical\n\n"
            "- [ ] Feature A\n"
            "- [ ] Feature B\n\n"
            "## P2 - Important\n\n"
            "- [ ] Feature C\n"
        )

        return tmp_path

    @pytest.fixture
    def empty_project(self, tmp_path: Path):
        """Create a project without context files."""
        # Create minimal .doit structure
        doit_dir = tmp_path / ".doit"
        doit_dir.mkdir(parents=True)
        return tmp_path

    def test_context_show_with_files(self, project_with_context: Path):
        """Test context show displays loaded sources when files exist."""
        result = subprocess.run(
            ["doit", "context", "show"],
            cwd=project_with_context,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "AI Context Status" in result.stdout
        assert "Loaded Sources" in result.stdout
        # Should show constitution and roadmap
        assert "constitution" in result.stdout.lower()
        assert "roadmap" in result.stdout.lower()

    def test_context_show_without_files(self, empty_project: Path):
        """Test context show handles missing files gracefully."""
        result = subprocess.run(
            ["doit", "context", "show"],
            cwd=empty_project,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "AI Context Status" in result.stdout
        # Should indicate no sources loaded
        assert "No sources loaded" in result.stdout or "not found" in result.stdout.lower()

    def test_context_show_verbose(self, project_with_context: Path):
        """Test context show --verbose displays content preview."""
        result = subprocess.run(
            ["doit", "context", "show", "--verbose"],
            cwd=project_with_context,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Source Content Preview" in result.stdout
        # Should show content from constitution
        assert "Project Constitution" in result.stdout or "Core Principles" in result.stdout

    def test_context_show_with_command_option(self, project_with_context: Path):
        """Test context show --command option shows command-specific context."""
        result = subprocess.run(
            ["doit", "context", "show", "--command", "specit"],
            cwd=project_with_context,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "specit" in result.stdout.lower()

    def test_context_show_displays_token_counts(self, project_with_context: Path):
        """Test context show displays token information."""
        result = subprocess.run(
            ["doit", "context", "show"],
            cwd=project_with_context,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should show token counts
        assert "tokens" in result.stdout.lower()
        assert "Total" in result.stdout


class TestContextStatusCommand:
    """Integration tests for doit context status command."""

    @pytest.fixture
    def project_with_config(self, tmp_path: Path):
        """Create a project with context configuration."""
        # Create .doit directories
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        config_dir = tmp_path / ".doit" / "config"
        config_dir.mkdir(parents=True)

        # Create context.yaml config
        config = config_dir / "context.yaml"
        config.write_text(
            "version: 1\n"
            "enabled: true\n"
            "max_tokens_per_source: 4000\n"
            "total_max_tokens: 16000\n"
        )

        # Create constitution
        constitution = memory_dir / "constitution.md"
        constitution.write_text("# Constitution\n\nProject principles here.")

        return tmp_path

    @pytest.fixture
    def git_project(self, tmp_path: Path):
        """Create a git project for branch detection tests."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create .doit structure
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        constitution = memory_dir / "constitution.md"
        constitution.write_text("# Constitution\n\nPrinciples.")

        # Create specs directory
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()

        return tmp_path

    def test_context_status_shows_configuration(self, project_with_config: Path):
        """Test context status shows config file status."""
        result = subprocess.run(
            ["doit", "context", "status"],
            cwd=project_with_config,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Context Configuration Status" in result.stdout
        assert "Configuration" in result.stdout

    def test_context_status_shows_source_files(self, project_with_config: Path):
        """Test context status shows source file availability."""
        result = subprocess.run(
            ["doit", "context", "status"],
            cwd=project_with_config,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Source Files" in result.stdout
        assert "constitution" in result.stdout.lower()

    def test_context_status_shows_git_branch(self, git_project: Path):
        """Test context status shows git branch information."""
        result = subprocess.run(
            ["doit", "context", "status"],
            cwd=git_project,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Git Branch" in result.stdout

    def test_context_status_detects_feature_branch(self, git_project: Path):
        """Test context status detects feature branch pattern."""
        # Create initial commit and feature branch
        readme = git_project / "README.md"
        readme.write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=git_project, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=git_project,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "-b", "026-test-feature"],
            cwd=git_project,
            capture_output=True,
        )

        result = subprocess.run(
            ["doit", "context", "status"],
            cwd=git_project,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "026-test-feature" in result.stdout

    def test_context_status_missing_config(self, tmp_path: Path):
        """Test context status handles missing config gracefully."""
        # Create minimal structure
        doit_dir = tmp_path / ".doit"
        doit_dir.mkdir()

        result = subprocess.run(
            ["doit", "context", "status"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should indicate using defaults
        assert "using defaults" in result.stdout.lower() or "not found" in result.stdout.lower()


class TestContextLoadingEndToEnd:
    """End-to-end tests for context loading in command execution."""

    @pytest.fixture
    def full_project(self, tmp_path: Path):
        """Create a full project with all context files."""
        # Create .doit structure
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        config_dir = tmp_path / ".doit" / "config"
        config_dir.mkdir(parents=True)

        # Create constitution
        constitution = memory_dir / "constitution.md"
        constitution.write_text(
            "# Project Constitution\n\n"
            "## Summary\n\n"
            "This is a test project following spec-driven development.\n\n"
            "## Principles\n\n"
            "1. Test first\n"
            "2. Document everything\n"
        )

        # Create roadmap
        roadmap = memory_dir / "roadmap.md"
        roadmap.write_text(
            "# Roadmap\n\n"
            "## P1 - Critical\n\n"
            "- [ ] Core functionality\n"
        )

        # Create config
        config = config_dir / "context.yaml"
        config.write_text(
            "version: 1\n"
            "enabled: true\n"
            "max_tokens_per_source: 4000\n"
            "total_max_tokens: 16000\n"
            "sources:\n"
            "  constitution:\n"
            "    enabled: true\n"
            "    priority: 1\n"
            "  roadmap:\n"
            "    enabled: true\n"
            "    priority: 2\n"
        )

        # Create specs directory
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()

        return tmp_path

    def test_context_loads_both_sources(self, full_project: Path):
        """Test that both constitution and roadmap are loaded."""
        result = subprocess.run(
            ["doit", "context", "show"],
            cwd=full_project,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Both sources should be listed
        output_lower = result.stdout.lower()
        assert "constitution" in output_lower
        assert "roadmap" in output_lower

    def test_context_respects_token_limits(self, full_project: Path):
        """Test that context respects configured token limits."""
        # Create a very large constitution
        memory_dir = full_project / ".doit" / "memory"
        constitution = memory_dir / "constitution.md"
        large_content = "# Constitution\n\n" + ("This is a test paragraph. " * 5000)
        constitution.write_text(large_content)

        # Set a low token limit in config
        config = full_project / ".doit" / "config" / "context.yaml"
        config.write_text(
            "version: 1\n"
            "enabled: true\n"
            "max_tokens_per_source: 100\n"
            "total_max_tokens: 200\n"
        )

        result = subprocess.run(
            ["doit", "context", "show"],
            cwd=full_project,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should indicate truncation
        assert "truncated" in result.stdout.lower()

    def test_context_disabled_shows_message(self, full_project: Path):
        """Test that disabled context shows appropriate message."""
        # Disable context in config
        config = full_project / ".doit" / "config" / "context.yaml"
        config.write_text(
            "version: 1\n"
            "enabled: false\n"
        )

        result = subprocess.run(
            ["doit", "context", "show"],
            cwd=full_project,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "disabled" in result.stdout.lower()

    def test_context_help_available(self):
        """Test that context command help is available."""
        result = subprocess.run(
            ["doit", "context", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "show" in result.stdout.lower()
        assert "status" in result.stdout.lower()


class TestContextWithSpecDirectory:
    """Tests for context loading with spec directory integration."""

    @pytest.fixture
    def project_with_spec(self, tmp_path: Path):
        """Create a git project with spec for current feature."""
        # Initialize git
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create .doit structure
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        constitution = memory_dir / "constitution.md"
        constitution.write_text("# Constitution\n\nPrinciples here.")

        # Create spec for feature 026
        spec_dir = tmp_path / "specs" / "026-test-feature"
        spec_dir.mkdir(parents=True)
        spec_file = spec_dir / "spec.md"
        spec_file.write_text(
            "# Test Feature\n\n"
            "**Status**: In Progress\n\n"
            "## Summary\n\n"
            "This is a test feature for integration testing.\n"
        )

        # Initial commit and create feature branch
        readme = tmp_path / "README.md"
        readme.write_text("# Test Project")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "-b", "026-test-feature"],
            cwd=tmp_path,
            capture_output=True,
        )

        return tmp_path

    def test_context_status_shows_current_spec(self, project_with_spec: Path):
        """Test that context status shows current spec when on feature branch."""
        result = subprocess.run(
            ["doit", "context", "status"],
            cwd=project_with_spec,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should show the feature branch
        assert "026-test-feature" in result.stdout
        # Should show the spec directory
        assert "specs" in result.stdout.lower()
