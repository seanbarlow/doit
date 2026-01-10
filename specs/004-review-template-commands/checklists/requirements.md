# Requirements Checklist: Review Template Commands

**Feature**: 004-review-template-commands
**Created**: 2026-01-10
**Status**: Draft

## Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | System MUST remove all legacy speckit templates from `templates/commands/` directory | P1 | [ ] |
| FR-002 | System MUST copy all 9 doit command templates to `templates/commands/` after cleanup | P1 | [ ] |
| FR-003 | Templates in `templates/commands/` MUST match templates in `.doit/templates/commands/` | P1 | [ ] |
| FR-004 | All templates MUST reference `.doit/` paths, not `.specify/` paths | P1 | [ ] |
| FR-005 | All templates MUST have valid YAML frontmatter with description field | P2 | [ ] |
| FR-006 | The doit.scaffold.md template MUST reference the correct template source paths | P2 | [ ] |

## Files to Remove

| File | Status |
|------|--------|
| templates/commands/analyze.md | [ ] |
| templates/commands/checklist.md | [ ] |
| templates/commands/clarify.md | [ ] |
| templates/commands/constitution.md | [ ] |
| templates/commands/implement.md | [ ] |
| templates/commands/plan.md | [ ] |
| templates/commands/specify.md | [ ] |
| templates/commands/tasks.md | [ ] |
| templates/commands/taskstoissues.md | [ ] |

## Files to Add

| File | Status |
|------|--------|
| templates/commands/doit.checkin.md | [ ] |
| templates/commands/doit.constitution.md | [ ] |
| templates/commands/doit.implement.md | [ ] |
| templates/commands/doit.plan.md | [ ] |
| templates/commands/doit.review.md | [ ] |
| templates/commands/doit.scaffold.md | [ ] |
| templates/commands/doit.specify.md | [ ] |
| templates/commands/doit.tasks.md | [ ] |
| templates/commands/doit.test.md | [ ] |

## Success Criteria

| ID | Criterion | Status |
|----|-----------|--------|
| SC-001 | Zero legacy speckit templates remain in `templates/commands/` | [ ] |
| SC-002 | 9 doit command templates exist in `templates/commands/` | [ ] |
| SC-003 | All templates in `templates/commands/` match their counterparts in `.doit/templates/commands/` | [ ] |
| SC-004 | Zero references to `.specify/` remain in any template file | [ ] |
| SC-005 | Zero references to "speckit" remain in any template file | [ ] |

## Acceptance Scenarios

### User Story 1 - Remove Legacy Speckit Templates
- [ ] Given legacy speckit templates exist in `templates/commands/`, When the cleanup is performed, Then all 9 legacy templates are removed
- [ ] Given the cleanup is complete, When a user looks at `templates/commands/`, Then only doit-named templates exist

### User Story 2 - Add Doit Templates to Root Templates
- [ ] Given the legacy templates are removed, When doit templates are added, Then `templates/commands/` contains all 9 doit command templates
- [ ] Given doit templates are in `templates/commands/`, When comparing to `.doit/templates/commands/`, Then the files match in content

### User Story 3 - Verify Doit Template Quality
- [ ] Given templates in `.doit/templates/commands/`, When reviewed for path references, Then all paths reference `.doit/` not `.specify/`
- [ ] Given templates are reviewed, When checking structure, Then each template has valid YAML frontmatter and execution outline
