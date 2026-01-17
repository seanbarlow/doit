"""Data models for bug-fix workflow.

This module contains all data models, enums, and dataclasses
for the doit fixit command workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# =============================================================================
# Enums (T004-T007)
# =============================================================================


class FixPhase(Enum):
    """Workflow phase states for bug-fix workflow."""

    INITIALIZED = "initialized"
    INVESTIGATING = "investigating"
    PLANNING = "planning"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    IMPLEMENTING = "implementing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FindingType(Enum):
    """Types of investigation findings."""

    HYPOTHESIS = "hypothesis"
    CONFIRMED_CAUSE = "confirmed_cause"
    AFFECTED_FILE = "affected_file"
    REPRODUCTION_STEP = "reproduction_step"
    RELATED_COMMIT = "related_commit"


class RiskLevel(Enum):
    """Risk levels for fix plans."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PlanStatus(Enum):
    """Status states for fix plans."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    REVISION_NEEDED = "revision_needed"
    APPROVED = "approved"


class IssueState(Enum):
    """GitHub issue states."""

    OPEN = "open"
    CLOSED = "closed"


class ChangeType(Enum):
    """Types of file changes in fix plans."""

    MODIFY = "modify"
    ADD = "add"
    DELETE = "delete"


# =============================================================================
# Models (T008-T011)
# =============================================================================


@dataclass
class GitHubIssue:
    """Represents a GitHub issue fetched from the repository."""

    number: int
    title: str
    body: str = ""
    state: IssueState = IssueState.OPEN
    labels: list[str] = field(default_factory=list)
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "GitHubIssue":
        """Create GitHubIssue from gh CLI JSON output."""
        state = IssueState(data.get("state", "open").lower())
        labels = [label["name"] if isinstance(label, dict) else label
                  for label in data.get("labels", [])]
        return cls(
            number=data["number"],
            title=data["title"],
            body=data.get("body", "") or "",
            state=state,
            labels=labels,
            created_at=None,  # Can be parsed from data if needed
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state.value,
            "labels": self.labels,
        }


@dataclass
class FixWorkflow:
    """Represents an in-progress bug fix workflow with its current phase and state."""

    id: str
    issue_id: int
    branch_name: str
    phase: FixPhase = FixPhase.INITIALIZED
    started_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "branch_name": self.branch_name,
            "phase": self.phase.value,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FixWorkflow":
        """Create FixWorkflow from dictionary."""
        return cls(
            id=data["id"],
            issue_id=data["issue_id"],
            branch_name=data["branch_name"],
            phase=FixPhase(data["phase"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class InvestigationFinding:
    """A discovered fact during investigation."""

    id: str
    finding_type: FindingType
    description: str
    evidence: str = ""
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.finding_type.value,
            "description": self.description,
            "evidence": self.evidence,
            "file_path": self.file_path,
            "line_number": self.line_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InvestigationFinding":
        """Create InvestigationFinding from dictionary."""
        return cls(
            id=data["id"],
            finding_type=FindingType(data["type"]),
            description=data["description"],
            evidence=data.get("evidence", ""),
            file_path=data.get("file_path"),
            line_number=data.get("line_number"),
        )


@dataclass
class InvestigationCheckpoint:
    """Tracks progress through investigation steps."""

    id: str
    title: str
    completed: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InvestigationCheckpoint":
        """Create InvestigationCheckpoint from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            completed=data.get("completed", False),
            notes=data.get("notes", ""),
        )


@dataclass
class InvestigationPlan:
    """Documents the approach for investigating a bug."""

    id: str
    workflow_id: str
    keywords: list[str] = field(default_factory=list)
    checkpoints: list[InvestigationCheckpoint] = field(default_factory=list)
    findings: list[InvestigationFinding] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "keywords": self.keywords,
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
            "findings": [f.to_dict() for f in self.findings],
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InvestigationPlan":
        """Create InvestigationPlan from dictionary."""
        return cls(
            id=data["id"],
            workflow_id=data["workflow_id"],
            keywords=data.get("keywords", []),
            checkpoints=[InvestigationCheckpoint.from_dict(cp)
                        for cp in data.get("checkpoints", [])],
            findings=[InvestigationFinding.from_dict(f)
                     for f in data.get("findings", [])],
            created_at=datetime.fromisoformat(data["created_at"])
                       if "created_at" in data else datetime.now(),
        )


@dataclass
class FileChange:
    """Describes a file modification in a fix plan."""

    file_path: str
    change_type: ChangeType
    description: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "change_type": self.change_type.value,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FileChange":
        """Create FileChange from dictionary."""
        return cls(
            file_path=data["file_path"],
            change_type=ChangeType(data["change_type"]),
            description=data["description"],
        )


@dataclass
class FixPlan:
    """Documents the approved approach to fix the bug."""

    id: str
    workflow_id: str
    root_cause: str = ""
    proposed_solution: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    status: PlanStatus = PlanStatus.DRAFT
    affected_files: list[FileChange] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "root_cause": self.root_cause,
            "proposed_solution": self.proposed_solution,
            "risk_level": self.risk_level.value,
            "status": self.status.value,
            "affected_files": [f.to_dict() for f in self.affected_files],
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FixPlan":
        """Create FixPlan from dictionary."""
        return cls(
            id=data["id"],
            workflow_id=data["workflow_id"],
            root_cause=data.get("root_cause", ""),
            proposed_solution=data.get("proposed_solution", ""),
            risk_level=RiskLevel(data.get("risk_level", "low")),
            status=PlanStatus(data.get("status", "draft")),
            affected_files=[FileChange.from_dict(f)
                           for f in data.get("affected_files", [])],
            created_at=datetime.fromisoformat(data["created_at"])
                       if "created_at" in data else datetime.now(),
            approved_at=datetime.fromisoformat(data["approved_at"])
                       if data.get("approved_at") else None,
        )


@dataclass
class FixitWorkflowState:
    """Complete state for a fixit workflow, used for persistence."""

    workflow: FixWorkflow
    issue: Optional[GitHubIssue] = None
    investigation_plan: Optional[InvestigationPlan] = None
    fix_plan: Optional[FixPlan] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "workflow": self.workflow.to_dict(),
            "issue": self.issue.to_dict() if self.issue else None,
            "investigation_plan": self.investigation_plan.to_dict()
                                 if self.investigation_plan else None,
            "fix_plan": self.fix_plan.to_dict() if self.fix_plan else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FixitWorkflowState":
        """Create FixitWorkflowState from dictionary."""
        return cls(
            workflow=FixWorkflow.from_dict(data["workflow"]),
            issue=GitHubIssue.from_dict(data["issue"])
                  if data.get("issue") else None,
            investigation_plan=InvestigationPlan.from_dict(data["investigation_plan"])
                              if data.get("investigation_plan") else None,
            fix_plan=FixPlan.from_dict(data["fix_plan"])
                    if data.get("fix_plan") else None,
        )
