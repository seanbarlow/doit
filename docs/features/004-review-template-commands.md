# Review Template Commands

**Completed**: 2026-01-10
**Branch**: 004-review-template-commands
**PR**: -

## Overview

Remove legacy doit templates from `templates/commands/` and replace them with standardized doit command templates from `.doit/templates/commands/`. This ensures a single authoritative source for command templates following the doit naming convention.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Remove all legacy doit templates from templates/commands/ | Done |
| FR-002 | Copy all 9 doit command templates to templates/commands/ | Done |
| FR-003 | Templates in templates/commands/ match .doit/templates/commands/ | Done |
| FR-004 | All templates reference .doit/ paths, not .specify/ | Done |
| FR-005 | All templates have valid YAML frontmatter with description | Done |
| FR-006 | doit.scaffoldit.md references correct template source paths | Done |

## Technical Details

- **Language/Version**: Bash 5.x (file operations only)
- **Dependencies**: Standard Unix utilities (rm, cp)
- **Testing**: Manual verification via shell commands

### Key Decisions

1. Full replacement of legacy templates rather than in-place editing
2. Single authoritative source in `.doit/templates/commands/`
3. Distribution templates in `templates/commands/` for scaffolding

## Files Changed

### Removed (9 legacy templates)

- `templates/commands/analyze.md`
- `templates/commands/checklist.md`
- `templates/commands/clarify.md`
- `templates/commands/constitution.md`
- `templates/commands/implement.md`
- `templates/commands/plan.md`
- `templates/commands/specify.md`
- `templates/commands/tasks.md`
- `templates/commands/taskstoissues.md`

### Added (9 doit templates)

- `templates/commands/doit.checkin.md`
- `templates/commands/doit.constitution.md`
- `templates/commands/doit.implementit.md`
- `templates/commands/doit.planit.md`
- `templates/commands/doit.reviewit.md`
- `templates/commands/doit.scaffoldit.md`
- `templates/commands/doit.specit.md`
- `templates/commands/doit.taskit.md`
- `templates/commands/doit.testit.md`

## Testing

### Automated Tests

N/A - File operations feature

### Manual Tests

| Test | Result |
|------|--------|
| MT-001: Legacy templates removed | PASS |
| MT-002: Only doit templates exist | PASS |
| MT-003: 9 templates present | PASS |
| MT-004: Content matches source | PASS |
| MT-005: Zero .specify/ refs | PASS |
| MT-006: Valid YAML frontmatter | PASS |

## Success Criteria

| ID | Criterion | Status |
|----|-----------|--------|
| SC-001 | Zero legacy doit templates remain | PASS |
| SC-002 | 9 doit command templates exist | PASS |
| SC-003 | Templates match source directory | PASS |
| SC-004 | Zero .specify/ references | PASS |
| SC-005 | Zero doit references | PASS |

## Related Issues

N/A - GitHub remote not accessible
