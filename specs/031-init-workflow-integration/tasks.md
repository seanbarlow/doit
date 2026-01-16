# Tasks: Init Workflow Integration

**Feature**: 031-init-workflow-integration
**Generated**: 2026-01-16
**Source**: [plan.md](./plan.md) | [spec.md](./spec.md)

## Task Summary

| Phase | Tasks | Est. Complexity |
| ----- | ----- | --------------- |
| Setup | 2 | Low |
| Foundation | 3 | Low |
| US1: Interactive Init | 5 | Medium |
| US2: Non-Interactive Mode | 3 | Low |
| US3: Enhanced Progress | 4 | Medium |
| US4: Documentation | 4 | Medium |
| US5: State Recovery | 4 | Medium |
| Polish | 3 | Low |
| **Total** | **28** | |

## Task Dependency Graph

<!-- BEGIN:AUTO-GENERATED section="task-dependencies" -->
```mermaid
flowchart TB
    subgraph Setup["Phase 1: Setup"]
        T01[T01: Create feature branch]
        T02[T02: Verify Feature 030 available]
    end

    subgraph Foundation["Phase 2: Foundation"]
        T03[T03: Create InitWorkflow factory]
        T04[T04: Add workflow imports]
        T05[T05: Create test scaffolding]
    end

    subgraph US1["Phase 3: US1 - Interactive Init"]
        T06[T06: Implement 3 workflow steps]
        T07[T07: Integrate WorkflowEngine]
        T08[T08: Map responses to init params]
        T09[T09: Handle workflow cancellation]
        T10[T10: Unit tests for workflow]
    end

    subgraph US2["Phase 4: US2 - Non-Interactive"]
        T11[T11: Bypass workflow with --yes]
        T12[T12: Use defaults/auto-detect]
        T13[T13: Non-interactive tests]
    end

    subgraph US3["Phase 5: US3 - Progress Display"]
        T14[T14: Add step counter]
        T15[T15: Show navigation hints]
        T16[T16: Display step names]
        T17[T17: Progress display tests]
    end

    subgraph US4["Phase 6: US4 - Documentation"]
        T18[T18: Create workflow guide]
        T19[T19: Create tutorials]
        T20[T20: Add API reference]
        T21[T21: Update README]
    end

    subgraph US5["Phase 7: US5 - State Recovery"]
        T22[T22: Save state on interrupt]
        T23[T23: Prompt resume on restart]
        T24[T24: Clean state on complete]
        T25[T25: State recovery tests]
    end

    subgraph Polish["Phase 8: Polish"]
        T26[T26: Integration tests]
        T27[T27: Manual testing]
        T28[T28: Final review]
    end

    T01 --> T02
    T02 --> T03
    T02 --> T04
    T02 --> T05
    T03 --> T06
    T04 --> T07
    T06 --> T07
    T07 --> T08
    T08 --> T09
    T05 --> T10
    T09 --> T10
    T07 --> T11
    T11 --> T12
    T12 --> T13
    T07 --> T14
    T14 --> T15
    T15 --> T16
    T16 --> T17
    T10 --> T18
    T13 --> T18
    T18 --> T19
    T19 --> T20
    T20 --> T21
    T07 --> T22
    T22 --> T23
    T23 --> T24
    T24 --> T25
    T17 --> T26
    T25 --> T26
    T21 --> T26
    T26 --> T27
    T27 --> T28
```
<!-- END:AUTO-GENERATED -->

## Phase Timeline

