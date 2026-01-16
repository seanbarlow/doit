# Quickstart: Init Workflow Integration

**Feature**: 031-init-workflow-integration
**Date**: 2026-01-16

## Overview

This guide walks through implementing the init workflow integration step by step.

## Prerequisites

- Feature 030 (Guided Workflows) merged and available
- Understanding of existing `init_command.py` structure
- Familiarity with `Workflow` and `WorkflowStep` dataclasses

## Implementation Steps

### Step 1: Create InitWorkflow Factory

**File**: `src/doit_cli/cli/init_command.py`

Add the workflow factory function:

```python
from ..models.workflow_models import Workflow, WorkflowStep

def create_init_workflow(path: Path) -> Workflow:
    """Create the init workflow definition."""
    return Workflow(
        id="init-workflow",
        command_name="init",
        description="Initialize a new doit project",
        interactive=True,
        steps=[
            WorkflowStep(
                id="select-agent",
                name="Select AI Agent",
                prompt_text="Which AI agent(s) do you want to initialize for?",
                required=True,
                order=0,
                validation_type="ChoiceValidator",
                default_value="claude",
                options={
                    "claude": "Claude Code",
                    "copilot": "GitHub Copilot",
                    "both": "Both agents",
                },
            ),
            WorkflowStep(
                id="confirm-path",
                name="Confirm Project Path",
                prompt_text=f"Initialize doit in '{path}'?",
                required=True,
                order=1,
                default_value="yes",
                options={"yes": "Confirm", "no": "Cancel"},
            ),
            WorkflowStep(
                id="custom-templates",
                name="Custom Templates",
                prompt_text="Custom template directory (leave empty for default)",
                required=False,
                order=2,
                validation_type="PathExistsValidator",
                default_value="",
            ),
        ],
    )
```

### Step 2: Integrate with init_command

Modify the main `init_command` function:

```python
from ..services.workflow_engine import WorkflowEngine
from ..services.state_manager import StateManager

def init_command(
    path: Path = Path("."),
    agent: str | None = None,
    templates: Path | None = None,
    update: bool = False,
    force: bool = False,
    yes: bool = False,
) -> None:
    """Initialize a new doit project."""
    # Non-interactive mode: bypass workflow
    if yes:
        result = run_init(
            path=path,
            agents=parse_agent_string(agent) if agent else None,
            update=update,
            force=force,
            yes=True,
            template_source=templates,
        )
        display_init_result(result, result.project.agents or [Agent.CLAUDE])
        return

    # Interactive mode: use workflow
    workflow = create_init_workflow(path)
    engine = WorkflowEngine(
        console=console,
        state_manager=StateManager(),
    )

    try:
        responses = engine.run(workflow)
    except KeyboardInterrupt:
        raise typer.Exit(130)

    # Map responses to init parameters
    if responses.get("confirm-path") == "no":
        console.print("[yellow]Initialization cancelled.[/yellow]")
        raise typer.Exit(0)

    agents = parse_agent_string(responses["select-agent"])
    template_source = Path(responses["custom-templates"]) if responses.get("custom-templates") else templates

    # Execute init with workflow responses
    result = run_init(
        path=path,
        agents=agents,
        update=update,
        force=force,
        yes=False,
        template_source=template_source,
    )

    display_init_result(result, agents)
```

### Step 3: Update Tests

**File**: `tests/unit/test_init_workflow.py`

```python
import pytest
from pathlib import Path
from src.doit_cli.cli.init_command import create_init_workflow

class TestCreateInitWorkflow:
    def test_creates_workflow_with_three_steps(self):
        workflow = create_init_workflow(Path("."))
        assert len(workflow.steps) == 3

    def test_step_ids_are_unique(self):
        workflow = create_init_workflow(Path("."))
        ids = [s.id for s in workflow.steps]
        assert len(ids) == len(set(ids))

    def test_first_step_is_agent_selection(self):
        workflow = create_init_workflow(Path("."))
        step = workflow.get_step_by_order(0)
        assert step.id == "select-agent"
        assert "claude" in step.options

    def test_path_included_in_confirm_prompt(self):
        workflow = create_init_workflow(Path("/test/path"))
        step = workflow.get_step_by_order(1)
        assert "/test/path" in step.prompt_text
```

**File**: `tests/integration/test_init_workflow_integration.py`

```python
import pytest
from typer.testing import CliRunner
from src.doit_cli.main import app

runner = CliRunner()

class TestInitWorkflowIntegration:
    def test_non_interactive_skips_prompts(self, tmp_path):
        result = runner.invoke(app, ["init", str(tmp_path), "--yes"])
        assert result.exit_code == 0
        assert "Step" not in result.output  # No workflow progress

    def test_interactive_shows_progress(self, tmp_path, monkeypatch):
        # Mock stdin to provide responses
        inputs = iter(["claude", "yes", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = runner.invoke(app, ["init", str(tmp_path)])
        # Check for workflow elements in output
        assert "Select AI Agent" in result.output or result.exit_code == 0
```

### Step 4: Create Documentation

**File**: `docs/guides/workflow-system-guide.md`

See the documentation template in the contracts folder for content structure.

## Verification Checklist

- [ ] `doit init .` shows step progress (Step 1/3, etc.)
- [ ] User can type "back" to return to previous step
- [ ] `doit init . --yes` completes without prompts
- [ ] Ctrl+C saves state, next run offers resume
- [ ] All existing init tests pass
- [ ] New workflow tests pass

## Common Issues

### Issue: Workflow not showing progress

**Cause**: TTY detection returning False
**Solution**: Check `InteractivePrompt._is_interactive()` and ensure terminal supports TTY

### Issue: State not persisting

**Cause**: StateManager not passed to WorkflowEngine
**Solution**: Ensure `StateManager()` is instantiated and passed to engine

### Issue: Back navigation not working

**Cause**: NavigationCommand not being caught
**Solution**: Ensure WorkflowEngine._handle_navigation is called

## Next Steps

After implementation:

1. Run `pytest tests/unit/test_init_workflow.py`
2. Run `pytest tests/integration/test_init_workflow_integration.py`
3. Manual testing: `doit init .` in a test directory
4. Create documentation files
5. Run `/doit.reviewit` for code review
