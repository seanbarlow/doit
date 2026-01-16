# Contract: Init Workflow Integration

**Feature**: 031-init-workflow-integration
**Date**: 2026-01-16
**Version**: 1.0.0

## Overview

This contract defines the interface for integrating the init command with the guided workflow system.

## Public Interface

### InitWorkflow Factory

```python
def create_init_workflow(path: Path) -> Workflow:
    """Create the init workflow definition.

    Args:
        path: Target project directory path

    Returns:
        Workflow instance configured for init command

    Example:
        workflow = create_init_workflow(Path("."))
        responses = engine.run(workflow)
    """
```

### Integration with init_command

```python
def init_command(
    path: Path = Path("."),
    agent: str | None = None,
    templates: Path | None = None,
    update: bool = False,
    force: bool = False,
    yes: bool = False,
) -> None:
    """Initialize a new doit project.

    When `yes=False` (interactive mode):
        Uses WorkflowEngine to guide user through steps

    When `yes=True` (non-interactive mode):
        Bypasses workflow, uses defaults/auto-detection

    Args:
        path: Project directory path
        agent: Target agent(s) override
        templates: Custom template directory
        update: Update existing project
        force: Overwrite without backup
        yes: Skip all prompts
    """
```

## Workflow Steps Contract

### Step 1: select-agent

| Aspect | Specification |
| ------ | ------------- |
| Input | Choice selection from options |
| Options | "claude", "copilot", "both" |
| Validation | Must be one of options |
| Default | "claude" |
| Output | Selected agent string |

### Step 2: confirm-path

| Aspect | Specification |
| ------ | ------------- |
| Input | Confirmation (yes/no) |
| Prompt | Dynamic, includes actual path |
| Validation | None (confirmation only) |
| Default | "yes" |
| Output | "yes" or "no" |

**Behavior on "no"**: Workflow raises `WorkflowError` and init aborts.

### Step 3: custom-templates (Optional)

| Aspect | Specification |
| ------ | ------------- |
| Input | Path string or empty |
| Validation | PathExistsValidator if non-empty |
| Default | "" (empty string) |
| Skippable | Yes |
| Output | Path string or empty |

## Response Mapping

Workflow responses are mapped to init parameters:

| Response Key | Init Parameter | Transformation |
| ------------ | -------------- | -------------- |
| select-agent | agents | parse_agent_string(value) |
| confirm-path | (abort if "no") | None |
| custom-templates | template_source | Path(value) if value else None |

```python
def map_workflow_responses(responses: dict) -> dict:
    """Map workflow responses to init parameters.

    Args:
        responses: Dict from WorkflowEngine.run()

    Returns:
        Dict with keys: agents, template_source

    Raises:
        WorkflowError: If confirm-path is "no"
    """
```

## Non-Interactive Mode Contract

When `--yes` flag is provided:

1. **Skip WorkflowEngine entirely**
2. **Agent selection**:
   - If `--agent` provided: Use specified agent
   - Else: Auto-detect using AgentDetector
   - Fallback: Default to Claude
3. **Path confirmation**: Implicit yes
4. **Custom templates**:
   - If `--templates` provided: Use specified path
   - Else: Use bundled templates

```python
def run_non_interactive(
    path: Path,
    agent: str | None,
    templates: Path | None,
) -> dict:
    """Execute init without workflow prompts.

    Returns:
        Dict matching workflow response structure
    """
```

## Error Handling

| Error Condition | Exception | Behavior |
| --------------- | --------- | -------- |
| User cancels (Ctrl+C) | KeyboardInterrupt | Save state, show resume message |
| User declines path | WorkflowError | Abort init, exit code 1 |
| Invalid agent choice | ValidationError | Re-prompt with error message |
| Invalid template path | ValidationError | Re-prompt with error message |
| State corruption | StateCorruptionError | Offer to start fresh |

## Testing Contract

### Unit Tests

```python
class TestInitWorkflow:
    def test_workflow_has_three_steps(self):
        """InitWorkflow must have exactly 3 steps."""

    def test_step_order_is_sequential(self):
        """Steps must have order 0, 1, 2."""

    def test_agent_selection_has_valid_options(self):
        """Agent step must have claude, copilot, both options."""

    def test_optional_step_has_default(self):
        """custom-templates step must have empty default."""
```

### Integration Tests

```python
class TestInitWorkflowIntegration:
    def test_interactive_init_shows_progress(self):
        """doit init . must show step progress."""

    def test_back_navigation_returns_to_previous(self):
        """Typing 'back' must return to previous step."""

    def test_non_interactive_bypasses_workflow(self):
        """doit init . --yes must not show prompts."""

    def test_interrupt_saves_state(self):
        """Ctrl+C must save state for resume."""

    def test_resume_continues_from_saved_step(self):
        """Resume must start from interrupted step."""
```

## Compatibility

- **Backward Compatible**: All existing `doit init` flags continue to work
- **New Behavior**: Interactive mode now uses WorkflowEngine
- **Breaking Changes**: None
