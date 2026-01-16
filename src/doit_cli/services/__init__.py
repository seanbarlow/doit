"""Services for doit-cli project initialization and management."""

from .agent_detector import AgentDetector
from .backup_service import BackupService
from .context_loader import ContextLoader, estimate_tokens, truncate_content
from .scaffolder import Scaffolder
from .template_manager import TemplateManager
from .validator import Validator
from .input_validator import (
    InputValidator,
    RequiredValidator,
    PathExistsValidator,
    ChoiceValidator,
    PatternValidator,
    get_validator,
    register_validator,
    chain_validators,
    validate_step,
)
from .workflow_engine import WorkflowEngine
from .state_manager import StateManager

__all__ = [
    "AgentDetector",
    "BackupService",
    "ContextLoader",
    "Scaffolder",
    "TemplateManager",
    "Validator",
    "estimate_tokens",
    "truncate_content",
    # Input validation
    "InputValidator",
    "RequiredValidator",
    "PathExistsValidator",
    "ChoiceValidator",
    "PatternValidator",
    "get_validator",
    "register_validator",
    "chain_validators",
    "validate_step",
    # Workflow engine
    "WorkflowEngine",
    # State management
    "StateManager",
]