<!-- BEGIN:AUTO-GENERATED section="phase-timeline" -->
```mermaid
gantt
    title Feature 031 Implementation Phases
    dateFormat YYYY-MM-DD

    section Setup
    Create feature branch       :t01, 2026-01-16, 1d
    Verify Feature 030          :t02, after t01, 1d

    section Foundation
    Create InitWorkflow factory :t03, after t02, 1d
    Add workflow imports        :t04, after t02, 1d
    Create test scaffolding     :t05, after t02, 1d

    section US1 Interactive
    Implement workflow steps    :t06, after t03, 1d
    Integrate WorkflowEngine    :t07, after t06, 1d
    Map responses              :t08, after t07, 1d
    Handle cancellation        :t09, after t08, 1d
    Unit tests                 :t10, after t09, 1d

    section US2 Non-Interactive
    Bypass with --yes          :t11, after t07, 1d
    Use defaults               :t12, after t11, 1d
    Non-interactive tests      :t13, after t12, 1d

    section US3 Progress
    Add step counter           :t14, after t07, 1d
    Show navigation hints      :t15, after t14, 1d
    Display step names         :t16, after t15, 1d
    Progress tests             :t17, after t16, 1d

    section US4 Documentation
    Create workflow guide      :t18, after t13, 1d
    Create tutorials           :t19, after t18, 1d
    Add API reference          :t20, after t19, 1d
    Update README              :t21, after t20, 1d

    section US5 State Recovery
    Save state on interrupt    :t22, after t07, 1d
    Prompt resume              :t23, after t22, 1d
    Clean state                :t24, after t23, 1d
    State tests                :t25, after t24, 1d

    section Polish
    Integration tests          :t26, after t25, 1d
    Manual testing             :t27, after t26, 1d
    Final review               :t28, after t27, 1d
```
<!-- END:AUTO-GENERATED -->

---

## Phase 1: Setup

### T01: Create Feature Branch

- **Status**: [X] Complete
- **Parent**: Epic #321
- **Depends On**: None

**Description**: Create the feature branch for init workflow integration.

**Acceptance Criteria**:
- [X] Branch `031-init-workflow-integration` created from main
- [X] Branch pushed to remote

**Files**: None (git operations only)

---

### T02: Verify Feature 030 Available

- **Status**: [X] Complete
- **Parent**: Epic #321
- **Depends On**: T01

**Description**: Verify that Feature 030 (Guided Workflows) code is available on main branch.

**Acceptance Criteria**:
- [X] `WorkflowEngine` class exists in `src/doit_cli/services/workflow_engine.py`
- [X] `StateManager` class exists in `src/doit_cli/services/state_manager.py`
- [X] `Workflow` and `WorkflowStep` dataclasses exist in `src/doit_cli/models/workflow_models.py`
- [X] All imports resolve without error

**Files**:
- `src/doit_cli/services/workflow_engine.py` (verify exists)
- `src/doit_cli/services/state_manager.py` (verify exists)
- `src/doit_cli/models/workflow_models.py` (verify exists)

---

## Phase 2: Foundation

### T03: Create InitWorkflow Factory Function

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T02
- **Contract**: [init-workflow.md](./contracts/init-workflow.md)

**Description**: Create the `create_init_workflow(path)` factory function that returns the InitWorkflow definition with 3 steps.

**Acceptance Criteria**:
- [X] Function `create_init_workflow(path: Path) -> Workflow` created
- [X] Returns workflow with id="init-workflow"
- [X] Contains 3 steps: select-agent, confirm-path, custom-templates
- [X] Step order is 0, 1, 2
- [X] Agent selection has options: claude, copilot, both

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

**Code Reference**:
```python
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
            # ... remaining steps
        ],
    )
```

---

### T04: Add Workflow Imports to init_command.py

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T02

**Description**: Add necessary imports for workflow integration.

**Acceptance Criteria**:
- [X] Import `Workflow`, `WorkflowStep` from workflow_models
- [X] Import `WorkflowEngine` from workflow_engine
- [X] Import `StateManager` from state_manager
- [X] No import errors when module loads

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

---

### T05: Create Test Scaffolding

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T02

**Description**: Create test file structure for init workflow tests.

**Acceptance Criteria**:
- [X] `tests/unit/test_init_workflow.py` created with TestCreateInitWorkflow class
- [X] `tests/integration/test_init_workflow_integration.py` created with TestInitWorkflowIntegration class
- [X] Basic test imports working
- [X] pytest discovers new test files

**Files**:
- `tests/unit/test_init_workflow.py` (create)
- `tests/integration/test_init_workflow_integration.py` (create)

---

## Phase 3: US1 - Interactive Init with WorkflowEngine (P1)

> **User Story**: As a developer, I want the init command to use the guided workflow system so that I have a consistent, step-by-step initialization experience.

