"""Integration tests for fixit workflow.

Tests for Feature 034: Bug-Fix Workflow Command
Tests the complete lifecycle: start → investigate → plan → complete
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from doit_cli.main import app
from doit_cli.models.fixit_models import (
    FixPhase,
    GitHubIssue,
    IssueState,
)


runner = CliRunner()


class TestFixitWorkflowStartCommand:
    """Integration tests for doit fixit start command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_fixit_starts_workflow_for_issue(self, mock_service_class, tmp_path):
        """doit fixit start <issue_id> should start workflow."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.is_github_available.return_value = True
        mock_service.start_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test-bug",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "start", "123"])

        assert result.exit_code == 0
        mock_service.start_workflow.assert_called_once_with(
            issue_id=123,
            resume=False,
            manual_branch=None,
        )

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_fixit_shows_error_for_nonexistent_issue(self, mock_service_class):
        """doit fixit start should show error for nonexistent issue."""
        from doit_cli.services.fixit_service import FixitServiceError

        mock_service = MagicMock()
        mock_service.is_github_available.return_value = True
        mock_service.start_workflow.side_effect = FixitServiceError("Issue #999 not found.")
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "start", "999"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_fixit_resumes_existing_workflow(self, mock_service_class):
        """doit fixit start --resume should continue existing workflow."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.is_github_available.return_value = True
        mock_service.start_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test-bug",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "start", "123", "--resume"])

        assert result.exit_code == 0
        assert "resumed" in result.output.lower()
        mock_service.start_workflow.assert_called_once_with(
            issue_id=123,
            resume=True,
            manual_branch=None,
        )


class TestFixitWorkflowListCommand:
    """Integration tests for doit fixit list command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_fixit_list_shows_open_bugs(self, mock_service_class):
        """doit fixit list should show open bugs."""
        mock_service = MagicMock()
        mock_service.list_bugs.return_value = [
            GitHubIssue(number=1, title="Bug 1", state=IssueState.OPEN, labels=["bug"]),
            GitHubIssue(number=2, title="Bug 2", state=IssueState.OPEN, labels=["bug"]),
        ]
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "list"])

        assert result.exit_code == 0
        assert "Bug 1" in result.output
        assert "Bug 2" in result.output

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_fixit_list_json_format(self, mock_service_class):
        """doit fixit list --format json should output JSON."""
        mock_service = MagicMock()
        mock_service.list_bugs.return_value = [
            GitHubIssue(number=1, title="Bug 1", state=IssueState.OPEN, labels=["bug"]),
        ]
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "list", "--format", "json"])

        assert result.exit_code == 0
        # Extract JSON from output (may have additional text after)
        json_end = result.output.rfind("]") + 1
        json_str = result.output[:json_end]
        data = json.loads(json_str)
        assert len(data) == 1
        assert data[0]["number"] == 1

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_fixit_list_empty_shows_message(self, mock_service_class):
        """doit fixit list should show message when no bugs found."""
        mock_service = MagicMock()
        mock_service.list_bugs.return_value = []
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "list"])

        assert result.exit_code == 0
        assert "no open issues" in result.output.lower()


class TestFixitWorkflowInvestigateCommand:
    """Integration tests for doit fixit investigate command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_investigate_starts_investigation(self, mock_service_class):
        """doit fixit investigate should start investigation."""
        from doit_cli.models.fixit_models import InvestigationPlan, InvestigationCheckpoint, FixWorkflow

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service.get_investigation_plan.return_value = None
        mock_service.start_investigation.return_value = InvestigationPlan(
            id="inv-123",
            workflow_id="fixit-123",
            keywords=["error", "click"],
            checkpoints=[
                InvestigationCheckpoint(id="cp-1", title="Review logs"),
            ],
        )
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "investigate"])

        assert result.exit_code == 0
        assert "investigation started" in result.output.lower()

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_investigate_add_finding(self, mock_service_class):
        """doit fixit investigate -a should add finding."""
        from doit_cli.models.fixit_models import (
            InvestigationFinding, FindingType, FixWorkflow
        )

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service.add_finding.return_value = InvestigationFinding(
            id="f-123",
            finding_type=FindingType.HYPOTHESIS,
            description="Null pointer in handler",
        )
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, [
            "fixit", "investigate",
            "-a", "Null pointer in handler",
            "-t", "hypothesis"
        ])

        assert result.exit_code == 0
        assert "finding added" in result.output.lower()

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_investigate_complete_checkpoint(self, mock_service_class):
        """doit fixit investigate -c should complete checkpoint."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service.complete_checkpoint.return_value = True
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "investigate", "-c", "cp-1"])

        assert result.exit_code == 0
        assert "completed" in result.output.lower()

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_investigate_done_advances_phase(self, mock_service_class):
        """doit fixit investigate --done should complete investigation."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service.complete_investigation.return_value = True
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "investigate", "--done"])

        assert result.exit_code == 0
        assert "complete" in result.output.lower()


