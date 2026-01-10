# Update Doit Templates

**Completed**: 2026-01-09
**Branch**: 002-update-doit-templates
**PR**: Pending

## Overview

Updated the template files in `.specify/templates/` to remove references to non-existent doit commands (`/doit.checklist`, `/doit.clarify`) and fixed incorrect path references. This ensures template documentation accurately reflects the actual doit command suite.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | All template files MUST only reference commands that exist in `.claude/commands/` | Done |
| FR-002 | The checklist-template.md MUST NOT reference `/doit.checklist` | Done |
| FR-003 | The plan-template.md MUST reference `.claude/commands/doit.planit.md` | Done |
| FR-004 | All templates MUST use correct command naming convention | Done |
| FR-005 | Path references in templates MUST point to existing files | Done |
| FR-006 | The doit.specit.md command MUST NOT reference `/doit.clarify` | Done |

## Technical Details

- **Type**: Documentation-only change
- **Files Changed**: 3 markdown files
- **Risk Level**: Low (no code execution affected)

### Key Changes

1. Removed `/doit.checklist` references from checklist-template.md
2. Replaced `/doit.clarify` with `/doit.planit` in doit.specit.md
3. Fixed path reference from `.specify/templates/commands/plan.md` to `.claude/commands/doit.planit.md`

## Files Changed

| File | Change |
|------|--------|
| `.specify/templates/checklist-template.md` | Removed `/doit.checklist` references |
| `.specify/templates/plan-template.md` | Fixed path to `.claude/commands/doit.planit.md` |
| `.claude/commands/doit.specit.md` | Removed `/doit.clarify` references |

## Testing

- **Automated tests**: N/A (documentation-only)
- **Manual verification**: All grep commands passed
  - Zero `/doit.checklist` references found
  - Zero `/doit.clarify` references found
  - Zero invalid path references found

## Success Criteria Met

- SC-001: Zero template files contain references to non-existent commands
- SC-002: 100% of path references resolve to existing files
- SC-003: Developers can follow template documentation without broken references
- SC-004: All template files pass validation