### T06: Implement Three Workflow Steps

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T03
- **Requirements**: FR-001, FR-002, FR-003, FR-004

**Description**: Implement all three workflow steps with proper configuration.

**Acceptance Criteria**:
- [X] Step 1 (select-agent): Choice validator with claude/copilot/both options
- [X] Step 2 (confirm-path): Includes actual path in prompt text
- [X] Step 3 (custom-templates): Optional step with PathExistsValidator
- [X] All steps have unique IDs
- [X] All steps have sequential order (0, 1, 2)

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

---

### T07: Integrate WorkflowEngine into init_command

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T04, T06
- **Requirements**: FR-005

**Description**: Modify init_command to use WorkflowEngine for interactive mode.

**Acceptance Criteria**:
- [X] WorkflowEngine instantiated with console and StateManager
- [X] `engine.run(workflow)` called for interactive mode
- [X] Responses dict returned from engine
- [X] KeyboardInterrupt caught and exits with code 130

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

**Code Reference**:
```python
workflow = create_init_workflow(path)
engine = WorkflowEngine(
    console=console,
    state_manager=StateManager(),
)
try:
    responses = engine.run(workflow)
except KeyboardInterrupt:
    raise typer.Exit(130)
```

---

### T08: Map Workflow Responses to Init Parameters

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T07
- **Requirements**: FR-006

**Description**: Convert workflow responses dict to init function parameters.

**Acceptance Criteria**:
- [X] `select-agent` response mapped to agents list via `parse_agent_string()`
- [X] `confirm-path` = "no" causes graceful abort with exit code 0
- [X] `custom-templates` response mapped to template_source Path (or None if empty)
- [X] Init function called with mapped parameters

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

---

### T09: Handle Workflow Cancellation

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T08
- **Requirements**: FR-007

**Description**: Handle user cancellation during workflow (confirm-path = "no").

**Acceptance Criteria**:
- [X] When confirm-path is "no", display yellow cancellation message
- [X] Exit with code 0 (not error)
- [X] No init operations performed
- [X] State cleaned up

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

---

### T10: Unit Tests for InitWorkflow

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T05, T09
- **Contract**: Testing Contract in [init-workflow.md](./contracts/init-workflow.md)

**Description**: Implement unit tests for the InitWorkflow factory and response mapping.

**Acceptance Criteria**:
- [X] `test_workflow_has_three_steps` passes
- [X] `test_step_order_is_sequential` passes
- [X] `test_agent_selection_has_valid_options` passes
- [X] `test_optional_step_has_default` passes
- [X] `test_path_included_in_confirm_prompt` passes
- [X] All tests in `tests/unit/test_init_workflow.py` pass

**Files**:
- `tests/unit/test_init_workflow.py` (modify)

---

## Phase 4: US2 - Non-Interactive Mode (P1)

> **User Story**: As a CI/CD pipeline, I want to run init with --yes flag to skip prompts so that automated setups complete without human intervention.

### T11: Bypass Workflow When --yes Flag Set

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T07
- **Requirements**: FR-008

**Description**: Skip WorkflowEngine entirely when --yes flag is provided.

**Acceptance Criteria**:
- [X] `if yes:` check at start of init_command
- [X] WorkflowEngine NOT instantiated when yes=True
- [X] Direct call to `run_init()` with defaults
- [X] No prompts displayed

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

---

### T12: Use Defaults and Auto-Detection for Non-Interactive

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T11
- **Requirements**: FR-009, FR-010

**Description**: Implement default value logic for non-interactive mode.

**Acceptance Criteria**:
- [X] Agent defaults to CLI arg if provided, else auto-detected, else Claude
- [X] Path confirmation implicit (always yes)
- [X] Templates from CLI arg if provided, else bundled
- [X] Performance: completes in <2 seconds

**Files**:
- `src/doit_cli/cli/init_command.py` (modify)

---

### T13: Non-Interactive Mode Tests

- **Status**: [X] Complete
- **Parent**: Feature #322
- **Depends On**: T12

**Description**: Add tests for non-interactive mode behavior.

**Acceptance Criteria**:
- [X] `test_non_interactive_skips_prompts` passes
- [X] `test_non_interactive_uses_defaults` passes
- [X] `test_non_interactive_respects_cli_args` passes
- [X] No workflow step output in non-interactive tests

