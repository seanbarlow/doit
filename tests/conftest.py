"""Shared pytest fixtures for doit-cli tests."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def project_dir(temp_dir):
    """Create a temporary project directory with basic structure."""
    project_path = temp_dir / "test_project"
    project_path.mkdir()
    return project_path


@pytest.fixture
def initialized_project(project_dir):
    """Create a project with .doit/ structure initialized."""
    from doit_cli.models.project import Project
    from doit_cli.services.scaffolder import Scaffolder

    project = Project(path=project_dir)
    scaffolder = Scaffolder(project)
    scaffolder.create_doit_structure()

    return project


@pytest.fixture
def claude_project(initialized_project):
    """Create a project with Claude agent initialized."""
    from doit_cli.models.agent import Agent
    from doit_cli.services.scaffolder import Scaffolder

    scaffolder = Scaffolder(initialized_project)
    scaffolder.create_agent_directory(Agent.CLAUDE)

    # Create sample command file (Claude uses doit.*.md naming convention)
    command_dir = initialized_project.command_directory(Agent.CLAUDE)
    sample_file = command_dir / "doit.specit.md"
    sample_file.write_text("# Test template\n")

    return initialized_project


@pytest.fixture
def copilot_project(initialized_project):
    """Create a project with Copilot agent initialized."""
    from doit_cli.models.agent import Agent
    from doit_cli.services.scaffolder import Scaffolder

    scaffolder = Scaffolder(initialized_project)
    scaffolder.create_agent_directory(Agent.COPILOT)

    # Create sample prompt file
    prompt_dir = initialized_project.command_directory(Agent.COPILOT)
    sample_file = prompt_dir / "doit-specit.prompt.md"
    sample_file.write_text("---\nmode: agent\ndescription: Test\n---\n# Test\n")

    return initialized_project


@pytest.fixture
def both_agents_project(initialized_project):
    """Create a project with both Claude and Copilot initialized."""
    from doit_cli.models.agent import Agent
    from doit_cli.services.scaffolder import Scaffolder

    scaffolder = Scaffolder(initialized_project)
    scaffolder.create_agent_directory(Agent.CLAUDE)
    scaffolder.create_agent_directory(Agent.COPILOT)

    return initialized_project
