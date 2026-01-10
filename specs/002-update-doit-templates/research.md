# Research: Update Doit Templates

**Branch**: `002-update-doit-templates` | **Date**: 2026-01-09

## Overview

This research documents the findings from analyzing the template files and doit commands to determine the exact changes needed.

## Findings

### 1. Non-Existent Command References

**Decision**: Remove or replace references to commands that don't exist.

**Rationale**: The doit command suite was recently refactored. Template files still reference old/planned commands that were never implemented.

**Analysis**:

| File | Invalid Reference | Resolution |
| ---- | ----------------- | ---------- |
| checklist-template.md | `/doit.checklist` | Replace with generic note about checklist usage |
| doit.specify.md | `/doit.clarify` | Replace with `/doit.plan` (appropriate next step) |

**Alternatives Considered**:
- Create the missing commands: Rejected - out of scope, requires separate feature
- Leave as-is with TODO markers: Rejected - confuses users now

### 2. Invalid Path References

**Decision**: Update paths to point to actual file locations.

**Rationale**: The plan-template.md references a path that doesn't exist.

**Analysis**:

| File | Invalid Path | Correct Path |
| ---- | ------------ | ------------ |
| plan-template.md | `.specify/templates/commands/plan.md` | `.claude/commands/doit.plan.md` |

**Alternatives Considered**:
- Create the referenced directory structure: Rejected - unnecessary duplication
- Remove the reference entirely: Rejected - helpful for users to know where command is defined

### 3. Valid References (No Changes Needed)

The following references are valid and require no changes:

| File | Reference | Status |
| ---- | --------- | ------ |
| tasks-template.md | `/doit.tasks` | Valid - command exists |
| plan-template.md | `/doit.plan` | Valid - command exists |
| plan-template.md | `/doit.tasks` | Valid - command exists |

## Available Commands Inventory

Verified commands in `.claude/commands/`:

1. `/doit.checkin` - doit.checkin.md
2. `/doit.constitution` - doit.constitution.md
3. `/doit.implement` - doit.implement.md
4. `/doit.plan` - doit.plan.md
5. `/doit.review` - doit.review.md
6. `/doit.scaffold` - doit.scaffold.md
7. `/doit.specify` - doit.specify.md
8. `/doit.tasks` - doit.tasks.md
9. `/doit.test` - doit.test.md

## Conclusion

All unknowns resolved. Ready for implementation:
- 2 template files need command reference updates
- 1 command file needs reference update
- 1 template file needs path correction
