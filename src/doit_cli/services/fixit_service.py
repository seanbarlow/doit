"""Service for orchestrating bug-fix workflow.

This module provides the FixitService class for managing
the complete bug-fix workflow lifecycle.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.fixit_models import (
    FindingType,
    FixPhase,
    FixWorkflow,
    FixitWorkflowState,
    GitHubIssue,
    InvestigationCheckpoint,
    InvestigationFinding,
    InvestigationPlan,
    IssueState,
)
from .github_service import GitHubService
from .state_manager import StateManager


class FixitServiceError(Exception):
    """Error raised when fixit workflow operations fail."""

    pass


class FixitService:
    """Orchestrates the complete bug-fix workflow lifecycle.

    Manages workflow state, coordinates with GitHub for issue operations,
    and provides methods for each workflow phase.
    """

    MAX_BRANCH_NAME_LENGTH = 60

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        state_manager: Optional[StateManager] = None,
    ):
        """Initialize the fixit service.

        Args:
            github_service: GitHubService instance for issue operations.
            state_manager: StateManager instance for state persistence.
        """
        self.github = github_service or GitHubService()
        self.state_manager = state_manager or StateManager()

    # =========================================================================
    # Workflow Lifecycle Methods
    # =========================================================================

    def start_workflow(
        self,
        issue_id: int,
        resume: bool = False,
        manual_branch: Optional[str] = None,
    ) -> FixWorkflow:
        """Start a new bug-fix workflow for an issue.

        Args:
            issue_id: GitHub issue number to fix.
            resume: If True, resume existing workflow instead of failing.
            manual_branch: Optional custom branch name.

        Returns:
            FixWorkflow for the started workflow.

        Raises:
            FixitServiceError: If issue not found, closed, or branch exists.
        """
        # Check for existing workflow
        existing_state = self.state_manager.load_fixit_state(issue_id)
        if existing_state:
            if resume:
                return FixWorkflow.from_dict(existing_state["workflow"])
            raise FixitServiceError(
                f"Workflow already exists for issue #{issue_id}. "
                "Use --resume to continue or cancel the existing workflow."
            )

        # Fetch and validate issue
        issue = self.github.get_issue(issue_id)
        if issue is None:
            raise FixitServiceError(f"Issue #{issue_id} not found.")
        if issue.state == IssueState.CLOSED:
            raise FixitServiceError(
                f"Issue #{issue_id} is already closed. Cannot start workflow."
            )

        # Determine branch name
        branch_name = manual_branch or self._create_branch_name(issue_id, issue.title)

        # Check if branch already exists
        local_exists, remote_exists = self.github.check_branch_exists(branch_name)
        if local_exists or remote_exists:
            raise FixitServiceError(
                f"Branch '{branch_name}' already exists. "
                "Use --branch to specify a different name."
            )

        # Create the branch
        if not self.github.create_branch(branch_name):
            raise FixitServiceError(f"Failed to create branch '{branch_name}'.")

        # Create workflow
        workflow = FixWorkflow(
            id=f"fixit-{issue_id}",
            issue_id=issue_id,
            branch_name=branch_name,
            phase=FixPhase.INVESTIGATING,
        )

        # Save state
        state = FixitWorkflowState(workflow=workflow, issue=issue)
        self.state_manager.save_fixit_state(state.to_dict(), issue_id)

        return workflow

    def cancel_workflow(self, issue_id: int) -> bool:
        """Cancel an active workflow.

        Args:
            issue_id: GitHub issue number.

        Returns:
            True if cancelled, False if not found.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return False

        # Update phase to cancelled
        state_data["workflow"]["phase"] = FixPhase.CANCELLED.value
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()

        self.state_manager.save_fixit_state(state_data, issue_id)
        return True

    def complete_workflow(self, issue_id: int, close_issue: bool = True) -> bool:
        """Complete a workflow after successful fix.

        Args:
            issue_id: GitHub issue number.
            close_issue: Whether to close the GitHub issue.

        Returns:
            True if completed, False if not found.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return False

        # Update phase to completed
        state_data["workflow"]["phase"] = FixPhase.COMPLETED.value
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()

        self.state_manager.save_fixit_state(state_data, issue_id)

        # Optionally close the issue
        if close_issue:
            self.github.close_issue(
                issue_id,
                comment="Fixed via doit fixit workflow."
            )

        return True

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_active_workflow(self) -> Optional[FixWorkflow]:
        """Get the currently active workflow.

        Returns:
            FixWorkflow if active workflow exists, None otherwise.
        """
        result = self.state_manager.get_active_fixit_workflow()
        if result is None:
            return None

        issue_id, state_data = result
        return FixWorkflow.from_dict(state_data["workflow"])

    def get_workflow(self, issue_id: int) -> Optional[FixWorkflow]:
        """Get workflow for a specific issue.

        Args:
            issue_id: GitHub issue number.

        Returns:
            FixWorkflow if exists, None otherwise.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return None
        return FixWorkflow.from_dict(state_data["workflow"])

    def get_workflow_state(self, issue_id: int) -> Optional[FixitWorkflowState]:
        """Get complete workflow state for an issue.

        Args:
            issue_id: GitHub issue number.

        Returns:
            FixitWorkflowState if exists, None otherwise.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return None
        return FixitWorkflowState.from_dict(state_data)

    def list_bugs(self, label: str = "bug", limit: int = 20) -> list[GitHubIssue]:
        """List open bugs from GitHub.

        Args:
            label: Label to filter by.
            limit: Maximum number to return.

        Returns:
            List of GitHubIssue objects.
        """
        return self.github.list_bugs(label=label, limit=limit)

    def list_workflows(self) -> list[tuple[int, FixWorkflow]]:
        """List all fixit workflows.

        Returns:
            List of (issue_id, workflow) tuples.
        """
        states = self.state_manager.list_fixit_states()
        workflows = []
        for issue_id, state_data in states:
            try:
                workflow = FixWorkflow.from_dict(state_data["workflow"])
                workflows.append((issue_id, workflow))
            except (KeyError, ValueError):
                continue
        return workflows

    # =========================================================================
    # Phase Transition Methods
    # =========================================================================

    def advance_phase(self, issue_id: int, to_phase: FixPhase) -> bool:
        """Advance workflow to a new phase.

        Args:
            issue_id: GitHub issue number.
            to_phase: Target phase.

        Returns:
            True if advanced, False if not allowed or not found.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return False

        current_phase = FixPhase(state_data["workflow"]["phase"])

        # Validate phase transition
        if not self._is_valid_transition(current_phase, to_phase):
            return False

        state_data["workflow"]["phase"] = to_phase.value
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()

        self.state_manager.save_fixit_state(state_data, issue_id)
        return True

    def _is_valid_transition(self, from_phase: FixPhase, to_phase: FixPhase) -> bool:
        """Check if a phase transition is valid.

        Args:
            from_phase: Current phase.
            to_phase: Target phase.

        Returns:
            True if transition is allowed.
        """
        valid_transitions = {
            FixPhase.INITIALIZED: {FixPhase.INVESTIGATING, FixPhase.CANCELLED},
            FixPhase.INVESTIGATING: {FixPhase.PLANNING, FixPhase.CANCELLED},
            FixPhase.PLANNING: {FixPhase.REVIEWING, FixPhase.CANCELLED},
            FixPhase.REVIEWING: {FixPhase.APPROVED, FixPhase.PLANNING},
            FixPhase.APPROVED: {FixPhase.IMPLEMENTING},
            FixPhase.IMPLEMENTING: {FixPhase.COMPLETED},
            FixPhase.COMPLETED: set(),
            FixPhase.CANCELLED: set(),
        }

        return to_phase in valid_transitions.get(from_phase, set())

    # =========================================================================
    # Investigation Methods (T022-T024)
    # =========================================================================

    def start_investigation(self, issue_id: int) -> Optional["InvestigationPlan"]:
        """Start investigation for a workflow.

        Creates an InvestigationPlan with keywords extracted from the issue.

        Args:
            issue_id: GitHub issue number.

        Returns:
            InvestigationPlan if created, None if workflow not found.
        """
        from uuid import uuid4

        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return None

        # Extract keywords from issue
        issue_data = state_data.get("issue")
        keywords = []
        if issue_data:
            # Extract words from title and body
            text = f"{issue_data.get('title', '')} {issue_data.get('body', '')}"
            # Simple keyword extraction - split and filter
            words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
            # Remove common words and deduplicate
            stopwords = {"the", "and", "for", "with", "this", "that", "from", "when"}
            keywords = list(dict.fromkeys(w for w in words if w not in stopwords))[:10]

        # Create investigation plan
        plan = InvestigationPlan(
            id=f"inv-{uuid4().hex[:8]}",
            workflow_id=state_data["workflow"]["id"],
            keywords=keywords,
            checkpoints=[
                InvestigationCheckpoint(id=f"cp-{uuid4().hex[:6]}", title="Review error logs and stack traces"),
                InvestigationCheckpoint(id=f"cp-{uuid4().hex[:6]}", title="Identify affected code paths"),
                InvestigationCheckpoint(id=f"cp-{uuid4().hex[:6]}", title="Search for related issues or commits"),
                InvestigationCheckpoint(id=f"cp-{uuid4().hex[:6]}", title="Formulate root cause hypothesis"),
            ],
        )

        # Save updated state
        state_data["investigation_plan"] = plan.to_dict()
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()
        self.state_manager.save_fixit_state(state_data, issue_id)

        return plan

    def add_finding(
        self,
        issue_id: int,
        finding_type: "FindingType",
        description: str,
        evidence: str = "",
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
    ) -> Optional["InvestigationFinding"]:
        """Add a finding to the investigation.

        Args:
            issue_id: GitHub issue number.
            finding_type: Type of finding.
            description: Description of the finding.
            evidence: Supporting evidence.
            file_path: Related source file.
            line_number: Line number in file.

        Returns:
            InvestigationFinding if added, None if no plan exists.
        """
        from uuid import uuid4

        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return None

        plan_data = state_data.get("investigation_plan")
        if not plan_data:
            return None

        # Create finding
        finding = InvestigationFinding(
            id=f"f-{uuid4().hex[:8]}",
            finding_type=finding_type,
            description=description,
            evidence=evidence,
            file_path=file_path,
            line_number=line_number,
        )

        # Add to plan
        if "findings" not in plan_data:
            plan_data["findings"] = []
        plan_data["findings"].append(finding.to_dict())

        # Save updated state
        state_data["investigation_plan"] = plan_data
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()
        self.state_manager.save_fixit_state(state_data, issue_id)

        return finding

    def complete_checkpoint(
        self,
        issue_id: int,
        checkpoint_id: str,
        notes: str = "",
    ) -> bool:
        """Mark a checkpoint as completed.

        Args:
            issue_id: GitHub issue number.
            checkpoint_id: ID of checkpoint to complete.
            notes: Optional notes about completion.

        Returns:
            True if completed, False if checkpoint not found.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return False

        plan_data = state_data.get("investigation_plan")
        if not plan_data:
            return False

        # Find and update checkpoint
        checkpoints = plan_data.get("checkpoints", [])
        found = False
        for cp in checkpoints:
            if cp["id"] == checkpoint_id:
                cp["completed"] = True
                cp["notes"] = notes
                found = True
                break

        if not found:
            return False

        # Save updated state
        state_data["investigation_plan"]["checkpoints"] = checkpoints
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()
        self.state_manager.save_fixit_state(state_data, issue_id)

        return True

    def complete_investigation(self, issue_id: int) -> bool:
        """Complete investigation and advance to planning phase.

        Requires at least one confirmed_cause finding.

        Args:
            issue_id: GitHub issue number.

        Returns:
            True if completed, False if no root cause found.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return False

        plan_data = state_data.get("investigation_plan")
        if not plan_data:
            return False

        # Check for confirmed cause
        findings = plan_data.get("findings", [])
        has_root_cause = any(f.get("type") == "confirmed_cause" for f in findings)

        if not has_root_cause:
            return False

        # Advance to planning phase
        state_data["workflow"]["phase"] = FixPhase.PLANNING.value
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()
        self.state_manager.save_fixit_state(state_data, issue_id)

        return True

    def get_investigation_plan(self, issue_id: int) -> Optional["InvestigationPlan"]:
        """Get the investigation plan for a workflow.

        Args:
            issue_id: GitHub issue number.

        Returns:
            InvestigationPlan if exists, None otherwise.
        """
        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return None

        plan_data = state_data.get("investigation_plan")
        if not plan_data:
            return None

        return InvestigationPlan.from_dict(plan_data)

    # =========================================================================
    # Fix Plan Methods (T028)
    # =========================================================================

    def generate_fix_plan(self, issue_id: int) -> Optional["FixPlan"]:
        """Generate a fix plan from investigation findings.

        Creates a FixPlan with root cause from confirmed_cause findings
        and proposed file changes from affected_file findings.

        Args:
            issue_id: GitHub issue number.

        Returns:
            FixPlan if created, None if no workflow or no confirmed cause.
        """
        from uuid import uuid4
        from ..models.fixit_models import ChangeType, FixPlan, FileChange, PlanStatus, RiskLevel

        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return None

        # Get investigation plan
        plan_data = state_data.get("investigation_plan")
        if not plan_data:
            return None

        findings = plan_data.get("findings", [])

        # Find confirmed cause
        confirmed_causes = [f for f in findings if f.get("type") == "confirmed_cause"]
        if not confirmed_causes:
            return None

        # Build root cause from confirmed_cause findings
        root_cause = "\n".join(f["description"] for f in confirmed_causes)

        # Build file changes from affected_file findings
        file_changes = []
        for f in findings:
            if f.get("type") == "affected_file" and f.get("file_path"):
                file_changes.append(FileChange(
                    file_path=f["file_path"],
                    change_type=ChangeType.MODIFY,
                    description=f["description"],
                ))

        # Also include files from confirmed_cause
        for f in confirmed_causes:
            if f.get("file_path"):
                file_changes.append(FileChange(
                    file_path=f["file_path"],
                    change_type=ChangeType.MODIFY,
                    description=f"Fix: {f['description']}",
                ))

        # Create fix plan
        fix_plan = FixPlan(
            id=f"plan-{uuid4().hex[:8]}",
            workflow_id=state_data["workflow"]["id"],
            root_cause=root_cause,
            proposed_solution="Apply fix based on confirmed root cause analysis",
            affected_files=file_changes,
            risk_level=RiskLevel.LOW if len(file_changes) <= 2 else RiskLevel.MEDIUM,
            status=PlanStatus.DRAFT,
        )

        # Save updated state
        state_data["fix_plan"] = fix_plan.to_dict()
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()
        self.state_manager.save_fixit_state(state_data, issue_id)

        return fix_plan

    def get_fix_plan(self, issue_id: int) -> Optional["FixPlan"]:
        """Get the fix plan for a workflow.

        Args:
            issue_id: GitHub issue number.

        Returns:
            FixPlan if exists, None otherwise.
        """
        from ..models.fixit_models import FixPlan

        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return None

        plan_data = state_data.get("fix_plan")
        if not plan_data:
            return None

        return FixPlan.from_dict(plan_data)

    def approve_plan(self, issue_id: int) -> bool:
        """Approve a fix plan and advance to approved phase.

        Args:
            issue_id: GitHub issue number.

        Returns:
            True if approved, False if no plan exists.
        """
        from ..models.fixit_models import PlanStatus

        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return False

        plan_data = state_data.get("fix_plan")
        if not plan_data:
            return False

        # Update plan status
        plan_data["status"] = PlanStatus.APPROVED.value
        state_data["fix_plan"] = plan_data

        # Advance workflow phase
        state_data["workflow"]["phase"] = FixPhase.APPROVED.value
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()

        self.state_manager.save_fixit_state(state_data, issue_id)
        return True

    def submit_for_review(self, issue_id: int) -> bool:
        """Submit fix plan for review.

        Args:
            issue_id: GitHub issue number.

        Returns:
            True if submitted, False if no plan exists.
        """
        from ..models.fixit_models import PlanStatus

        state_data = self.state_manager.load_fixit_state(issue_id)
        if not state_data:
            return False

        plan_data = state_data.get("fix_plan")
        if not plan_data:
            return False

        # Update plan status
        plan_data["status"] = PlanStatus.PENDING_REVIEW.value
        state_data["fix_plan"] = plan_data

        # Advance workflow phase to reviewing
        state_data["workflow"]["phase"] = FixPhase.REVIEWING.value
        state_data["workflow"]["updated_at"] = datetime.now().isoformat()

        self.state_manager.save_fixit_state(state_data, issue_id)
        return True

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _create_branch_name(self, issue_id: int, title: str) -> str:
        """Create a branch name from issue ID and title.

        Args:
            issue_id: GitHub issue number.
            title: Issue title.

        Returns:
            Branch name in format: fix/{issue_id}-{slug}
        """
        # Convert to lowercase and replace non-alphanumeric with hyphens
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")

        # Build branch name
        branch_name = f"fix/{issue_id}-{slug}"

        # Truncate if too long
        if len(branch_name) > self.MAX_BRANCH_NAME_LENGTH:
            # Keep fix/{issue_id}- prefix, truncate slug
            prefix = f"fix/{issue_id}-"
            max_slug_length = self.MAX_BRANCH_NAME_LENGTH - len(prefix)
            slug = slug[:max_slug_length].rstrip("-")
            branch_name = f"{prefix}{slug}"

        return branch_name

    def is_github_available(self) -> bool:
        """Check if GitHub API is available.

        Returns:
            True if GitHub is accessible.
        """
        return self.github.is_available()