**Files**:
- `tests/integration/test_init_workflow_integration.py` (modify)

---

## Phase 5: US3 - Enhanced Progress Display (P2)

> **User Story**: As a user, I want to see clear progress during init so that I know which step I'm on and how many remain.

### T14: Add Step Counter to Progress Display

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T07
- **Requirements**: FR-011

**Description**: Display "Step X/Y" during workflow execution.

**Acceptance Criteria**:
- [X] Progress shows "Step 1/3", "Step 2/3", "Step 3/3"
- [X] Counter updates as steps complete
- [X] Uses ProgressDisplay from Feature 030

**Files**:
- `src/doit_cli/cli/init_command.py` (modify - verify ProgressDisplay usage)

---

### T15: Show Navigation Hints

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T14
- **Requirements**: FR-012

**Description**: Display navigation hints (back, skip, quit) during prompts.

**Acceptance Criteria**:
- [X] "Type 'back' to return to previous step" shown
- [X] "Type 'skip' to use default" shown for optional steps
- [X] "Press Ctrl+C to cancel" shown
- [X] Hints styled with dim/muted color

**Files**:
- `src/doit_cli/cli/init_command.py` (verify)

---

### T16: Display Step Names in Progress

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T15
- **Requirements**: FR-013

**Description**: Show step name alongside counter.

**Acceptance Criteria**:
- [X] Progress shows "Step 1/3: Select AI Agent"
- [X] Step name from WorkflowStep.name field
- [X] Consistent formatting across all steps

**Files**:
- `src/doit_cli/cli/init_command.py` (verify)

---

### T17: Progress Display Tests

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T16

**Description**: Test progress display output.

**Acceptance Criteria**:
- [X] `test_progress_shows_step_counter` passes
- [X] `test_progress_shows_step_name` passes
- [X] `test_navigation_hints_displayed` passes

**Files**:
- `tests/integration/test_init_workflow_integration.py` (modify)

---

## Phase 6: US4 - Comprehensive Documentation (P2)

> **User Story**: As a developer, I want comprehensive workflow system documentation so that I can understand and extend the workflow capabilities.

### T18: Create Workflow System Guide

- **Status**: [X] Complete
- **Parent**: Feature #324
- **Depends On**: T10, T13
- **Requirements**: FR-014, FR-015

**Description**: Create comprehensive guide for the workflow system.

**Acceptance Criteria**:
- [X] `docs/guides/workflow-system-guide.md` created
- [X] Architecture overview with Mermaid diagram
- [X] Core components documented (WorkflowEngine, StateManager, InteractivePrompt)
- [X] ~1200 words of content

**Files**:
- `docs/guides/workflow-system-guide.md` (create)

---

### T19: Create Workflow Tutorial

- **Status**: [X] Complete
- **Parent**: Feature #324
- **Depends On**: T18
- **Requirements**: FR-016

**Description**: Create step-by-step tutorial for creating custom workflows.

**Acceptance Criteria**:
- [X] `docs/tutorials/creating-workflows.md` created
- [X] Step-by-step instructions with code examples
- [X] Working example workflow included
- [X] ~600 words of content

**Files**:
- `docs/tutorials/creating-workflows.md` (create)

---

### T20: Add API Reference Documentation

- **Status**: [X] Complete
- **Parent**: Feature #324
- **Depends On**: T19
- **Requirements**: FR-017

**Description**: Document public APIs for workflow system.

**Acceptance Criteria**:
- [X] API reference section in workflow guide
- [X] All public methods documented with signatures
- [X] Example usage for each method
- [X] Type hints documented

**Files**:
- `docs/guides/workflow-system-guide.md` (modify)

---

### T21: Update README with Workflow Info

- **Status**: [X] Complete
- **Parent**: Feature #324
- **Depends On**: T20
- **Requirements**: FR-019

**Description**: Add workflow system mention to main README.

**Acceptance Criteria**:
- [X] README mentions guided workflow system
- [X] Link to full documentation
- [X] Brief feature highlights

**Files**:
- `README.md` (modify)

---

## Phase 7: US5 - State Recovery for Init (P3)

