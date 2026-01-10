# Scaffold Doit Commands

**Completed**: 2026-01-10
**Branch**: 003-scaffold-doit-commands
**PR**: Pending

## Overview

When initializing a new project using the `/doit.scaffoldit` command, the doit command suite is now automatically generated. This feature also renamed the configuration folder from `.specify` to `.doit` for consistent naming, removed unused templates, and created command templates for scaffolding.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Command template directory structure created | Done |
| FR-002 | Scaffold command enhanced with command generation | Done |
| FR-003 | Template cleanup completed (unused templates removed) | Done |
| FR-004 | All 9 command templates created | Done |
| FR-005 | Folder renamed from .specify to .doit | Done |

## Technical Details

### Key Changes

1. **Folder Rename**: Renamed `.specify/` to `.doit/` using `git mv`
2. **Reference Updates**: Updated 40+ files with `.specify` to `.doit` references
3. **Template Cleanup**: Removed 2 unused templates (agent-file-template.md, checklist-template.md)
4. **Command Templates**: Created 9 command templates in `.doit/templates/commands/`
5. **Scaffold Enhancement**: Added section 8 to doit.scaffoldit.md for command generation

### Files Changed

**Folder Renamed**:
- `.specify/` → `.doit/`

**Commands Updated** (9 files):
- `.claude/commands/doit.checkin.md`
- `.claude/commands/doit.constitution.md`
- `.claude/commands/doit.implementit.md`
- `.claude/commands/doit.planit.md`
- `.claude/commands/doit.reviewit.md`
- `.claude/commands/doit.scaffoldit.md`
- `.claude/commands/doit.specit.md`
- `.claude/commands/doit.taskit.md`
- `.claude/commands/doit.testit.md`

**Templates Created** (9 files):
- `.doit/templates/commands/doit.*.md` (all 9 commands)

**Templates Deleted** (2 files):
- `.doit/templates/agent-file-template.md`
- `.doit/templates/checklist-template.md`

**Scripts Updated** (13 files):
- `.doit/scripts/bash/*.sh` (5 files)
- `scripts/bash/*.sh` (4 files)
- `scripts/powershell/*.ps1` (4 files)

**Documentation Updated** (8+ files):
- README.md, CHANGELOG.md, CONTRIBUTING.md
- docs/upgrade.md, docs/installation.md, docs/local-development.md, docs/quickstart.md
- spec-driven.md, CLAUDE.md

## Testing

### Automated Tests
- No automated tests requested for this feature
- Manual verification via quickstart.md commands

### Manual Tests
| Test | Result |
|------|--------|
| `.doit/` folder exists | PASS |
| `.specify/` folder removed | PASS |
| Zero `.specify/` folder references | PASS |
| Unused templates removed | PASS |
| 9 command templates exist | PASS |
| Active templates kept | PASS |
| Scaffold documentation updated | PASS |

## Related Issues

- No GitHub issues were created for this feature

## User Stories Completed

1. **US-001**: Scaffold Projects with Doit Commands
2. **US-002**: Remove Unused Templates
3. **US-003**: Add Command Templates for Scaffolding
4. **US-004**: Rename .specify to .doit