class TestFixitWorkflowPlanCommand:
    """Integration tests for doit fixit plan command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_plan_generate_creates_plan(self, mock_service_class):
        """doit fixit plan --generate should create fix plan."""
        from doit_cli.models.fixit_models import (
            FixPlan, PlanStatus, RiskLevel, FixWorkflow
        )

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.PLANNING,
        )
        mock_service.generate_fix_plan.return_value = FixPlan(
            id="plan-123",
            workflow_id="fixit-123",
            root_cause="Null check missing",
            proposed_solution="Add null check",
            affected_files=[],
            risk_level=RiskLevel.LOW,
            status=PlanStatus.DRAFT,
        )
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "plan", "--generate"])

        assert result.exit_code == 0
        assert "generated" in result.output.lower()

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_plan_submit_for_review(self, mock_service_class):
        """doit fixit plan --submit should submit for review."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.PLANNING,
        )
        mock_service.submit_for_review.return_value = True
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "plan", "--submit"])

        assert result.exit_code == 0
        assert "submitted" in result.output.lower()


class TestFixitWorkflowReviewCommand:
    """Integration tests for doit fixit review command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_review_approve_advances_phase(self, mock_service_class):
        """doit fixit review --approve should approve plan."""
        from doit_cli.models.fixit_models import (
            FixPlan, PlanStatus, RiskLevel, FixWorkflow
        )

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.REVIEWING,
        )
        mock_service.get_fix_plan.return_value = FixPlan(
            id="plan-123",
            workflow_id="fixit-123",
            root_cause="Null check missing",
            proposed_solution="Add null check",
            affected_files=[],
            risk_level=RiskLevel.LOW,
            status=PlanStatus.PENDING_REVIEW,
        )
        mock_service.approve_plan.return_value = True
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "review", "--approve"])

        assert result.exit_code == 0
        assert "approved" in result.output.lower()


class TestFixitWorkflowStatusCommand:
    """Integration tests for doit fixit status command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_status_shows_active_workflow(self, mock_service_class):
        """doit fixit status should show active workflow."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test-bug",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service.get_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test-bug",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "status"])

        assert result.exit_code == 0
        assert "123" in result.output

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_status_no_active_workflow(self, mock_service_class):
        """doit fixit status should show message when no workflow active."""
        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = None
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "status"])

        assert result.exit_code == 0
        assert "no active" in result.output.lower()


class TestFixitWorkflowCancelCommand:
    """Integration tests for doit fixit cancel command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_cancel_with_force_skips_confirm(self, mock_service_class):
        """doit fixit cancel --force should skip confirmation."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.get_active_workflow.return_value = FixWorkflow(
            id="fixit-123",
            issue_id=123,
            branch_name="fix/123-test",
            phase=FixPhase.INVESTIGATING,
        )
        mock_service.cancel_workflow.return_value = True
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "cancel", "--force"])

        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()


class TestFixitWorkflowWorkflowsCommand:
    """Integration tests for doit fixit workflows command."""

    @patch("doit_cli.cli.fixit_command.FixitService")
    def test_workflows_lists_all_workflows(self, mock_service_class):
        """doit fixit workflows should list all workflows."""
        from doit_cli.models.fixit_models import FixWorkflow

        mock_service = MagicMock()
        mock_service.list_workflows.return_value = [
            (123, FixWorkflow(
                id="fixit-123",
                issue_id=123,
                branch_name="fix/123-bug-a",
                phase=FixPhase.INVESTIGATING,
            )),
            (456, FixWorkflow(
                id="fixit-456",
                issue_id=456,
                branch_name="fix/456-bug-b",
                phase=FixPhase.COMPLETED,
            )),
        ]
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["fixit", "workflows"])

        assert result.exit_code == 0
        assert "#123" in result.output
        assert "#456" in result.output


class TestFixitWorkflowEndToEnd:
    """End-to-end integration tests for complete workflow."""

    @patch("doit_cli.services.fixit_service.GitHubService")
    @patch("doit_cli.services.fixit_service.StateManager")
    def test_full_workflow_lifecycle(self, mock_state_class, mock_github_class, tmp_path):
        """Test complete workflow: start → investigate → plan → complete."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.models.fixit_models import FindingType

        # Setup mocks
        mock_github = MagicMock()
        mock_github.get_issue.return_value = GitHubIssue(
            number=123,
            title="Button click error",
            body="Error when clicking submit button",
            state=IssueState.OPEN,
            labels=["bug"],
        )
        mock_github.check_branch_exists.return_value = (False, False)
        mock_github.create_branch.return_value = True
        mock_github.is_available.return_value = True
        mock_github_class.return_value = mock_github

        # Use in-memory state
        state_storage = {}
        mock_state = MagicMock()
        mock_state.load_fixit_state.side_effect = lambda issue_id: state_storage.get(issue_id)
        mock_state.save_fixit_state.side_effect = lambda data, issue_id: state_storage.__setitem__(issue_id, data)
        mock_state.get_active_fixit_workflow.side_effect = lambda: (123, state_storage[123]) if 123 in state_storage else None
        mock_state.list_fixit_states.side_effect = lambda: list(state_storage.items())
        mock_state_class.return_value = mock_state

        # Create service
        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        # Phase 1: Start workflow
        workflow = service.start_workflow(issue_id=123)
        assert workflow.issue_id == 123
        assert workflow.phase == FixPhase.INVESTIGATING
        assert "fix/123-" in workflow.branch_name

        # Phase 2: Start investigation
        plan = service.start_investigation(issue_id=123)
        assert plan is not None
        assert len(plan.checkpoints) > 0

        # Phase 3: Add findings
        finding1 = service.add_finding(
            issue_id=123,
            finding_type=FindingType.HYPOTHESIS,
            description="Click handler may have null reference",
        )
        assert finding1 is not None

        finding2 = service.add_finding(
            issue_id=123,
            finding_type=FindingType.CONFIRMED_CAUSE,
            description="Null check missing in button click handler",
            file_path="src/handlers/button.py",
        )
        assert finding2 is not None

        # Phase 4: Complete investigation
        success = service.complete_investigation(issue_id=123)
        assert success is True

        # Check phase advanced
        workflow = service.get_workflow(123)
        assert workflow.phase == FixPhase.PLANNING

        # Phase 5: Generate fix plan
        fix_plan = service.generate_fix_plan(issue_id=123)
        assert fix_plan is not None
        assert "null" in fix_plan.root_cause.lower()

        # Phase 6: Submit for review
        success = service.submit_for_review(issue_id=123)
        assert success is True

        workflow = service.get_workflow(123)
        assert workflow.phase == FixPhase.REVIEWING

        # Phase 7: Approve plan
        success = service.approve_plan(issue_id=123)
        assert success is True

        workflow = service.get_workflow(123)
        assert workflow.phase == FixPhase.APPROVED

        # Phase 8: Complete workflow
        success = service.complete_workflow(issue_id=123, close_issue=False)
        assert success is True

        workflow = service.get_workflow(123)
        assert workflow.phase == FixPhase.COMPLETED

    @patch("doit_cli.services.fixit_service.GitHubService")
    @patch("doit_cli.services.fixit_service.StateManager")
    def test_workflow_cancel(self, mock_state_class, mock_github_class):
        """Test workflow cancellation."""
        from doit_cli.services.fixit_service import FixitService

        # Setup mocks
        mock_github = MagicMock()
        mock_github.get_issue.return_value = GitHubIssue(
            number=456,
            title="Another bug",
            state=IssueState.OPEN,
            labels=["bug"],
        )
        mock_github.check_branch_exists.return_value = (False, False)
        mock_github.create_branch.return_value = True
        mock_github.is_available.return_value = True
        mock_github_class.return_value = mock_github

        state_storage = {}
        mock_state = MagicMock()
        mock_state.load_fixit_state.side_effect = lambda issue_id: state_storage.get(issue_id)
        mock_state.save_fixit_state.side_effect = lambda data, issue_id: state_storage.__setitem__(issue_id, data)
        mock_state_class.return_value = mock_state

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        # Start and cancel
        workflow = service.start_workflow(issue_id=456)
        assert workflow.phase == FixPhase.INVESTIGATING

        success = service.cancel_workflow(issue_id=456)
        assert success is True

        workflow = service.get_workflow(456)
        assert workflow.phase == FixPhase.CANCELLED

    @patch("doit_cli.services.fixit_service.GitHubService")
    @patch("doit_cli.services.fixit_service.StateManager")
    def test_investigation_requires_confirmed_cause(self, mock_state_class, mock_github_class):
        """Test that investigation cannot complete without confirmed cause."""
        from doit_cli.services.fixit_service import FixitService
        from doit_cli.models.fixit_models import FindingType

        # Setup mocks
        mock_github = MagicMock()
        mock_github.get_issue.return_value = GitHubIssue(
            number=789,
            title="Test bug",
            state=IssueState.OPEN,
            labels=["bug"],
        )
        mock_github.check_branch_exists.return_value = (False, False)
        mock_github.create_branch.return_value = True
        mock_github.is_available.return_value = True
        mock_github_class.return_value = mock_github

        state_storage = {}
        mock_state = MagicMock()
        mock_state.load_fixit_state.side_effect = lambda issue_id: state_storage.get(issue_id)
        mock_state.save_fixit_state.side_effect = lambda data, issue_id: state_storage.__setitem__(issue_id, data)
        mock_state_class.return_value = mock_state

        service = FixitService(
            github_service=mock_github,
            state_manager=mock_state,
        )

        # Start workflow and investigation
        service.start_workflow(issue_id=789)
        service.start_investigation(issue_id=789)

        # Add only hypothesis (not confirmed_cause)
        service.add_finding(
            issue_id=789,
            finding_type=FindingType.HYPOTHESIS,
            description="Maybe this is the cause",
        )

        # Try to complete - should fail
        success = service.complete_investigation(issue_id=789)
        assert success is False

        # Workflow should still be in investigating phase
        workflow = service.get_workflow(789)
        assert workflow.phase == FixPhase.INVESTIGATING
