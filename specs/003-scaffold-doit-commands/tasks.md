# Tasks: Scaffold Doit Commands

**Input**: Design documents from `/specs/003-scaffold-doit-commands/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: No automated tests requested - manual verification via quickstart.md commands.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Capture baseline state before changes

- [x] T001 Run pre-implementation verification commands from quickstart.md
- [x] T002 Capture current .specify reference count (expected ~50)

---

## Phase 2: User Story 4 - Rename .specify to .doit (Priority: P1) 🎯 FOUNDATIONAL

**Goal**: Rename the configuration folder from `.specify` to `.doit` for consistent naming

**Independent Test**: `test -d .doit && echo "OK" || echo "FAIL"`

### Implementation for User Story 4

- [x] T003 [US4] Rename .specify/ directory to .doit/ using git mv
- [x] T004 [US4] Update references in .doit/scripts/bash/check-prerequisites.sh
- [x] T005 [US4] Update references in .doit/scripts/bash/common.sh
- [x] T006 [US4] Update references in .doit/scripts/bash/create-new-feature.sh
- [x] T007 [US4] Update references in .doit/scripts/bash/setup-plan.sh
- [x] T008 [US4] Update references in .doit/scripts/bash/update-agent-context.sh
- [x] T009 [P] [US4] Update references in .claude/commands/doit.checkin.md
- [x] T010 [P] [US4] Update references in .claude/commands/doit.constitution.md
- [x] T011 [P] [US4] Update references in .claude/commands/doit.implement.md
- [x] T012 [P] [US4] Update references in .claude/commands/doit.plan.md
- [x] T013 [P] [US4] Update references in .claude/commands/doit.review.md
- [x] T014 [P] [US4] Update references in .claude/commands/doit.scaffold.md
- [x] T015 [P] [US4] Update references in .claude/commands/doit.specify.md
- [x] T016 [P] [US4] Update references in .claude/commands/doit.tasks.md
- [x] T017 [P] [US4] Update references in .claude/commands/doit.test.md
- [x] T018 [P] [US4] Update references in .doit/templates/plan-template.md
- [x] T019 [P] [US4] Update references in .doit/templates/spec-template.md
- [x] T020 [P] [US4] Update references in .doit/templates/tasks-template.md
- [x] T021 [P] [US4] Update references in scripts/bash/check-prerequisites.sh
- [x] T022 [P] [US4] Update references in scripts/bash/create-new-feature.sh
- [x] T023 [P] [US4] Update references in scripts/bash/setup-plan.sh
- [x] T024 [P] [US4] Update references in scripts/bash/update-agent-context.sh
- [x] T025 [P] [US4] Update references in scripts/powershell/check-prerequisites.ps1
- [x] T026 [P] [US4] Update references in scripts/powershell/create-new-feature.ps1
- [x] T027 [P] [US4] Update references in scripts/powershell/setup-plan.ps1
- [x] T028 [P] [US4] Update references in scripts/powershell/update-agent-context.ps1
- [x] T029 [P] [US4] Update references in README.md
- [x] T030 [P] [US4] Update references in CHANGELOG.md
- [x] T031 [P] [US4] Update references in CONTRIBUTING.md
- [x] T032 [P] [US4] Update references in docs/upgrade.md
- [x] T033 [P] [US4] Update references in docs/installation.md
- [x] T034 [P] [US4] Update references in docs/local-development.md
- [x] T035 [P] [US4] Update references in docs/quickstart.md
- [x] T036 [P] [US4] Update references in spec-driven.md
- [x] T037 [P] [US4] Update references in templates/plan-template.md
- [x] T038 [P] [US4] Update references in templates/vscode-settings.json
- [x] T039 [P] [US4] Update references in templates/commands/clarify.md
- [x] T040 [P] [US4] Update references in templates/commands/constitution.md
- [x] T041 [P] [US4] Update references in templates/commands/specify.md
- [x] T042 [P] [US4] Update references in templates/commands/analyze.md
- [x] T043 [P] [US4] Update references in src/specify_cli/__init__.py
- [x] T044 [US4] Update references in CLAUDE.md
- [x] T045 [US4] Verify folder rename with test -d .doit

**Checkpoint**: .doit folder exists, all internal references updated

---

## Phase 3: User Story 2 - Remove Unused Templates (Priority: P1)

**Goal**: Remove templates that are no longer used by any doit command

**Independent Test**: `test -f .doit/templates/agent-file-template.md && echo "FAIL" || echo "OK"`

### Implementation for User Story 2

- [x] T046 [US2] Delete .doit/templates/agent-file-template.md
- [x] T047 [US2] Delete .doit/templates/checklist-template.md
- [x] T048 [US2] Verify 3 templates remain: spec-template.md, plan-template.md, tasks-template.md

**Checkpoint**: Only actively-used templates remain in .doit/templates/

---

## Phase 4: User Story 3 - Add Command Templates for Scaffolding (Priority: P1)

**Goal**: Create command templates that can be copied to new projects during scaffolding

**Independent Test**: `ls .doit/templates/commands/*.md | wc -l` should return 9

### Implementation for User Story 3

- [x] T049 [US3] Create directory .doit/templates/commands/
- [x] T050 [P] [US3] Copy .claude/commands/doit.checkin.md to .doit/templates/commands/doit.checkin.md
- [x] T051 [P] [US3] Copy .claude/commands/doit.constitution.md to .doit/templates/commands/doit.constitution.md
- [x] T052 [P] [US3] Copy .claude/commands/doit.implement.md to .doit/templates/commands/doit.implement.md
- [x] T053 [P] [US3] Copy .claude/commands/doit.plan.md to .doit/templates/commands/doit.plan.md
- [x] T054 [P] [US3] Copy .claude/commands/doit.review.md to .doit/templates/commands/doit.review.md
- [x] T055 [P] [US3] Copy .claude/commands/doit.scaffold.md to .doit/templates/commands/doit.scaffold.md
- [x] T056 [P] [US3] Copy .claude/commands/doit.specify.md to .doit/templates/commands/doit.specify.md
- [x] T057 [P] [US3] Copy .claude/commands/doit.tasks.md to .doit/templates/commands/doit.tasks.md
- [x] T058 [P] [US3] Copy .claude/commands/doit.test.md to .doit/templates/commands/doit.test.md
- [x] T059 [US3] Verify 9 command templates exist in .doit/templates/commands/

**Checkpoint**: All 9 command templates ready for scaffolding

---

## Phase 5: User Story 1 - Scaffold Projects with Doit Commands (Priority: P1)

**Goal**: Update scaffold command to automatically generate doit commands in new projects

**Independent Test**: Scaffold new project and verify 9 commands exist in .claude/commands/

### Implementation for User Story 1

- [x] T060 [US1] Read current .claude/commands/doit.scaffold.md
- [x] T061 [US1] Add command template copying logic to doit.scaffold.md
- [x] T062 [US1] Update scaffold command to create .claude/commands/ in target project
- [x] T063 [US1] Update scaffold command to copy all 9 command templates to target
- [x] T064 [US1] Update scaffold command documentation section

**Checkpoint**: Scaffold command now generates complete doit workflow in new projects

---

## Phase 6: Polish & Verification

**Purpose**: Final verification and cleanup

- [x] T065 Run post-implementation verification commands from quickstart.md
- [x] T066 Verify .specify folder no longer exists
- [x] T067 Verify zero .specify references remain in .claude/ and .doit/ directories
- [x] T068 [P] Update specs/003-scaffold-doit-commands/checklists/requirements.md with completion status
- [x] T069 Final review of all changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - capture baseline first
- **User Story 4 (Phase 2)**: Depends on Setup - FOUNDATIONAL for all other stories
- **User Story 2 (Phase 3)**: Depends on US4 (folder must be renamed first)
- **User Story 3 (Phase 4)**: Depends on US4 (templates go in .doit/)
- **User Story 1 (Phase 5)**: Depends on US3 (templates must exist to copy)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

```text
US4 (Folder Rename) ──┬──► US2 (Remove Templates)
                      │
                      └──► US3 (Add Templates) ──► US1 (Update Scaffold)
```

### Within Each User Story

- File updates within a story marked [P] can run in parallel
- Bash scripts should be updated before commands (to avoid broken paths during testing)
- Verification tasks should run after implementation tasks

### Parallel Opportunities

**Phase 2 (US4) - Maximum Parallelization**:
- T009-T017: All 9 doit command updates can run in parallel
- T018-T020: All 3 template updates can run in parallel
- T021-T028: All 8 root script updates can run in parallel
- T029-T036: All 8 documentation updates can run in parallel
- T037-T043: All legacy templates and source updates can run in parallel

**Phase 4 (US3)**:
- T050-T058: All 9 command template copies can run in parallel

---

## Parallel Example: Phase 2 (US4)

```bash
# Launch all doit command updates together:
Task: "Update references in .claude/commands/doit.checkin.md"
Task: "Update references in .claude/commands/doit.constitution.md"
Task: "Update references in .claude/commands/doit.implement.md"
Task: "Update references in .claude/commands/doit.plan.md"
Task: "Update references in .claude/commands/doit.review.md"
Task: "Update references in .claude/commands/doit.scaffold.md"
Task: "Update references in .claude/commands/doit.specify.md"
Task: "Update references in .claude/commands/doit.tasks.md"
Task: "Update references in .claude/commands/doit.test.md"
```

---

## Implementation Strategy

### MVP First (User Story 4 Only)

1. Complete Phase 1: Setup (baseline)
2. Complete Phase 2: User Story 4 (folder rename)
3. **STOP and VALIDATE**: Verify .doit exists and scripts work
4. Continue with remaining stories

### Full Implementation

1. Phase 1: Setup → Baseline captured
2. Phase 2: US4 → Folder renamed, all references updated
3. Phase 3: US2 → Unused templates removed
4. Phase 4: US3 → Command templates created
5. Phase 5: US1 → Scaffold command updated
6. Phase 6: Polish → All verification passes

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Use `sed` or find-replace for bulk .specify → .doit updates
- Commit after each phase completion
- Total tasks: 69
- Parallel opportunities: 40+ tasks can run in parallel within phases
