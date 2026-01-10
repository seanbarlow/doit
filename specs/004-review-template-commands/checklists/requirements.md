# Requirements Checklist: Review Template Commands

**Feature**: 004-review-template-commands
**Created**: 2026-01-10
**Status**: Complete

## Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | System MUST remove all legacy speckit templates from `templates/commands/` directory | P1 | [X] |
| FR-002 | System MUST copy all 9 doit command templates to `templates/commands/` after cleanup | P1 | [X] |
| FR-003 | Templates in `templates/commands/` MUST match templates in `.doit/templates/commands/` | P1 | [X] |
| FR-004 | All templates MUST reference `.doit/` paths, not `.specify/` paths | P1 | [X] |
| FR-005 | All templates MUST have valid YAML frontmatter with description field | P2 | [X] |
| FR-006 | The doit.scaffold.md template MUST reference the correct template source paths | P2 | [X] |

## Files to Remove

| File | Status |
|------|--------|
| templates/commands/analyze.md | [X] |
| templates/commands/checklist.md | [X] |
| templates/commands/clarify.md | [X] |
| templates/commands/constitution.md | [X] |
| templates/commands/implement.md | [X] |
| templates/commands/plan.md | [X] |
| templates/commands/specify.md | [X] |
| templates/commands/tasks.md | [X] |
| templates/commands/taskstoissues.md | [X] |

## Files to Add

| File | Status |
|------|--------|
| templates/commands/doit.checkin.md | [X] |
| templates/commands/doit.constitution.md | [X] |
| templates/commands/doit.implement.md | [X] |
| templates/commands/doit.plan.md | [X] |
| templates/commands/doit.review.md | [X] |
| templates/commands/doit.scaffold.md | [X] |
| templates/commands/doit.specify.md | [X] |
| templates/commands/doit.tasks.md | [X] |
| templates/commands/doit.test.md | [X] |

## Success Criteria

| ID | Criterion | Status |
|----|-----------|--------|
| SC-001 | Zero legacy speckit templates remain in `templates/commands/` | [X] |
| SC-002 | 9 doit command templates exist in `templates/commands/` | [X] |
| SC-003 | All templates in `templates/commands/` match their counterparts in `.doit/templates/commands/` | [X] |
| SC-004 | Zero references to `.specify/` remain in any template file | [X] |
| SC-005 | Zero references to "speckit" remain in any template file | [X] |

## Acceptance Scenarios

### User Story 1 - Remove Legacy Speckit Templates

- [X] Given legacy speckit templates exist in `templates/commands/`, When the cleanup is performed, Then all 9 legacy templates are removed
- [X] Given the cleanup is complete, When a user looks at `templates/commands/`, Then only doit-named templates exist

### User Story 2 - Add Doit Templates to Root Templates

- [X] Given the legacy templates are removed, When doit templates are added, Then `templates/commands/` contains all 9 doit command templates
- [X] Given doit templates are in `templates/commands/`, When comparing to `.doit/templates/commands/`, Then the files match in content

### User Story 3 - Verify Doit Template Quality

- [X] Given templates in `.doit/templates/commands/`, When reviewed for path references, Then all paths reference `.doit/` not `.specify/`
- [X] Given templates are reviewed, When checking structure, Then each template has valid YAML frontmatter and execution outline
