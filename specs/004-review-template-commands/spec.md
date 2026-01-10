# Feature Specification: Review Template Commands

**Feature Branch**: `004-review-template-commands`
**Created**: 2026-01-10
**Status**: Draft
**Input**: User description: "Review and update templates and template commands that generate doit commands. Remove legacy speckit templates and replace with doit templates."

## Problem Statement

The codebase contains two separate sets of command templates:
1. `.doit/templates/commands/` - The 9 doit command templates used by `/doit.scaffold`
2. `templates/commands/` - Legacy speckit templates with outdated naming and references

The legacy templates in `templates/commands/` still contain "speckit" references and don't follow the doit naming convention. These need to be removed and replaced with the standardized doit templates to ensure consistency across the codebase.

## User Scenarios & Testing

### User Story 1 - Remove Legacy Speckit Templates (Priority: P1)

As a project maintainer, I want the legacy speckit templates removed from `templates/commands/` so that there is only one authoritative source of command templates following the doit naming convention.

**Why this priority**: Legacy templates cause confusion and may be accidentally used instead of the correct doit templates. Removing them eliminates this source of errors.

**Independent Test**: After implementation, `ls templates/commands/` should show doit-named files (doit.*.md) instead of speckit-named files (clarify.md, analyze.md, etc.)

**Acceptance Scenarios**:

1. **Given** legacy speckit templates exist in `templates/commands/`, **When** the cleanup is performed, **Then** all legacy templates (analyze.md, checklist.md, clarify.md, constitution.md, implement.md, plan.md, specify.md, tasks.md, taskstoissues.md) are removed
2. **Given** the cleanup is complete, **When** a user looks at `templates/commands/`, **Then** only doit-named templates exist

---

### User Story 2 - Add Doit Templates to Root Templates (Priority: P1)

As a developer scaffolding a new project, I want the `templates/commands/` directory to contain the same doit command templates as `.doit/templates/commands/` so that template distribution is consistent.

**Why this priority**: The `templates/` directory is used for distributing templates to new projects. It must contain the correct doit templates.

**Independent Test**: `ls templates/commands/doit.*.md | wc -l` should return 9 (all doit commands present)

**Acceptance Scenarios**:

1. **Given** the legacy templates are removed, **When** doit templates are added, **Then** `templates/commands/` contains all 9 doit command templates
2. **Given** doit templates are in `templates/commands/`, **When** comparing to `.doit/templates/commands/`, **Then** the files match in content

---

### User Story 3 - Verify Doit Template Quality (Priority: P2)

As a developer using the doit workflow, I want to verify that all templates in `.doit/templates/commands/` are correct and functional so that scaffolded projects receive working command definitions.

**Why this priority**: This ensures the templates that get distributed actually work correctly. Lower priority than removal because the current templates were copied from working commands.

**Independent Test**: Each template can be validated by checking for correct path references (`.doit/` not `.specify/`) and proper command structure

**Acceptance Scenarios**:

1. **Given** templates in `.doit/templates/commands/`, **When** reviewed for path references, **Then** all paths reference `.doit/` not `.specify/`
2. **Given** templates are reviewed, **When** checking structure, **Then** each template has valid YAML frontmatter and execution outline

---

### Edge Cases

- What happens if a template references a non-existent path? Should be flagged during review.
- What happens if `templates/commands/` doesn't exist? Create it before adding templates.

## Requirements

### Functional Requirements

- **FR-001**: System MUST remove all legacy speckit templates from `templates/commands/` directory
- **FR-002**: System MUST copy all 9 doit command templates to `templates/commands/` after cleanup
- **FR-003**: Templates in `templates/commands/` MUST match templates in `.doit/templates/commands/`
- **FR-004**: All templates MUST reference `.doit/` paths, not `.specify/` paths
- **FR-005**: All templates MUST have valid YAML frontmatter with description field
- **FR-006**: The doit.scaffold.md template MUST reference the correct template source paths

### Files to Remove (Legacy Speckit Templates)

- `templates/commands/analyze.md`
- `templates/commands/checklist.md`
- `templates/commands/clarify.md`
- `templates/commands/constitution.md`
- `templates/commands/implement.md`
- `templates/commands/plan.md`
- `templates/commands/specify.md`
- `templates/commands/tasks.md`
- `templates/commands/taskstoissues.md`

### Files to Add (Doit Command Templates)

Copy from `.doit/templates/commands/` to `templates/commands/`:
- `doit.checkin.md`
- `doit.constitution.md`
- `doit.implement.md`
- `doit.plan.md`
- `doit.review.md`
- `doit.scaffold.md`
- `doit.specify.md`
- `doit.tasks.md`
- `doit.test.md`

## Success Criteria

### Measurable Outcomes

- **SC-001**: Zero legacy speckit templates remain in `templates/commands/`
- **SC-002**: 9 doit command templates exist in `templates/commands/`
- **SC-003**: All templates in `templates/commands/` match their counterparts in `.doit/templates/commands/`
- **SC-004**: Zero references to `.specify/` remain in any template file
- **SC-005**: Zero references to "speckit" remain in any template file

## Dependencies

- Feature 003 (Scaffold Doit Commands) - Completed (created `.doit/templates/commands/`)

## Assumptions

- The templates in `.doit/templates/commands/` are the authoritative source
- The `templates/` directory is used for distributing templates during project scaffolding
- No external systems depend on the legacy speckit template names

## Out of Scope

- Modifying the actual doit commands in `.claude/commands/`
- Creating new doit commands
- Changes to the scaffold workflow itself (just template files)
