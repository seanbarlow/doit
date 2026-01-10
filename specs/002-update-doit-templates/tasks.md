# Tasks: Update Doit Templates

**Input**: Design documents from `/specs/002-update-doit-templates/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not requested - this is a documentation-only feature.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Documentation files: `.specify/templates/` and `.claude/commands/`

---

## Phase 1: Setup (Verification Baseline)

**Purpose**: Establish baseline for verification

- [x] T001 Run grep to capture current invalid references in .specify/templates/ and .claude/commands/ for comparison

**Checkpoint**: Baseline captured - ready for implementation

---

## Phase 2: User Story 1 - Accurate Command References (Priority: P1)

**Goal**: Update checklist-template.md to remove reference to non-existent `/doit.checklist` command

**Independent Test**: `grep -r "/doit.checklist" .specify/templates/` returns no matches

### Implementation for User Story 1

- [x] T002 [US1] Read .specify/templates/checklist-template.md and identify `/doit.checklist` references
- [x] T003 [US1] Replace `/doit.checklist` with generic checklist note in .specify/templates/checklist-template.md
- [x] T004 [US1] Verify no `/doit.checklist` references remain with grep in .specify/templates/

**Checkpoint**: checklist-template.md references only valid commands

---

## Phase 3: User Story 2 - Remove Non-Existent Command References (Priority: P1)

**Goal**: Update doit.specify.md to remove reference to non-existent `/doit.clarify` command

**Independent Test**: `grep -r "/doit.clarify" .claude/commands/` returns no matches

### Implementation for User Story 2

- [x] T005 [P] [US2] Read .claude/commands/doit.specify.md and identify `/doit.clarify` references
- [x] T006 [US2] Replace `/doit.clarify` with `/doit.plan` in .claude/commands/doit.specify.md
- [x] T007 [US2] Verify no `/doit.clarify` references remain with grep in .claude/commands/

**Checkpoint**: doit.specify.md references only valid commands

---

## Phase 4: User Story 3 - Consistent Path References (Priority: P2)

**Goal**: Update plan-template.md to fix incorrect path reference

**Independent Test**: `grep -r "templates/commands/plan.md" .specify/templates/` returns no matches

### Implementation for User Story 3

- [x] T008 [P] [US3] Read .specify/templates/plan-template.md and identify invalid path references
- [x] T009 [US3] Replace `.specify/templates/commands/plan.md` with `.claude/commands/doit.plan.md` in .specify/templates/plan-template.md
- [x] T010 [US3] Verify no invalid path references remain with grep in .specify/templates/

**Checkpoint**: plan-template.md references only valid paths

---

## Phase 5: Polish & Verification

**Purpose**: Final validation across all files

- [x] T011 Run quickstart.md verification commands to confirm all invalid references removed
- [x] T012 Review all modified files for consistency and formatting

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phases 2-4)**: Depend on Setup for baseline comparison
  - User stories can proceed in parallel (different files)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - modifies checklist-template.md only
- **User Story 2 (P1)**: Independent - modifies doit.specify.md only
- **User Story 3 (P2)**: Independent - modifies plan-template.md only

### Parallel Opportunities

- T002, T005, T008 can run in parallel (reading different files)
- T003, T006, T009 can run in parallel (editing different files)
- T004, T007, T010 can run in parallel (verifying different patterns)

---

## Parallel Example

```bash
# All user story implementations can run in parallel:
Task T003: "Replace /doit.checklist in .specify/templates/checklist-template.md"
Task T006: "Replace /doit.clarify in .claude/commands/doit.specify.md"
Task T009: "Replace invalid path in .specify/templates/plan-template.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline capture)
2. Complete Phase 2: User Story 1 (checklist-template.md)
3. **STOP and VALIDATE**: Verify checklist-template.md works correctly
4. This alone delivers value by fixing one broken reference

### Incremental Delivery

1. Complete Setup → Baseline ready
2. Complete User Story 1 → checklist-template.md fixed
3. Complete User Story 2 → doit.specify.md fixed
4. Complete User Story 3 → plan-template.md fixed
5. Complete Polish → All verified

### Single Developer Strategy

Since all tasks modify different files:
1. Run all read tasks (T002, T005, T008) in parallel
2. Run all edit tasks (T003, T006, T009) in parallel
3. Run all verify tasks (T004, T007, T010) in parallel
4. Complete polish phase

---

## Notes

- All user stories are independent (different files)
- No code compilation or runtime testing needed
- Verification is via grep commands
- Each edit is a simple text replacement
- Total: 12 tasks across 5 phases
