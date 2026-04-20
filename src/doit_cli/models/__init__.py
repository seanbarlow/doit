"""Data models for doit-cli."""

from __future__ import annotations

from .agent import Agent
from .context_config import (
    CommandOverride,
    ContextConfig,
    ContextSource,
    LoadedContext,
    SourceConfig,
)
from .crossref_models import (
    CoverageReport,
    CoverageStatus,
    CrossReference,
    Requirement,
    RequirementCoverage,
    Task,
    TaskReference,
)
from .diagram_models import (
    AcceptanceScenario,
    Cardinality,
    DiagramResult,
    DiagramSection,
    DiagramType,
    EntityAttribute,
    EntityRelationship,
    GeneratedDiagram,
    ParsedEntity,
    ParsedUserStory,
)
from .diagram_models import (
    ValidationResult as DiagramValidationResult,
)
from .project import Project
from .memory_contract import (
    ConstitutionFrontmatter,
    MemoryContractIssue,
    MemoryIssueSeverity,
    OpenQuestion,
    split_frontmatter,
)
from .results import InitResult, VerifyCheck, VerifyResult, VerifyStatus
from .search_models import (
    ContentSnippet,
    MemorySource,
    QueryType,
    SearchHistory,
    SearchQuery,
    SearchResult,
    SourceFilter,
    SourceType,
)
from .status_models import (
    SpecState,
    SpecStatus,
    StatusReport,
)
from .template import Template
from .validation_models import (
    CustomRule,
    RuleOverride,
    Severity,
    ValidationConfig,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    ValidationStatus,
)
from .wizard_models import (
    BackupNotFoundError,
    ConfigBackup,
    WizardCancelledError,
    WizardResult,
    WizardState,
    WizardStep,
    WizardStepError,
)
from .wizard_models import (
    ValidationResult as WizardValidationResult2,
)
from .workflow_models import (
    NavigationCommand,
    StateCorruptionError,
    StepResponse,
    Workflow,
    WorkflowError,
    WorkflowState,
    WorkflowStatus,
    WorkflowStep,
)
from .workflow_models import (
    ValidationError as WorkflowValidationError,
)
from .workflow_models import (
    ValidationResult as WorkflowValidationResult,
)

__all__ = [
    "AcceptanceScenario",
    "Agent",
    "BackupNotFoundError",
    "Cardinality",
    "CommandOverride",
    "ConfigBackup",
    # Memory-file contract
    "ConstitutionFrontmatter",
    "ContentSnippet",
    "ContextConfig",
    "ContextSource",
    "CoverageReport",
    # Cross-reference models
    "CoverageStatus",
    "CrossReference",
    "CustomRule",
    "DiagramResult",
    "DiagramSection",
    # Diagram models
    "DiagramType",
    "DiagramValidationResult",
    "EntityAttribute",
    "EntityRelationship",
    "GeneratedDiagram",
    "InitResult",
    "LoadedContext",
    "MemoryContractIssue",
    "MemoryIssueSeverity",
    "MemorySource",
    "NavigationCommand",
    "OpenQuestion",
    "ParsedEntity",
    "ParsedUserStory",
    "Project",
    # Search models
    "QueryType",
    "Requirement",
    "RequirementCoverage",
    "RuleOverride",
    "SearchHistory",
    "SearchQuery",
    "SearchResult",
    "Severity",
    "SourceConfig",
    "SourceFilter",
    "SourceType",
    # Status models
    "SpecState",
    "SpecStatus",
    "StateCorruptionError",
    "StatusReport",
    "StepResponse",
    "Task",
    "TaskReference",
    "Template",
    "ValidationConfig",
    "ValidationIssue",
    "ValidationResult",
    "ValidationRule",
    "ValidationStatus",
    "VerifyCheck",
    "VerifyResult",
    "VerifyStatus",
    "WizardCancelledError",
    "WizardResult",
    "WizardState",
    # Wizard models
    "WizardStep",
    "WizardStepError",
    "WizardValidationResult2",
    "Workflow",
    "WorkflowError",
    "WorkflowState",
    # Workflow models
    "WorkflowStatus",
    "WorkflowStep",
    "WorkflowValidationError",
    "WorkflowValidationResult",
]
