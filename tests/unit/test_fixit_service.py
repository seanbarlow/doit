"""Unit tests for Fixit service.

Tests for FixitService class which orchestrates the bug-fix workflow lifecycle.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from doit_cli.models.fixit_models import (
    FixPhase,
    FixWorkflow,
    FixitWorkflowState,
    GitHubIssue,
    IssueState,
)


class TestFixitServiceStartWorkflow:
    """Tests for FixitService.start_workflow() method."""

    def test_start_workflow_creates_workflow_with_issue_id(self):
        """Should create workflow for given issue ID."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        # Mock dependencies
        mock_github = MagicMock(spec=GitHubService)
        mock_github.get_issue.return_value = GitHubIssue(
            number=123,
            title="Button click error",
            body="Error when clicking submit",
            state=IssueState.OPEN,
            labels=["bug"],
        )
        mock_github.check_branch_exists.return_value = (False, False)
        mock_github.create_branch.return_value = True

        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        workflow = service.start_workflow(issue_id=123)

        assert workflow is not None
        assert workflow.issue_id == 123
        assert workflow.phase == FixPhase.INVESTIGATING
        assert "fix/123-" in workflow.branch_name

    def test_start_workflow_fails_for_closed_issue(self):
        """Should fail when issue is already closed."""
        from doit_cli.services.fixit_service import FixitService, FixitServiceError
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_github.get_issue.return_value = GitHubIssue(
            number=123,
            title="Closed bug",
            state=IssueState.CLOSED,
        )

        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None  # No existing workflow

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        with pytest.raises(FixitServiceError) as exc_info:
            service.start_workflow(issue_id=123)
        assert "closed" in str(exc_info.value).lower()

    def test_start_workflow_fails_for_nonexistent_issue(self):
        """Should fail when issue doesn't exist."""
        from doit_cli.services.fixit_service import FixitService, FixitServiceError
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_github.get_issue.return_value = None

        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None  # No existing workflow

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        with pytest.raises(FixitServiceError) as exc_info:
            service.start_workflow(issue_id=99999)
        assert "not found" in str(exc_info.value).lower()

    def test_start_workflow_resumes_existing_workflow(self):
        """Should resume if workflow already exists and resume flag is set."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_github.get_issue.return_value = GitHubIssue(
            number=123,
            title="Existing bug",
            state=IssueState.OPEN,
        )

        existing_state = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-existing-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "issue": None,
        }

        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = existing_state

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        workflow = service.start_workflow(issue_id=123, resume=True)

        assert workflow is not None
        assert workflow.id == "fixit-123"
        assert workflow.phase == FixPhase.INVESTIGATING

    def test_start_workflow_fails_when_branch_exists(self):
        """Should fail when fix branch already exists."""
        from doit_cli.services.fixit_service import FixitService, FixitServiceError
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_github.get_issue.return_value = GitHubIssue(
            number=123,
            title="Bug",
            state=IssueState.OPEN,
        )
        mock_github.check_branch_exists.return_value = (True, True)  # Branch exists

        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        with pytest.raises(FixitServiceError) as exc_info:
            service.start_workflow(issue_id=123)
        assert "branch" in str(exc_info.value).lower()


class TestFixitServiceCreateBranchName:
    """Tests for branch name generation."""

    def test_create_branch_name_from_issue_title(self):
        """Should create branch name from issue title."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        branch_name = service._create_branch_name(123, "Button Click Causes Error")

        assert branch_name == "fix/123-button-click-causes-error"

    def test_create_branch_name_handles_special_characters(self):
        """Should handle special characters in title."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        branch_name = service._create_branch_name(
            456, "Bug: API returns 500 (server error) on /users endpoint!"
        )

        assert branch_name.startswith("fix/456-")
        assert "/" not in branch_name.split("fix/")[1]  # No slashes in slug
        assert "!" not in branch_name

    def test_create_branch_name_truncates_long_titles(self):
        """Should truncate very long titles."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        long_title = "This is a very long issue title that should definitely be truncated to a reasonable length for a branch name"
        branch_name = service._create_branch_name(789, long_title)

        assert len(branch_name) <= 60  # Reasonable branch name length
        assert branch_name.startswith("fix/789-")


class TestFixitServiceGetActiveWorkflow:
    """Tests for get_active_workflow method."""

    def test_get_active_workflow_returns_none_when_empty(self):
        """Should return None when no active workflows."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.get_active_fixit_workflow.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.get_active_workflow()

        assert result is None

    def test_get_active_workflow_returns_workflow(self):
        """Should return active workflow when exists."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.get_active_fixit_workflow.return_value = (
            123,
            {
                "workflow": {
                    "id": "fixit-123",
                    "issue_id": 123,
                    "branch_name": "fix/123-bug",
                    "phase": "investigating",
                    "started_at": "2026-01-16T10:00:00",
                    "updated_at": "2026-01-16T10:30:00",
                }
            },
        )

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.get_active_workflow()

        assert result is not None
        assert result.id == "fixit-123"


