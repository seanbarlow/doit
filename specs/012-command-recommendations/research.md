# Research: Command Workflow Recommendations

**Feature**: 012-command-recommendations
**Date**: 2026-01-10

## Research Topics

### 1. Existing Command Output Patterns

**Question**: How do current doit commands structure their output?

**Findings**:
- Commands use markdown formatting with headers and code blocks
- The `doit init` command already has a "Getting Started" section with next steps
- Rich formatting (boxes, panels) is used via markdown rendering
- Commands end with a summary of actions taken

**Decision**: Follow the existing `doit init` pattern which uses a boxed "Next Steps" section
**Rationale**: Consistent with established UX patterns in the codebase
**Alternatives Considered**:
- JSON output with recommendations (rejected - not human-readable)
- Separate recommendation file (rejected - adds complexity)

### 2. Workflow Sequence Definition

**Question**: What is the canonical doit workflow sequence?

**Findings**:
- Main workflow: specit → planit → taskit → implementit → testit → reviewit → checkin
- Auxiliary commands: constitution, scaffoldit, documentit, roadmapit
- Some commands have branching logic (e.g., specit may recommend clarify before planit)
- Commands can be run out of order but prerequisites should be detected

**Decision**: Define workflow as a directed graph with prerequisites
**Rationale**: Allows flexible navigation while enforcing logical dependencies
**Alternatives Considered**:
- Strict linear sequence (rejected - too rigid for real usage)
- No validation (rejected - loses guidance value)

### 3. Context Detection Methods

**Question**: How should commands detect current workflow state?

**Findings**:
- File existence is reliable: spec.md, plan.md, tasks.md, etc.
- File content can be parsed for markers like [NEEDS CLARIFICATION]
- Task completion status can be read from tasks.md checkboxes
- No persistent state storage needed - files are the source of truth

**Decision**: Use file existence and content parsing for state detection
**Rationale**: Stateless approach aligns with existing architecture
**Alternatives Considered**:
- JSON state file (rejected - adds maintenance burden)
- Database tracking (rejected - overkill for file-based system)

### 4. Recommendation Output Format

**Question**: What format should recommendations use?

**Findings**:
- Current init command uses:
  ```
  ╭────────────────────────────── Getting Started ───────────────────────────────╮
  │ Next Steps:                                                                  │
  │ 1. Run /doit.constitution to establish project principles                    │
  ╰──────────────────────────────────────────────────────────────────────────────╯
  ```
- This box format is visually distinct and scannable
- Numbered lists work well for 1-3 recommendations

**Decision**: Use boxed format with numbered recommendations
**Rationale**: Proven pattern from init command, visually distinct
**Alternatives Considered**:
- Plain markdown headers (rejected - not visually distinct enough)
- Emoji indicators (rejected - inconsistent terminal support)

### 5. Progress Indicator Design

**Question**: How should the workflow progress indicator be displayed?

**Findings**:
- Linear indicators work well: `○ specit → ● planit → ○ taskit → ...`
- Filled circle (●) for current/completed, empty (○) for upcoming
- Must fit on single line for terminal width constraints
- Auxiliary commands should not appear in main progress line

**Decision**: Single-line progress bar with filled/empty circles
**Rationale**: Compact, universal symbol support, clear visual hierarchy
**Alternatives Considered**:
- Multi-line tree view (rejected - too verbose)
- Percentage complete (rejected - workflow isn't always linear)

### 6. Error Recovery Recommendations

**Question**: What should commands recommend when errors occur?

**Findings**:
- Common errors: missing prerequisites, failed validation, incomplete prior steps
- Recovery actions are usually: run prerequisite command, fix issue, retry
- Error messages should include specific fix recommendations

**Decision**: Each error type maps to a specific recovery recommendation
**Rationale**: Actionable guidance reduces user frustration
**Alternatives Considered**:
- Generic "see documentation" (rejected - not helpful)
- Automatic retry (rejected - out of scope)

## Summary

All research questions resolved. Key decisions:

1. **Output format**: Boxed "Next Steps" section (like init command)
2. **State detection**: File existence and content parsing
3. **Progress indicator**: Single-line with ○/● symbols
4. **Workflow graph**: Directed with prerequisites, not strictly linear
5. **Error handling**: Specific recovery recommendations per error type

No NEEDS CLARIFICATION items remain.
