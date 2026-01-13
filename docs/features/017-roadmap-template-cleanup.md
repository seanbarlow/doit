# Roadmap Template Cleanup

**Completed**: 2026-01-13
**Branch**: 017-roadmap-template-cleanup
**PR**: #56

## Overview

Updated the roadmap and roadmap_completed templates in `templates/memory/` to contain placeholder syntax instead of sample data. Users initializing new projects with `doit init` now receive clean templates they can customize for their project.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | roadmap.md contains placeholder syntax | Done |
| FR-002 | roadmap_completed.md contains placeholder syntax | Done |
| FR-003 | Memory templates match reference template structure | Done |
| FR-004 | Placeholder format uses `[UPPER_SNAKE_CASE]` | Done |
| FR-005 | HTML comments preserved | Done |

## Technical Details

This was a template content update with no code changes:

- Copied content from `.doit/templates/roadmap-template.md` to `templates/memory/roadmap.md`
- Copied content from `.doit/templates/completed-roadmap-template.md` to `templates/memory/roadmap_completed.md`
- Verified files match exactly using diff commands
- Confirmed no sample content remains ("Task Management App" removed)

### Template Locations

| Location | Purpose |
|----------|---------|
| `.doit/templates/` | Reference templates (canonical format documentation) |
| `templates/memory/` | Memory templates (packaged with CLI, copied by `doit init`) |

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `templates/memory/roadmap.md` | Modified | Replaced sample data with placeholder template |
| `templates/memory/roadmap_completed.md` | Modified | Replaced completed feature entries with placeholder template |

## Testing

- **Automated tests**: N/A (no code changes)
- **Manual tests**: 4/4 passed
  - MT-001: Verified roadmap.md contains placeholders
  - MT-002: Verified roadmap_completed.md contains placeholders
  - MT-003: Verified no sample data remains
  - MT-004: Verified structure matches reference templates

## Related Issues

- Epic: #46
- Features: #47, #48
- Tasks: #49, #50, #51, #52, #53, #54, #55
