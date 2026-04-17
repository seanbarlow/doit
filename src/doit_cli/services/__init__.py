"""Services for doit-cli project initialization and management."""

from __future__ import annotations

from .agent_detector import AgentDetector
from .architecture_generator import ArchitectureGenerator
from .backup_service import BackupService
from .context_loader import ContextLoader, estimate_tokens, truncate_content
from .coverage_calculator import CoverageCalculator
from .crossref_service import CrossReferenceService
from .diagram_service import DiagramService
from .entity_parser import EntityParser
from .er_diagram_generator import ERDiagramGenerator
from .input_validator import (
    ChoiceValidator,
    InputValidator,
    PathExistsValidator,
    PatternValidator,
    RequiredValidator,
    chain_validators,
    get_validator,
    register_validator,
    validate_step,
)
from .mermaid_validator import MermaidValidator
from .requirement_parser import RequirementParser
from .scaffolder import Scaffolder
from .section_parser import SectionParser
from .spec_scanner import NotADoitProjectError, SpecNotFoundError, SpecScanner
from .state_manager import StateManager
from .status_reporter import StatusReporter
from .task_parser import TaskParser
from .template_manager import TemplateManager
from .user_journey_generator import UserJourneyGenerator
from .user_story_parser import UserStoryParser
from .validator import Validator
from .workflow_engine import WorkflowEngine

__all__ = [
    "AgentDetector",
    "ArchitectureGenerator",
    "BackupService",
    "ChoiceValidator",
    "ContextLoader",
    "CoverageCalculator",
    "CrossReferenceService",
    # Diagram services
    "DiagramService",
    "ERDiagramGenerator",
    "EntityParser",
    # Input validation
    "InputValidator",
    "MermaidValidator",
    "NotADoitProjectError",
    "PathExistsValidator",
    "PatternValidator",
    "RequiredValidator",
    # Cross-reference services
    "RequirementParser",
    "Scaffolder",
    "SectionParser",
    "SpecNotFoundError",
    # Status dashboard
    "SpecScanner",
    # State management
    "StateManager",
    "StatusReporter",
    "TaskParser",
    "TemplateManager",
    "UserJourneyGenerator",
    "UserStoryParser",
    "Validator",
    # Workflow engine
    "WorkflowEngine",
    "chain_validators",
    "estimate_tokens",
    "get_validator",
    "register_validator",
    "truncate_content",
    "validate_step",
]