class TestFixitServiceListBugs:
    """Tests for listing available bugs."""

    def test_list_bugs_delegates_to_github_service(self):
        """Should delegate to GitHubService."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_github.list_bugs.return_value = [
            GitHubIssue(number=1, title="Bug 1", state=IssueState.OPEN),
            GitHubIssue(number=2, title="Bug 2", state=IssueState.OPEN),
        ]
        mock_state = MagicMock(spec=StateManager)

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        bugs = service.list_bugs(label="bug", limit=10)

        assert len(bugs) == 2
        mock_github.list_bugs.assert_called_once_with(label="bug", limit=10)


class TestFixitServiceCancelWorkflow:
    """Tests for cancel_workflow method."""

    def test_cancel_workflow_updates_phase(self):
        """Should update workflow phase to cancelled."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            }
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.cancel_workflow(issue_id=123)

        assert result is True
        # Verify state was saved with cancelled phase
        mock_state.save_fixit_state.assert_called_once()
        saved_state = mock_state.save_fixit_state.call_args[0][0]
        assert saved_state["workflow"]["phase"] == "cancelled"

    def test_cancel_workflow_returns_false_when_not_found(self):
        """Should return False when workflow doesn't exist."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.cancel_workflow(issue_id=999)

        assert result is False


# =============================================================================
# Phase 4: Investigation Tests (T021)
# =============================================================================


class TestFixitServiceStartInvestigation:
    """Tests for start_investigation method."""

    def test_start_investigation_creates_plan(self):
        """Should create investigation plan with keywords from issue."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "issue": {
                "number": 123,
                "title": "Button click error in login form",
                "body": "Error when clicking submit button",
                "state": "open",
                "labels": ["bug"],
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        plan = service.start_investigation(issue_id=123)

        assert plan is not None
        assert len(plan.keywords) > 0
        # Keywords should be extracted from title/body
        assert any("button" in kw.lower() for kw in plan.keywords)

    def test_start_investigation_returns_none_when_no_workflow(self):
        """Should return None when workflow doesn't exist."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        plan = service.start_investigation(issue_id=999)

        assert plan is None


class TestFixitServiceAddFinding:
    """Tests for add_finding method."""

    def test_add_finding_creates_finding(self):
        """Should add finding to investigation plan."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager
        from doit_cli.models.fixit_models import FindingType

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "investigation_plan": {
                "id": "inv-abc",
                "workflow_id": "fixit-123",
                "keywords": ["button", "error"],
                "checkpoints": [],
                "findings": [],
                "created_at": "2026-01-16T10:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        finding = service.add_finding(
            issue_id=123,
            finding_type=FindingType.HYPOTHESIS,
            description="Null pointer exception in click handler",
            file_path="src/login.py",
            line_number=42,
        )

        assert finding is not None
        assert finding.finding_type == FindingType.HYPOTHESIS
        assert finding.description == "Null pointer exception in click handler"
        mock_state.save_fixit_state.assert_called_once()

    def test_add_finding_returns_none_when_no_plan(self):
        """Should return None when no investigation plan exists."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager
        from doit_cli.models.fixit_models import FindingType

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "investigation_plan": None,
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        finding = service.add_finding(
            issue_id=123,
            finding_type=FindingType.HYPOTHESIS,
            description="Test finding",
        )

        assert finding is None


class TestFixitServiceCompleteCheckpoint:
    """Tests for complete_checkpoint method."""

    def test_complete_checkpoint_marks_done(self):
        """Should mark checkpoint as completed."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "investigation_plan": {
                "id": "inv-abc",
                "workflow_id": "fixit-123",
                "keywords": [],
                "checkpoints": [
                    {"id": "cp-1", "title": "Review error logs", "completed": False, "notes": ""},
                    {"id": "cp-2", "title": "Check related code", "completed": False, "notes": ""},
                ],
                "findings": [],
                "created_at": "2026-01-16T10:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.complete_checkpoint(
            issue_id=123,
            checkpoint_id="cp-1",
            notes="Found error in handler",
        )

        assert result is True
        mock_state.save_fixit_state.assert_called_once()

    def test_complete_checkpoint_returns_false_for_invalid_id(self):
        """Should return False for invalid checkpoint ID."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "investigation_plan": {
                "id": "inv-abc",
                "workflow_id": "fixit-123",
                "keywords": [],
                "checkpoints": [],
                "findings": [],
                "created_at": "2026-01-16T10:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.complete_checkpoint(
            issue_id=123,
            checkpoint_id="invalid-id",
        )

        assert result is False


class TestFixitServiceCompleteInvestigation:
    """Tests for complete_investigation method."""

    def test_complete_investigation_advances_phase(self):
        """Should advance phase to planning when root cause found."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager
        from doit_cli.models.fixit_models import FixPhase

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "investigation_plan": {
                "id": "inv-abc",
                "workflow_id": "fixit-123",
                "keywords": [],
                "checkpoints": [],
                "findings": [
                    {
                        "id": "f-1",
                        "type": "confirmed_cause",
                        "description": "Null pointer in handler",
                        "evidence": "",
                        "file_path": None,
                        "line_number": None,
                    }
                ],
                "created_at": "2026-01-16T10:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.complete_investigation(issue_id=123)

        assert result is True
        # Verify phase was updated
        saved_state = mock_state.save_fixit_state.call_args[0][0]
        assert saved_state["workflow"]["phase"] == "planning"


# =============================================================================
# Phase 5: Fix Plan Tests (T027)
# =============================================================================


class TestFixitServiceGenerateFixPlan:
    """Tests for generate_fix_plan method."""

    def test_generate_fix_plan_creates_plan_from_findings(self):
        """Should create fix plan from investigation findings."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager
        from doit_cli.models.fixit_models import PlanStatus

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "planning",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "issue": {
                "number": 123,
                "title": "Button click error",
                "body": "Error when clicking submit",
                "state": "open",
                "labels": ["bug"],
            },
            "investigation_plan": {
                "id": "inv-abc",
                "workflow_id": "fixit-123",
                "keywords": ["button", "error"],
                "checkpoints": [],
                "findings": [
                    {
                        "id": "f-1",
                        "type": "confirmed_cause",
                        "description": "Null pointer in click handler",
                        "evidence": "traceback points to line 42",
                        "file_path": "src/handlers.py",
                        "line_number": 42,
                    },
                    {
                        "id": "f-2",
                        "type": "affected_file",
                        "description": "Handler file needs null check",
                        "evidence": "",
                        "file_path": "src/handlers.py",
                        "line_number": None,
                    },
                ],
                "created_at": "2026-01-16T10:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        plan = service.generate_fix_plan(issue_id=123)

        assert plan is not None
        assert plan.status == PlanStatus.DRAFT
        assert "Null pointer in click handler" in plan.root_cause
        mock_state.save_fixit_state.assert_called_once()

    def test_generate_fix_plan_requires_confirmed_cause(self):
        """Should return None if no confirmed cause found."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "planning",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "investigation_plan": {
                "id": "inv-abc",
                "workflow_id": "fixit-123",
                "keywords": [],
                "checkpoints": [],
                "findings": [
                    {
                        "id": "f-1",
                        "type": "hypothesis",  # Only hypothesis, no confirmed cause
                        "description": "Maybe null pointer?",
                        "evidence": "",
                        "file_path": None,
                        "line_number": None,
                    },
                ],
                "created_at": "2026-01-16T10:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        plan = service.generate_fix_plan(issue_id=123)

        assert plan is None

    def test_generate_fix_plan_returns_none_when_no_workflow(self):
        """Should return None when workflow doesn't exist."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        plan = service.generate_fix_plan(issue_id=999)

        assert plan is None


class TestFixitServiceGetFixPlan:
    """Tests for get_fix_plan method."""

    def test_get_fix_plan_returns_existing_plan(self):
        """Should return existing fix plan."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager
        from doit_cli.models.fixit_models import PlanStatus

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "reviewing",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "fix_plan": {
                "id": "plan-abc",
                "workflow_id": "fixit-123",
                "root_cause": "Null pointer in handler",
                "proposed_solution": "Add null check",
                "affected_files": [
                    {
                        "file_path": "src/handlers.py",
                        "change_type": "modify",
                        "description": "Add null check at line 42",
                    }
                ],
                "risk_level": "low",
                                "status": "draft",
                "created_at": "2026-01-16T11:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        plan = service.get_fix_plan(issue_id=123)

        assert plan is not None
        assert plan.root_cause == "Null pointer in handler"
        assert plan.status == PlanStatus.DRAFT

    def test_get_fix_plan_returns_none_when_no_plan(self):
        """Should return None when no fix plan exists."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "planning",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "fix_plan": None,
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        plan = service.get_fix_plan(issue_id=123)

        assert plan is None


class TestFixitServiceApprovePlan:
    """Tests for approve_plan method."""

    def test_approve_plan_updates_status_and_phase(self):
        """Should update plan status to approved and workflow phase to approved."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "reviewing",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "fix_plan": {
                "id": "plan-abc",
                "workflow_id": "fixit-123",
                "root_cause": "Null pointer",
                "proposed_solution": "Add null check",
                "affected_files": [],
                "risk_level": "low",
                                "status": "pending_review",
                "created_at": "2026-01-16T11:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.approve_plan(issue_id=123)

        assert result is True
        saved_state = mock_state.save_fixit_state.call_args[0][0]
        assert saved_state["fix_plan"]["status"] == "approved"
        assert saved_state["workflow"]["phase"] == "approved"

    def test_approve_plan_returns_false_when_no_plan(self):
        """Should return False when no fix plan exists."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "planning",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "fix_plan": None,
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.approve_plan(issue_id=123)

        assert result is False


class TestFixitServiceSubmitForReview:
    """Tests for submit_for_review method."""

    def test_submit_for_review_updates_status(self):
        """Should update plan status to pending_review."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "planning",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "fix_plan": {
                "id": "plan-abc",
                "workflow_id": "fixit-123",
                "root_cause": "Null pointer",
                "proposed_solution": "Add null check",
                "affected_files": [],
                "risk_level": "low",
                                "status": "draft",
                "created_at": "2026-01-16T11:00:00",
            },
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.submit_for_review(issue_id=123)

        assert result is True
        saved_state = mock_state.save_fixit_state.call_args[0][0]
        assert saved_state["fix_plan"]["status"] == "pending_review"
        assert saved_state["workflow"]["phase"] == "reviewing"


# =============================================================================
# Phase 6: Progress Tracking Tests (T031)
# =============================================================================


class TestFixitServiceGetWorkflowState:
    """Tests for get_workflow_state method."""

    def test_get_workflow_state_returns_complete_state(self):
        """Should return complete workflow state including issue and plans."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager
        from doit_cli.models.fixit_models import FixPhase

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "investigating",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            },
            "issue": {
                "number": 123,
                "title": "Bug fix",
                "body": "Fix the bug",
                "state": "open",
                "labels": ["bug"],
            },
            "investigation_plan": None,
            "fix_plan": None,
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        state = service.get_workflow_state(issue_id=123)

        assert state is not None
        assert state.workflow.id == "fixit-123"
        assert state.workflow.phase == FixPhase.INVESTIGATING
        assert state.issue is not None
        assert state.issue.number == 123

    def test_get_workflow_state_returns_none_when_not_found(self):
        """Should return None when workflow doesn't exist."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        state = service.get_workflow_state(issue_id=999)

        assert state is None


class TestFixitServiceCompleteWorkflow:
    """Tests for complete_workflow method."""

    def test_complete_workflow_updates_phase(self):
        """Should update workflow phase to completed."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "implementing",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            }
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.complete_workflow(issue_id=123, close_issue=True)

        assert result is True
        saved_state = mock_state.save_fixit_state.call_args[0][0]
        assert saved_state["workflow"]["phase"] == "completed"
        mock_github.close_issue.assert_called_once()

    def test_complete_workflow_without_closing_issue(self):
        """Should complete without closing GitHub issue when close_issue=False."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = {
            "workflow": {
                "id": "fixit-123",
                "issue_id": 123,
                "branch_name": "fix/123-bug",
                "phase": "implementing",
                "started_at": "2026-01-16T10:00:00",
                "updated_at": "2026-01-16T10:30:00",
            }
        }

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.complete_workflow(issue_id=123, close_issue=False)

        assert result is True
        mock_github.close_issue.assert_not_called()

    def test_complete_workflow_returns_false_when_not_found(self):
        """Should return False when workflow doesn't exist."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.load_fixit_state.return_value = None

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        result = service.complete_workflow(issue_id=999)

        assert result is False


class TestFixitServiceListWorkflows:
    """Tests for list_workflows method."""

    def test_list_workflows_returns_all_workflows(self):
        """Should return all fixit workflows."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.list_fixit_states.return_value = [
            (123, {
                "workflow": {
                    "id": "fixit-123",
                    "issue_id": 123,
                    "branch_name": "fix/123-bug",
                    "phase": "investigating",
                    "started_at": "2026-01-16T10:00:00",
                    "updated_at": "2026-01-16T10:30:00",
                }
            }),
            (456, {
                "workflow": {
                    "id": "fixit-456",
                    "issue_id": 456,
                    "branch_name": "fix/456-feature",
                    "phase": "completed",
                    "started_at": "2026-01-15T10:00:00",
                    "updated_at": "2026-01-15T12:00:00",
                }
            }),
        ]

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        workflows = service.list_workflows()

        assert len(workflows) == 2
        assert workflows[0][0] == 123
        assert workflows[1][0] == 456

    def test_list_workflows_returns_empty_when_none(self):
        """Should return empty list when no workflows."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.services.github_service import GitHubService
        from doit_cli.services.state_manager import StateManager

        mock_github = MagicMock(spec=GitHubService)
        mock_state = MagicMock(spec=StateManager)
        mock_state.list_fixit_states.return_value = []

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        workflows = service.list_workflows()

        assert workflows == []
