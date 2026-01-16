# Tutorial: Creating Custom Workflows

**Feature**: 030-guided-workflows
**Last Updated**: 2026-01-16

## Introduction

This tutorial walks through creating a custom workflow for a doit CLI command. By the end, you'll understand how to define workflow steps, integrate with the WorkflowEngine, and handle responses.

## Prerequisites

- Python 3.11+
- Understanding of doit CLI structure
- Familiarity with dataclasses

## Step 1: Define Your Workflow

First, create a factory function that returns a `Workflow` instance:

```python
from pathlib import Path
from doit_cli.models.workflow_models import Workflow, WorkflowStep

def create_deploy_workflow(environment: str) -> Workflow:
    """Create a deployment workflow definition."""
    return Workflow(
        id="deploy-workflow",
        command_name="deploy",
        description="Deploy application to target environment",
        interactive=True,
        steps=[
            WorkflowStep(
                id="confirm-env",
                name="Confirm Environment",
                prompt_text=f"Deploy to {environment}?",
                required=True,
                order=0,
                default_value="yes",
                options={"yes": "Confirm", "no": "Cancel"},
            ),
            WorkflowStep(
                id="select-version",
                name="Select Version",
                prompt_text="Which version to deploy?",
                required=True,
                order=1,
                validation_type="NonEmptyValidator",
                default_value="latest",
            ),
            WorkflowStep(
                id="dry-run",
                name="Dry Run",
                prompt_text="Perform dry run first?",
                required=False,
                order=2,
                default_value="yes",
                options={"yes": "Yes", "no": "No"},
            ),
        ],
    )
```

### Key Points

- **id**: Unique identifier for the workflow
- **command_name**: CLI command this workflow belongs to
- **steps**: Ordered list of steps (use `order` field for sequencing)
- **required=False**: Makes a step optional (user can skip)

## Step 2: Integrate with Your Command

Modify your command function to use the workflow:

```python
from rich.console import Console
from doit_cli.services.workflow_engine import WorkflowEngine
from doit_cli.services.state_manager import StateManager

console = Console()

def deploy_command(
    environment: str,
    yes: bool = False,
) -> None:
    """Deploy application to environment."""

    # Non-interactive mode: bypass workflow
    if yes:
        run_deploy(environment, version="latest", dry_run=False)
        return

    # Interactive mode: use workflow
    workflow = create_deploy_workflow(environment)
    engine = WorkflowEngine(
        console=console,
        state_manager=StateManager(),
    )

    try:
        responses = engine.run(workflow)
    except KeyboardInterrupt:
        raise typer.Exit(130)

    # Handle cancellation
    if responses.get("confirm-env") == "no":
        console.print("[yellow]Deployment cancelled.[/yellow]")
        raise typer.Exit(0)

    # Map responses to parameters
    version = responses.get("select-version", "latest")
    dry_run = responses.get("dry-run", "yes") == "yes"

    # Execute deployment
    run_deploy(environment, version, dry_run)
```

## Step 3: Add Validation

For steps requiring input validation, specify a validator type:

```python
WorkflowStep(
    id="config-path",
    name="Configuration File",
    prompt_text="Path to deployment config:",
    required=True,
    order=3,
    validation_type="PathExistsValidator",
    default_value="./deploy.yaml",
)
```

### Available Validators

| Validator | Use Case |
| --------- | -------- |
| `ChoiceValidator` | Limit to specific options |
| `PathExistsValidator` | Verify file/directory exists |
| `DirectoryValidator` | Verify is a directory |
| `NonEmptyValidator` | Require non-empty input |

## Step 4: Handle Responses

The `engine.run()` method returns a dictionary mapping step IDs to response values:

```python
responses = engine.run(workflow)
# {
#     "confirm-env": "yes",
#     "select-version": "v1.2.3",
#     "dry-run": "yes",
# }
```

Create a helper function to map responses to your command's parameters:

```python
def map_deploy_responses(responses: dict) -> dict:
    """Map workflow responses to deploy parameters."""
    return {
        "version": responses.get("select-version", "latest"),
        "dry_run": responses.get("dry-run", "yes") == "yes",
    }
```

## Step 5: Test Your Workflow

Write tests for both the workflow definition and integration:

```python
import pytest
from your_module import create_deploy_workflow

class TestDeployWorkflow:
    def test_has_three_steps(self):
        workflow = create_deploy_workflow("production")
        assert len(workflow.steps) == 3

    def test_environment_in_prompt(self):
        workflow = create_deploy_workflow("staging")
        step = workflow.get_step_by_id("confirm-env")
        assert "staging" in step.prompt_text

    def test_optional_step_has_default(self):
        workflow = create_deploy_workflow("dev")
        step = workflow.get_step_by_id("dry-run")
        assert step.required is False
        assert step.default_value == "yes"
```

## Complete Example

Here's the full implementation:

```python
"""Deploy command with workflow integration."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from doit_cli.models.workflow_models import Workflow, WorkflowStep
from doit_cli.services.workflow_engine import WorkflowEngine
from doit_cli.services.state_manager import StateManager

console = Console()


def create_deploy_workflow(environment: str) -> Workflow:
    """Create the deploy workflow definition."""
    return Workflow(
        id="deploy-workflow",
        command_name="deploy",
        description="Deploy application to target environment",
        interactive=True,
        steps=[
            WorkflowStep(
                id="confirm-env",
                name="Confirm Environment",
                prompt_text=f"Deploy to {environment}?",
                required=True,
                order=0,
                default_value="yes",
                options={"yes": "Confirm", "no": "Cancel"},
            ),
            WorkflowStep(
                id="select-version",
                name="Select Version",
                prompt_text="Which version to deploy?",
                required=True,
                order=1,
                validation_type="NonEmptyValidator",
                default_value="latest",
            ),
            WorkflowStep(
                id="dry-run",
                name="Dry Run",
                prompt_text="Perform dry run first?",
                required=False,
                order=2,
                default_value="yes",
                options={"yes": "Yes", "no": "No"},
            ),
        ],
    )


def deploy_command(
    environment: Annotated[str, typer.Argument(help="Target environment")],
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    """Deploy application to environment."""

    if yes:
        console.print(f"Deploying latest to {environment}...")
        return

    workflow = create_deploy_workflow(environment)
    engine = WorkflowEngine(
        console=console,
        state_manager=StateManager(),
    )

    try:
        responses = engine.run(workflow)
    except KeyboardInterrupt:
        raise typer.Exit(130)

    if responses.get("confirm-env") == "no":
        console.print("[yellow]Deployment cancelled.[/yellow]")
        raise typer.Exit(0)

    version = responses.get("select-version", "latest")
    dry_run = responses.get("dry-run", "yes") == "yes"

    if dry_run:
        console.print(f"[cyan]DRY RUN:[/cyan] Would deploy {version} to {environment}")
    else:
        console.print(f"[green]Deploying {version} to {environment}...[/green]")
```

## Next Steps

- Read the [Workflow System Guide](../guides/workflow-system-guide.md) for detailed API reference
- Review the init command implementation for a real-world example
- Add custom validators for your specific validation needs
