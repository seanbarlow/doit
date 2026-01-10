# Implementation Plan: Update Doit Templates

**Branch**: `002-update-doit-templates` | **Date**: 2026-01-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-update-doit-templates/spec.md`

**Note**: This template is filled in by the `/doit.plan` command. See `.claude/commands/doit.plan.md` for the execution workflow.

## Summary

Update the template files in `.specify/templates/` to remove references to non-existent doit commands (`/doit.checklist`, `/doit.clarify`) and fix incorrect path references. This is a documentation-only change requiring edits to 3 markdown files.

## Technical Context

**Language/Version**: Markdown (documentation files)
**Primary Dependencies**: None (text file edits only)
**Storage**: N/A
**Testing**: Manual verification - grep for command references
**Target Platform**: Cross-platform (markdown files)
**Project Type**: Documentation update (no code changes)
**Performance Goals**: N/A
**Constraints**: N/A
**Scale/Scope**: 3 files to update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS - Documentation-only changes align with project structure.

| Gate | Status | Notes |
|------|--------|-------|
| Tech Stack Alignment | N/A | Markdown files only, no new tech |
| Complexity | PASS | Simple text replacements |
| Principles | PASS | Improves documentation accuracy |

## Project Structure

### Documentation (this feature)

```text
specs/002-update-doit-templates/
├── plan.md              # This file (/doit.plan command output)
├── research.md          # Phase 0 output (/doit.plan command)
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/doit.tasks command)
```

### Files to Modify

```text
.specify/templates/
├── checklist-template.md    # MODIFY: Remove /doit.checklist reference
├── plan-template.md         # MODIFY: Fix path reference to command file
└── tasks-template.md        # NO CHANGE: References valid /doit.tasks

.claude/commands/
└── doit.specify.md          # MODIFY: Remove /doit.clarify reference
```

**Structure Decision**: No source code changes. This feature modifies only markdown template and command definition files.

## Complexity Tracking

> No violations - simple documentation update.

| Aspect | Complexity | Justification |
|--------|------------|---------------|
| Files Changed | Low | 3 files |
| Change Type | Low | Text replacements |
| Risk | Low | No code execution affected |
