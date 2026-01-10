# Feature Specification: Scaffold Doit Commands

## Overview

**Feature ID**: 003-scaffold-doit-commands
**Created**: 2026-01-09
**Status**: Draft
**Branch**: `003-scaffold-doit-commands`

## Problem Statement

When initializing a new project using the `/doit.scaffold` command, the doit command suite is not automatically generated. Users must manually copy these commands into new projects. Additionally, the `.specify/templates/` folder contains templates that are no longer needed and is missing templates for new commands.

## User Stories

### US-001: Scaffold Projects with Doit Commands (P1)
**As a** developer initializing a new project
**I want** the scaffold command to automatically generate all doit command files
**So that** I can immediately use the doit workflow without manual setup

**Acceptance Criteria**:
- [ ] AC-001.1: Running `/doit.scaffold` creates `.claude/commands/` directory
- [ ] AC-001.2: All 9 doit command files are generated (checkin, constitution, implement, plan, review, scaffold, specify, tasks, test)
- [ ] AC-001.3: Generated commands are functional and match source templates
- [ ] AC-001.4: Scaffold command documentation reflects this new capability

### US-002: Remove Unused Templates (P1)
**As a** project maintainer
**I want** unused templates removed from `.specify/templates/`
**So that** the template folder only contains relevant, actively-used templates

**Acceptance Criteria**:
- [ ] AC-002.1: Identify templates that are not referenced by any doit command
- [ ] AC-002.2: Remove unused template files
- [ ] AC-002.3: Update any documentation referencing removed templates

### US-003: Add Command Templates for Scaffolding (P1)
**As a** developer using the scaffold command
**I want** template versions of all doit commands
**So that** new projects receive consistent, up-to-date command definitions

**Acceptance Criteria**:
- [ ] AC-003.1: Create command templates in `.doit/templates/commands/`
- [ ] AC-003.2: Templates match current doit command implementations
- [ ] AC-003.3: Scaffold command copies templates to `.claude/commands/` in new projects

### US-004: Rename .specify to .doit (P1)
**As a** developer using the doit workflow
**I want** the configuration folder renamed from `.specify` to `.doit`
**So that** the folder name matches the command naming convention

**Acceptance Criteria**:
- [ ] AC-004.1: Rename `.specify/` directory to `.doit/`
- [ ] AC-004.2: Update all references in doit commands from `.specify` to `.doit`
- [ ] AC-004.3: Update all scripts that reference `.specify` paths
- [ ] AC-004.4: Update documentation to reflect new folder name

## Functional Requirements

### FR-001: Command Template Directory Structure
- Create `.doit/templates/commands/` directory
- Store all doit command templates with `.md` extension
- Templates must be self-contained and not reference project-specific paths

### FR-002: Scaffold Command Enhancement
- Modify `doit.scaffold.md` to include command generation step
- Copy command templates to target project's `.claude/commands/` directory
- Maintain directory structure during copy

### FR-003: Template Cleanup
- Remove templates no longer used by the doit workflow:
  - `agent-file-template.md` - Not referenced by any current command
  - `checklist-template.md` - Referenced in comments but `/doit.checklist` doesn't exist
- Keep templates actively used:
  - `spec-template.md` - Used by `/doit.specify`
  - `plan-template.md` - Used by `/doit.plan`
  - `tasks-template.md` - Used by `/doit.tasks`

### FR-004: Command Templates to Create
Create templates for all 9 doit commands:
1. `doit.checkin.md` - Feature completion and PR creation
2. `doit.constitution.md` - Project constitution management
3. `doit.implement.md` - Task implementation execution
4. `doit.plan.md` - Implementation planning
5. `doit.review.md` - Code review workflow
6. `doit.scaffold.md` - Project scaffolding
7. `doit.specify.md` - Feature specification
8. `doit.tasks.md` - Task generation
9. `doit.test.md` - Test execution

### FR-005: Folder Rename (.specify → .doit)
- Rename `.specify/` directory to `.doit/`
- Update all doit command files to reference `.doit/` paths
- Update all bash scripts in `.doit/scripts/bash/`
- Update CLAUDE.md and other documentation
- Ensure backwards compatibility is documented

## Non-Functional Requirements

### NFR-001: Maintainability
- Command templates should be single source of truth
- Updates to templates automatically reflect in new projects

### NFR-002: Backwards Compatibility
- Existing projects are not affected
- Only new scaffold operations use updated templates

## Technical Constraints

- Templates must work with Claude Code slash command system
- File paths in templates should use relative references where possible
- Templates should not contain hardcoded project names or paths

## Success Criteria

1. Running `/doit.scaffold` on a new project creates all 9 doit command files
2. `.doit/templates/` contains only actively-used templates
3. New projects can immediately run any doit command after scaffolding
4. Template directory structure is clean and well-organized
5. All references to `.specify` are replaced with `.doit`

## Dependencies

- Feature 002 (Update Doit Templates) - Completed
- Feature 001 (Doit Command Refactor) - Completed

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing projects | High | Only affects new scaffold operations |
| Template drift from source | Medium | Consider automation to sync templates |
| Missing command functionality | Medium | Thorough testing of each generated command |

## Out of Scope

- Automatic updates to existing projects
- Version management for command templates
- Custom command generation
