# Interactive Guided Workflows

**Completed**: 2026-01-16
**Branch**: `030-guided-workflows`
**Epic**: #278

## Overview

This feature adds interactive guided workflows to the doit CLI, providing step-by-step guidance through command execution with real-time validation, progress visualization, workflow recovery, and non-interactive mode support.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Detect interactive terminal and enable guided mode | Done |
| FR-002 | Provide step-by-step prompts for commands requiring input | Done |
| FR-003 | Validate inputs at each step before proceeding | Done |
| FR-004 | Display clear error messages with correction guidance | Done |
| FR-005 | Show progress indicator for multi-step workflows | Done |
| FR-006 | Allow back navigation using 'back' command | Done |
| FR-007 | Allow skipping optional steps with 'skip' or Enter | Done |
| FR-008 | Save workflow state when interrupted | Done |
| FR-009 | Offer to resume interrupted workflows | Done |
| FR-010 | Support `--non-interactive` flag | Done |
| FR-011 | Detect non-TTY and auto-switch to non-interactive | Done |
| FR-012 | Support `DOIT_NON_INTERACTIVE` environment variable | Done |
| FR-013 | Provide sensible defaults for optional inputs | Done |
| FR-014 | Validate prerequisites at workflow start | Done |
| FR-015 | Provide helpful hints and examples in prompts | Done |

## User Stories Delivered

1. **US1 - Step-by-Step Command Guidance** (P1): Interactive prompts guide users through each required input
2. **US2 - Real-Time Input Validation** (P1): Immediate feedback on invalid inputs with suggestions
3. **US3 - Progress Visualization** (P2): Visual progress indicator showing current step and completion percentage
4. **US4 - Workflow Recovery** (P2): Save and resume interrupted workflows via Ctrl+C handling
5. **US5 - Non-Interactive Mode** (P3): Support for CI/CD automation via flags and environment variables

## Technical Details

### Architecture

The guided workflow system consists of:

- **WorkflowEngine**: Orchestrates workflow execution, handles navigation, manages state
- **InteractivePrompt**: Collects user input with validation support
- **ProgressDisplay**: Shows step progress with checkmarks and percentages
- **StateManager**: Persists workflow state to JSON files for recovery
- **InputValidator**: Extensible validation framework with built-in validators

### Key Design Decisions

1. **Protocol-based validators**: Allows custom validators via registry pattern
2. **File-based state persistence**: Simple JSON files in `.doit/state/` for recovery
3. **Navigation via exceptions**: `NavigationCommand` exceptions for clean control flow
4. **TTY detection + env var**: Multiple ways to enable non-interactive mode

## Files Changed

### New Files Created

- `src/doit_cli/models/workflow_models.py` - Core dataclasses and exceptions
- `src/doit_cli/prompts/interactive.py` - InteractivePrompt and ProgressDisplay
- `src/doit_cli/services/input_validator.py` - Validation framework
- `src/doit_cli/services/workflow_engine.py` - Workflow orchestration
- `src/doit_cli/services/state_manager.py` - State persistence
- `src/doit_cli/cli/workflow_mixin.py` - CLI integration helpers

### Test Files

- `tests/unit/test_interactive_prompt.py` - 18 tests
- `tests/unit/test_input_validator.py` - 26 tests
- `tests/unit/test_workflow_engine.py` - 23 tests
- `tests/unit/test_progress_display.py` - 17 tests
- `tests/unit/test_state_manager.py` - 24 tests
- `tests/unit/test_non_interactive.py` - 24 tests
- `tests/integration/test_guided_workflows.py` - 10 tests
- `tests/contract/test_workflow_contracts.py` - 18 tests

## Testing

- **Automated tests**: 160 tests passing
- **Test coverage**: Unit, integration, and contract tests

## Related Issues

- Epic: #278
- Features: #279, #280, #281, #282, #283
- Tasks: #284-#315, #318-#319 (34 completed)
- Deferred: #316 (T033), #317 (T034)

## Usage Example

```python
from doit_cli.models import Workflow, WorkflowStep
from doit_cli.services import WorkflowEngine

# Define a workflow
workflow = Workflow(
    id="init-workflow",
    command_name="init",
    description="Initialize a new project",
    interactive=True,
    steps=[
        WorkflowStep(
            id="project-name",
            name="Project Name",
            prompt_text="Enter your project name:",
            required=True,
            order=0,
        ),
        WorkflowStep(
            id="description",
            name="Description",
            prompt_text="Enter project description:",
            required=False,
            order=1,
            default_value="A doit project",
        ),
    ],
)

# Run the workflow
engine = WorkflowEngine()
results = engine.run(workflow)
# results = {"project-name": "my-app", "description": "My application"}
```

## Non-Interactive Mode

```bash
# Via flag
doit init --non-interactive

# Via environment variable
DOIT_NON_INTERACTIVE=true doit init

# Via piped input (auto-detected)
echo "my-project" | doit init
```