> **User Story**: As a user who was interrupted, I want init to offer to resume from where I left off so that I don't have to restart from the beginning.

### T22: Save State on Interrupt

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T07
- **Requirements**: FR-011 (state aspect)

**Description**: Ensure state is saved when user interrupts with Ctrl+C.

**Acceptance Criteria**:
- [X] StateManager.save() called on SIGINT
- [X] State file created at `.doit/state/init_{timestamp}.json`
- [X] Current step and responses preserved
- [X] Message shown: "Progress saved. Run again to resume."

**Files**:
- `src/doit_cli/cli/init_command.py` (verify)

---

### T23: Prompt Resume on Restart

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T22

**Description**: Detect saved state and offer to resume.

**Acceptance Criteria**:
- [X] StateManager.load() called at workflow start
- [X] If interrupted state found, prompt "Resume from step X?"
- [X] If yes, continue from saved step
- [X] If no, start fresh (delete old state)

**Files**:
- `src/doit_cli/cli/init_command.py` (verify WorkflowEngine handles this)

---

### T24: Clean State on Complete

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T23

**Description**: Delete state file when workflow completes successfully.

**Acceptance Criteria**:
- [X] StateManager.delete() called on successful completion
- [X] No state files remain after successful init
- [X] State preserved only for interrupted workflows

**Files**:
- `src/doit_cli/cli/init_command.py` (verify)

---

### T25: State Recovery Tests

- **Status**: [X] Complete
- **Parent**: Feature #323
- **Depends On**: T24

**Description**: Test state persistence and recovery.

**Acceptance Criteria**:
- [X] `test_interrupt_saves_state` passes
- [X] `test_resume_continues_from_saved_step` passes
- [X] `test_complete_cleans_state` passes

**Files**:
- `tests/integration/test_init_workflow_integration.py` (modify)

---

## Phase 8: Polish

### T26: Integration Tests

- **Status**: [X] Complete
- **Parent**: Epic #321
- **Depends On**: T17, T21, T25

**Description**: Run full integration test suite.

**Acceptance Criteria**:
- [X] All tests in `tests/integration/test_init_workflow_integration.py` pass
- [X] No regressions in existing init tests
- [X] Test coverage meets project standards

**Files**:
- `tests/integration/test_init_workflow_integration.py` (verify)

---

### T27: Manual Testing

- **Status**: [X] Complete
- **Parent**: Epic #321
- **Depends On**: T26

**Description**: Perform manual testing of all user scenarios.

**Acceptance Criteria**:
- [X] `doit init .` shows step progress
- [X] User can type "back" to return to previous step
- [X] `doit init . --yes` completes without prompts
- [X] Ctrl+C saves state, next run offers resume
- [X] All agents (claude, copilot, both) work correctly

**Files**: None (manual testing)

---

### T28: Final Review and PR

- **Status**: [~] In Progress
- **Parent**: Epic #321
- **Depends On**: T27

**Description**: Final code review and PR creation.

**Acceptance Criteria**:
- [X] Code passes linting (`ruff check .`)
- [X] All tests pass (`pytest`)
- [X] Documentation complete
- [ ] PR created with summary
- [ ] Run `/doit.reviewit` for code review

**Files**: None (review process)

---

## Parallel Execution Opportunities

Tasks that can be executed in parallel:

| Group | Tasks | Rationale |
| ----- | ----- | --------- |
| Foundation | T03, T04, T05 | Independent setup tasks after T02 |
| US Tracks | US2, US3, US5 | Can proceed in parallel after T07 completes |
| Docs | T18-T21 | Documentation can be written while code stabilizes |

## GitHub Issue Mapping

| Task | GitHub Issue | Parent |
| ---- | ------------ | ------ |
| T01-T02 | Setup tasks | Epic #321 |
| T03-T10 | US1: Interactive Init | Feature #322 |
| T11-T13 | US2: Non-Interactive | Feature #322 |
| T14-T17 | US3: Progress Display | Feature #323 |
| T18-T21 | US4: Documentation | Feature #324 |
| T22-T25 | US5: State Recovery | Feature #323 |
| T26-T28 | Polish | Epic #321 |
