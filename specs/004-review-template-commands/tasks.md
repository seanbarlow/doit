# Tasks: Review Template Commands

**Input**: Design documents from `/specs/004-review-template-commands/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: Not explicitly requested - no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **File operations**: `templates/commands/` (target), `.doit/templates/commands/` (source)

---

## Phase 1: Setup (Baseline Verification)

**Purpose**: Verify current state before making changes

- [X] T001 Run baseline verification: count legacy templates in templates/commands/ (expect 9)
- [X] T002 Verify source doit templates exist in .doit/templates/commands/ (expect 9)
- [X] T003 Document speckit reference count in legacy templates (expect 8 files with references)

**Checkpoint**: Baseline documented - ready for template cleanup

---

## Phase 2: Foundational (Not Required)

**Purpose**: No blocking prerequisites for this feature

This feature has no foundational tasks - file operations can proceed directly after baseline verification.

---

## Phase 3: User Story 1 - Remove Legacy Speckit Templates (Priority: P1) MVP

**Goal**: Remove all 9 legacy speckit templates from `templates/commands/` to eliminate confusion and outdated references.

**Independent Test**: `ls templates/commands/` should show no files with speckit-style names (analyze.md, clarify.md, etc.)

### Implementation for User Story 1

- [X] T004 [P] [US1] Remove templates/commands/analyze.md
- [X] T005 [P] [US1] Remove templates/commands/checklist.md
- [X] T006 [P] [US1] Remove templates/commands/clarify.md
- [X] T007 [P] [US1] Remove templates/commands/constitution.md
- [X] T008 [P] [US1] Remove templates/commands/implement.md
- [X] T009 [P] [US1] Remove templates/commands/plan.md
- [X] T010 [P] [US1] Remove templates/commands/specify.md
- [X] T011 [P] [US1] Remove templates/commands/tasks.md
- [X] T012 [P] [US1] Remove templates/commands/taskstoissues.md
- [X] T013 [US1] Verify templates/commands/ is empty or contains no legacy files

**Checkpoint**: All legacy templates removed - directory ready for doit templates

---

## Phase 4: User Story 2 - Add Doit Templates (Priority: P1)

**Goal**: Copy all 9 doit command templates from `.doit/templates/commands/` to `templates/commands/` for distribution.

**Independent Test**: `ls templates/commands/doit.*.md | wc -l` should return 9

### Implementation for User Story 2

- [X] T014 [P] [US2] Copy .doit/templates/commands/doit.checkin.md to templates/commands/
- [X] T015 [P] [US2] Copy .doit/templates/commands/doit.constitution.md to templates/commands/
- [X] T016 [P] [US2] Copy .doit/templates/commands/doit.implement.md to templates/commands/
- [X] T017 [P] [US2] Copy .doit/templates/commands/doit.plan.md to templates/commands/
- [X] T018 [P] [US2] Copy .doit/templates/commands/doit.review.md to templates/commands/
- [X] T019 [P] [US2] Copy .doit/templates/commands/doit.scaffold.md to templates/commands/
- [X] T020 [P] [US2] Copy .doit/templates/commands/doit.specify.md to templates/commands/
- [X] T021 [P] [US2] Copy .doit/templates/commands/doit.tasks.md to templates/commands/
- [X] T022 [P] [US2] Copy .doit/templates/commands/doit.test.md to templates/commands/
- [X] T023 [US2] Verify all 9 doit templates present in templates/commands/
- [X] T024 [US2] Verify file contents match source (diff -q check)

**Checkpoint**: All doit templates copied and verified - distribution templates ready

---

## Phase 5: User Story 3 - Verify Template Quality (Priority: P2)

**Goal**: Verify all templates reference correct paths and have valid structure.

**Independent Test**: `grep -r ".specify/" templates/commands/` returns no results; all templates have YAML frontmatter

### Implementation for User Story 3

- [X] T025 [US3] Verify zero ".specify/" references in templates/commands/
- [X] T026 [US3] Verify zero "speckit" references in templates/commands/
- [X] T027 [US3] Verify all templates have valid YAML frontmatter with description field
- [X] T028 [US3] Verify doit.scaffold.md references correct template source paths

**Checkpoint**: Template quality verified - all success criteria met

---

## Phase 6: Polish & Final Verification

**Purpose**: Final checks and cleanup

- [X] T029 Run full quickstart.md verification suite
- [X] T030 Update specs/004-review-template-commands/checklists/requirements.md - mark completed items
- [X] T031 Commit all changes with descriptive message

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **US1 (Phase 3)**: Depends on Setup completion
- **US2 (Phase 4)**: Depends on US1 completion (must remove before copy)
- **US3 (Phase 5)**: Depends on US2 completion (must have files to verify)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup - No dependencies on other stories
- **User Story 2 (P1)**: Must wait for US1 (directory must be clean before copy)
- **User Story 3 (P2)**: Must wait for US2 (must have templates to verify)

### Parallel Opportunities

**Within US1 (9 parallel deletions)**:

```text
All T004-T012 can execute in parallel (different files)
```

**Within US2 (9 parallel copies)**:

```text
All T014-T022 can execute in parallel (different files)
```

**Note**: US1 and US2 cannot run in parallel (sequential dependency).

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup (verify baseline)
2. Complete Phase 3: US1 - Remove all legacy templates (parallel)
3. Complete Phase 4: US2 - Copy all doit templates (parallel)
4. **STOP and VALIDATE**: Verify file counts and content match
5. Ready for review

### Full Implementation

1. Complete MVP (US1 + US2)
2. Complete Phase 5: US3 - Verify template quality
3. Complete Phase 6: Polish and commit

### Execution Time Estimate

- Phase 1: ~1 minute (verification commands)
- Phase 3: ~1 minute (9 file deletions)
- Phase 4: ~1 minute (9 file copies)
- Phase 5: ~2 minutes (grep/validation commands)
- Phase 6: ~2 minutes (verification and commit)
- **Total**: ~7 minutes

---

## Notes

- All [P] tasks within same phase can run in parallel
- File operations are atomic - no partial state risk
- Rollback available via `git checkout HEAD -- templates/commands/`
- Commit after each checkpoint for safety
