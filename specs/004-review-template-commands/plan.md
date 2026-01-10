# Implementation Plan: Review Template Commands

**Branch**: `004-review-template-commands` | **Date**: 2026-01-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-review-template-commands/spec.md`

## Summary

Remove legacy speckit templates from `templates/commands/` and replace them with standardized doit command templates from `.doit/templates/commands/`. This ensures a single authoritative source for command templates following the doit naming convention.

## Technical Context

**Language/Version**: Bash 5.x (file operations only)
**Primary Dependencies**: None (standard Unix utilities: rm, cp)
**Storage**: N/A (file system operations)
**Testing**: Manual verification via shell commands
**Target Platform**: Any POSIX-compatible system
**Project Type**: File operations (no source code changes)
**Performance Goals**: N/A (one-time migration)
**Constraints**: N/A
**Scale/Scope**: 9 files to remove, 9 files to copy

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS - No constitution violations

This feature involves only file operations (removing/copying markdown templates) with no architectural or code changes. The project constitution template is not yet filled in, but this feature aligns with:

- Existing use of Markdown for command definitions
- File-based template distribution pattern established in Feature 003
- No new technologies introduced

## Project Structure

### Documentation (this feature)

```text
specs/004-review-template-commands/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
└── checklists/
    └── requirements.md  # Requirements tracking
```

### Source Files (affected)

```text
templates/commands/           # Target directory for cleanup and replacement
├── [REMOVE] analyze.md       # Legacy speckit template
├── [REMOVE] checklist.md     # Legacy speckit template
├── [REMOVE] clarify.md       # Legacy speckit template
├── [REMOVE] constitution.md  # Legacy speckit template
├── [REMOVE] implement.md     # Legacy speckit template
├── [REMOVE] plan.md          # Legacy speckit template
├── [REMOVE] specify.md       # Legacy speckit template
├── [REMOVE] tasks.md         # Legacy speckit template
├── [REMOVE] taskstoissues.md # Legacy speckit template
├── [ADD] doit.checkin.md     # From .doit/templates/commands/
├── [ADD] doit.constitution.md
├── [ADD] doit.implement.md
├── [ADD] doit.plan.md
├── [ADD] doit.review.md
├── [ADD] doit.scaffold.md
├── [ADD] doit.specify.md
├── [ADD] doit.tasks.md
└── [ADD] doit.test.md

.doit/templates/commands/     # Source directory (authoritative)
├── doit.checkin.md
├── doit.constitution.md
├── doit.implement.md
├── doit.plan.md
├── doit.review.md
├── doit.scaffold.md
├── doit.specify.md
├── doit.tasks.md
└── doit.test.md
```

**Structure Decision**: No source code structure changes. This feature operates on the `templates/commands/` directory, replacing legacy files with copies from `.doit/templates/commands/`.

## Complexity Tracking

No complexity violations - this is a straightforward file operation task with no architectural decisions.
