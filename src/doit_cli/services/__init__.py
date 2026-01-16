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
from .spec_scanner import SpecScanner, NotADoitProjectError, SpecNotFoundError
from .status_reporter import StatusReporter
from .requirement_parser import RequirementParser
from .task_parser import TaskParser
from .coverage_calculator import CoverageCalculator
from .crossref_service import CrossReferenceService

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
    # Status dashboard
    "SpecScanner",
    "NotADoitProjectError",
    "SpecNotFoundError",
    "StatusReporter",
    # Cross-reference services
    "RequirementParser",
    "TaskParser",
    "CoverageCalculator",
    "CrossReferenceService",
]
