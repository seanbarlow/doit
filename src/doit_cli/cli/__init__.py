"""CLI commands for doit-cli."""

from __future__ import annotations

from .init_command import init_command, parse_agent_string, run_init
from .memory_command import memory_app
from .verify_command import verify_command
from .workflow_mixin import (
    WorkflowMixin,
    create_non_interactive_workflow,
    non_interactive_option,
    validate_required_defaults,
    workflow_command_options,
)

__all__ = [
    # Workflow support
    "WorkflowMixin",
    "create_non_interactive_workflow",
    "init_command",
    "memory_app",
    "non_interactive_option",
    "parse_agent_string",
    "run_init",
    "validate_required_defaults",
    "verify_command",
    "workflow_command_options",
]
