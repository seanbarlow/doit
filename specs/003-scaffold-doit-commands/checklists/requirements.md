# Requirements Checklist: Scaffold Doit Commands

**Purpose**: Track implementation completeness for Feature 003
**Created**: 2026-01-09
**Feature**: [spec.md](../spec.md)

## US-001: Scaffold Projects with Doit Commands

- [x] AC-001.1: Running `/doit.scaffold` creates `.claude/commands/` directory
- [x] AC-001.2: All 9 doit command files are generated
- [x] AC-001.3: Generated commands are functional and match source templates
- [x] AC-001.4: Scaffold command documentation reflects this new capability

## US-002: Remove Unused Templates

- [x] AC-002.1: Identify templates that are not referenced by any doit command
- [x] AC-002.2: Remove unused template files
- [x] AC-002.3: Update any documentation referencing removed templates

## US-003: Add Command Templates for Scaffolding

- [x] AC-003.1: Create command templates in `.doit/templates/commands/`
- [x] AC-003.2: Templates match current doit command implementations
- [x] AC-003.3: Scaffold command copies templates to `.claude/commands/` in new projects

## US-004: Rename .specify to .doit

- [x] AC-004.1: Rename `.specify/` directory to `.doit/`
- [x] AC-004.2: Update all references in doit commands from `.specify` to `.doit`
- [x] AC-004.3: Update all scripts that reference `.specify` paths
- [x] AC-004.4: Update documentation to reflect new folder name

## Functional Requirements

- [x] FR-001: Command template directory structure created
- [x] FR-002: Scaffold command enhanced with command generation
- [x] FR-003: Template cleanup completed (unused templates removed)
- [x] FR-004: All 9 command templates created
- [x] FR-005: Folder renamed from .specify to .doit

## Verification

- [x] New project scaffolding includes all doit commands
- [x] Each generated command file is valid and functional
- [x] `.doit/templates/` contains only active templates
- [x] No broken references in remaining templates

## Notes

- Check items off as completed: `[x]`
- Link to relevant commits or PRs when completing items
- Items are numbered by acceptance criteria for traceability
