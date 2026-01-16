# Research: Init Workflow Integration

**Feature**: 031-init-workflow-integration
**Date**: 2026-01-16
**Status**: Complete

## Research Summary

This feature integrates the existing init command with the guided workflow system from Feature 030. Research focused on understanding the existing workflow patterns and identifying the best integration approach.

---

## Research Items

### R1: Existing Workflow Integration Pattern

**Question**: How do other commands integrate with the WorkflowEngine?

**Research Method**: Code analysis of existing `workflow_mixin.py` and Feature 030 implementation

**Findings**:

The `workflow_mixin.py` provides a reusable pattern:

```python
class WorkflowMixin:
    """Mixin providing workflow capabilities to CLI commands."""

    def run_workflow(self, workflow: Workflow, non_interactive: bool = False) -> dict:
        """Execute workflow and return responses."""
        if non_interactive:
            return self._run_non_interactive(workflow)

        engine = WorkflowEngine(console=self.console, state_manager=StateManager())
        return engine.run(workflow)
```

**Decision**: Use `WorkflowMixin` pattern for init command integration
**Rationale**: Consistent with existing architecture, minimal code duplication
**Alternatives Rejected**: Direct WorkflowEngine instantiation (less maintainable)

---

### R2: InitWorkflow Step Design

**Question**: What steps should the InitWorkflow contain?

**Research Method**: Analysis of current `init_command.py` prompts and user flows

**Findings**:

Current init command has these interactive touchpoints:
1. Agent selection (Claude, Copilot, Both) - `prompt_agent_selection()`
2. Unsafe directory warning - `typer.confirm()`
3. Custom template validation - `typer.confirm()`

**Decision**: Define 3 workflow steps:
1. **Agent Selection** (required): Choice step with options Claude/Copilot/Both
2. **Path Confirmation** (required): Confirm the target directory
3. **Custom Templates** (optional): Path input for custom template directory

**Rationale**: Maps directly to existing user interactions, maintains backward compatibility
**Alternatives Rejected**: Single "configure all" step (less granular navigation)

---

### R3: Non-Interactive Mode Behavior

**Question**: How should `--yes` flag interact with the workflow system?

**Research Method**: Analysis of existing `--yes` flag behavior and CI/CD use cases

**Findings**:

Current behavior with `--yes`:
- Skips agent selection prompt (defaults to Claude or auto-detected)
- Skips unsafe directory confirmation
- Skips custom template confirmation

Workflow system supports non-interactive via:
- `InteractivePrompt._is_interactive()` checks TTY
- Default values in `WorkflowStep.default_value`

**Decision**: When `--yes` flag is set, bypass WorkflowEngine entirely and use direct defaults
**Rationale**: Fastest execution path for CI/CD, maintains <2s performance target
**Alternatives Rejected**: Running workflow with auto-accept (unnecessary overhead)

---

### R4: State Recovery Integration

**Question**: How should init workflow state be persisted for resume?

**Research Method**: Analysis of existing `StateManager` implementation

**Findings**:

`StateManager` handles:
- State file location: `.doit/state/{command_name}_{timestamp}.json`
- Save on interrupt (SIGINT handler in WorkflowEngine)
- Load and prompt to resume on next execution
- Delete on successful completion

**Decision**: Use existing StateManager as-is with command_name="init"
**Rationale**: No modifications needed, existing infrastructure handles all requirements
**Alternatives Rejected**: Custom state handling (reinventing the wheel)

---

### R5: Documentation Structure

**Question**: What should the workflow documentation cover?

**Research Method**: Review of similar CLI documentation (Click, Typer docs) and user needs

**Findings**:

Key documentation needs:
1. Architecture overview with diagrams
2. API reference for core classes
3. Tutorial for creating custom workflows
4. Extension points documentation

Industry best practices:
- Start with "Getting Started" quickstart
- Provide runnable code examples
- Include troubleshooting section

**Decision**: Create two documents:
1. `docs/guides/workflow-system-guide.md` - Comprehensive guide (~1200 words)
2. `docs/tutorials/creating-workflows.md` - Step-by-step tutorial (~600 words)

**Rationale**: Separates reference content from learning content
**Alternatives Rejected**: Single monolithic document (harder to navigate)

---

### R6: Input Validation for Init Steps

**Question**: What validators are needed for init workflow steps?

**Research Method**: Analysis of existing validators in `input_validator.py`

**Findings**:

Existing validators:
- `PathExistsValidator` - validates path exists
- `DirectoryValidator` - validates is directory
- `NonEmptyValidator` - validates non-empty string
- `ChoiceValidator` - validates against option list

**Decision**: Use existing validators:
- Agent selection: `ChoiceValidator` with ["claude", "copilot", "both"]
- Path confirmation: No validator (just confirmation)
- Custom templates: `PathExistsValidator` + `DirectoryValidator` (optional step)

**Rationale**: Reuses existing validation infrastructure
**Alternatives Rejected**: Custom validators (unnecessary complexity)

---

## Unresolved Items

None - all research items resolved.

## Dependencies Identified

| Dependency | Version | Purpose |
| ---------- | ------- | ------- |
| WorkflowEngine | Feature 030 | Core workflow orchestration |
| StateManager | Feature 030 | State persistence for resume |
| InteractivePrompt | Feature 030 | User input handling |
| ProgressDisplay | Feature 030 | Step progress visualization |

All dependencies are already implemented in Feature 030 and merged to main.

## Next Steps

1. Proceed to Phase 1: Generate data-model.md with InitWorkflow definition
2. Generate contracts/init-workflow.md with API contract
3. Generate quickstart.md with implementation guide
