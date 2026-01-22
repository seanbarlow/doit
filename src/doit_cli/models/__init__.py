"""Data models for doit-cli."""

from .agent import Agent
from .project import Project
from .template import Template
from .results import InitResult, VerifyResult, VerifyCheck, VerifyStatus
from .context_config import (
    ContextConfig,
    SourceConfig,
    CommandOverride,
    ContextSource,
    LoadedContext,
)
from .validation_models import (
    Severity,
    ValidationStatus,
    ValidationRule,
    ValidationIssue,
    ValidationResult,
    RuleOverride,
    CustomRule,
    ValidationConfig,
)
from .workflow_models import (
    WorkflowStatus,
    WorkflowStep,
    Workflow,
    StepResponse,
    WorkflowState,
    ValidationResult as WorkflowValidationResult,
    WorkflowError,
    ValidationError as WorkflowValidationError,
    NavigationCommand,
    StateCorruptionError,
)
from .status_models import (
    SpecState,
    SpecStatus,
    StatusReport,
)
from .crossref_models import (
    CoverageStatus,
    Requirement,
    TaskReference,
    Task,
    CrossReference,
    RequirementCoverage,
    CoverageReport,
)
from .diagram_models import (
    DiagramType,
    Cardinality,
    AcceptanceScenario,
    ParsedUserStory,
    EntityAttribute,
    EntityRelationship,
    ParsedEntity,
    DiagramSection,
    ValidationResult as DiagramValidationResult,
    GeneratedDiagram,
    DiagramResult,
)
from .search_models import (
    QueryType,
    SourceType,
    SourceFilter,
    SearchQuery,
    SearchResult,
    MemorySource,
    ContentSnippet,
    SearchHistory,
)
from .wizard_models import (
    WizardStep,
    ValidationResult as WizardValidationResult2,
    WizardState,
    WizardResult,
    ConfigBackup,
    WizardCancelledError,
    WizardStepError,
    BackupNotFoundError,
)

__all__ = [
    "Agent",
    "Project",
    "Template",
    "InitResult",
    "VerifyResult",
    "VerifyCheck",
    "VerifyStatus",
    "ContextConfig",
    "SourceConfig",
    "CommandOverride",
    "ContextSource",
    "LoadedContext",
    "Severity",
    "ValidationStatus",
    "ValidationRule",
    "ValidationIssue",
    "ValidationResult",
    "RuleOverride",
    "CustomRule",
    "ValidationConfig",
    # Workflow models
    "WorkflowStatus",
    "WorkflowStep",
    "Workflow",
    "StepResponse",
    "WorkflowState",
    "WorkflowValidationResult",
    "WorkflowError",
    "WorkflowValidationError",
    "NavigationCommand",
    "StateCorruptionError",
    # Status models
    "SpecState",
    "SpecStatus",
    "StatusReport",
    # Cross-reference models
    "CoverageStatus",
    "Requirement",
    "TaskReference",
    "Task",
    "CrossReference",
    "RequirementCoverage",
    "CoverageReport",
    # Diagram models
    "DiagramType",
    "Cardinality",
    "AcceptanceScenario",
    "ParsedUserStory",
    "EntityAttribute",
    "EntityRelationship",
    "ParsedEntity",
    "DiagramSection",
    "DiagramValidationResult",
    "GeneratedDiagram",
    "DiagramResult",
    # Search models
    "QueryType",
    "SourceType",
    "SourceFilter",
    "SearchQuery",
    "SearchResult",
    "MemorySource",
    "ContentSnippet",
    "SearchHistory",
    # Wizard models
    "WizardStep",
    "WizardValidationResult2",
    "WizardState",
    "WizardResult",
    "ConfigBackup",
    "WizardCancelledError",
    "WizardStepError",
    "BackupNotFoundError",
]
