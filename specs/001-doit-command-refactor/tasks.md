# Tasks: Doit Command Refactoring

**Input**: Design documents from `/specs/001-doit-command-refactor/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - manual validation through command execution.

**Organization**: Tasks grouped by user story (US1-US11) for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- All paths are relative to repository root

## Path Conventions

- **Commands**: `.claude/commands/doit.*.md`
- **Scripts**: `.specify/scripts/bash/*.sh`
- **Templates**: `.specify/templates/*.md`
- **Memory**: `.specify/memory/constitution.md`
- **Issue Templates**: `.github/ISSUE_TEMPLATE/*.yml`
- **Python CLI**: `src/specify_cli/__init__.py`

---

## Phase 1: Setup

**Purpose**: Project initialization and directory structure

- [X] T001 Create `.github/ISSUE_TEMPLATE/` directory for issue templates
- [X] T002 [P] Backup existing command files to `.claude/commands/backup/` for reference
- [X] T003 [P] Verify git repository is clean before major refactoring

---

## Phase 2: Foundational - US1 Rename Base Command (Priority: P1) 🎯 MVP

**Goal**: Rename all speckit commands to doit and update all internal references

**Independent Test**: Run `/doit.specify "test"` and verify it executes without speckit references

**⚠️ CRITICAL**: All subsequent user stories depend on this phase being complete

### Command File Renaming

- [X] T004 [P] [US1] Copy speckit.constitution.md to doit.constitution.md in .claude/commands/
- [X] T005 [P] [US1] Copy speckit.specify.md to doit.specify.md in .claude/commands/
- [X] T006 [P] [US1] Copy speckit.plan.md to doit.plan.md in .claude/commands/
- [X] T007 [P] [US1] Copy speckit.tasks.md to doit.tasks.md in .claude/commands/
- [X] T008 [P] [US1] Copy speckit.implement.md to doit.implement.md in .claude/commands/

### Internal Reference Updates

- [X] T009 [US1] Update all "speckit" references to "doit" in doit.constitution.md
- [X] T010 [US1] Update all "speckit" references to "doit" in doit.specify.md
- [X] T011 [US1] Update all "speckit" references to "doit" in doit.plan.md
- [X] T012 [US1] Update all "speckit" references to "doit" in doit.tasks.md
- [X] T013 [US1] Update all "speckit" references to "doit" in doit.implement.md

### Handoff Reference Updates

- [X] T014 [US1] Update handoff agent references in doit.constitution.md (speckit.specify → doit.specify)
- [X] T015 [US1] Update handoff agent references in doit.specify.md (speckit.plan → doit.plan)
- [X] T016 [US1] Update handoff agent references in doit.plan.md (speckit.tasks → doit.tasks)
- [X] T017 [US1] Update handoff agent references in doit.tasks.md (speckit.implement → doit.implement)
- [X] T018 [US1] Update handoff agent references in doit.implement.md

### Script Updates

- [X] T019 [P] [US1] Update speckit references in .specify/scripts/bash/common.sh
- [X] T020 [P] [US1] Update speckit references in .specify/scripts/bash/create-new-feature.sh
- [X] T021 [P] [US1] Update speckit references in .specify/scripts/bash/setup-plan.sh
- [X] T022 [P] [US1] Update speckit references in .specify/scripts/bash/check-prerequisites.sh
- [X] T023 [P] [US1] Update speckit references in .specify/scripts/bash/update-agent-context.sh

### Template Updates

- [X] T024 [P] [US1] Update speckit references in .specify/templates/plan-template.md
- [X] T025 [P] [US1] Update speckit references in .specify/templates/tasks-template.md
- [X] T026 [P] [US1] Update speckit references in .specify/templates/checklist-template.md
- [X] T027 [P] [US1] Update speckit references in .specify/templates/agent-file-template.md

### Python CLI Updates

- [X] T028 [US1] Update project name in pyproject.toml from "specify-cli" to "doit-cli"
- [X] T029 [US1] Update branding references in src/specify_cli/__init__.py

### Old Command Removal

- [X] T030 [US1] Delete speckit.constitution.md from .claude/commands/
- [X] T031 [US1] Delete speckit.specify.md from .claude/commands/
- [X] T032 [US1] Delete speckit.clarify.md from .claude/commands/ (FR-067)
- [X] T033 [US1] Delete speckit.plan.md from .claude/commands/
- [X] T034 [US1] Delete speckit.checklist.md from .claude/commands/ (FR-069)
- [X] T035 [US1] Delete speckit.tasks.md from .claude/commands/
- [X] T036 [US1] Delete speckit.analyze.md from .claude/commands/ (FR-068)
- [X] T037 [US1] Delete speckit.implement.md from .claude/commands/
- [X] T038 [US1] Delete speckit.taskstoissues.md from .claude/commands/ (FR-070)

**Checkpoint**: All commands now use "doit" naming. Test: `/doit.specify "test"` should work.

---

## Phase 3: US8 - Enhanced Constitution Command (Priority: P1)

**Goal**: Add tech stack, infrastructure, and deployment prompts to constitution

**Independent Test**: Run `/doit.constitution` and verify it prompts for purpose, tech stack, and infrastructure

### Constitution Template Enhancement

- [X] T039 [US8] Add Purpose & Goals section to .specify/memory/constitution.md template
- [X] T040 [US8] Add Tech Stack section (languages, frameworks, libraries) to constitution.md template
- [X] T041 [US8] Add Infrastructure section (hosting, cloud provider) to constitution.md template
- [X] T042 [US8] Add Deployment section (CI/CD, strategy) to constitution.md template

### Constitution Command Enhancement

- [X] T043 [US8] Add project purpose prompts to doit.constitution.md (FR-004)
- [X] T044 [US8] Add tech stack prompts (languages) to doit.constitution.md (FR-005)
- [X] T045 [US8] Add frameworks/libraries prompts to doit.constitution.md (FR-006)
- [X] T046 [US8] Add infrastructure prompts to doit.constitution.md (FR-007)
- [X] T047 [US8] Add cloud provider prompts to doit.constitution.md (FR-008)
- [X] T048 [US8] Add deployment strategy prompts to doit.constitution.md (FR-009)
- [X] T049 [US8] Implement section-by-section update capability (FR-011)
- [X] T050 [US8] Add constitution reading utility for other commands (FR-013)

**Checkpoint**: Constitution command captures full project context. Test with new project setup.

---

## Phase 4: US11 - New Scaffold Command (Priority: P1)

**Goal**: Create scaffold command that generates project structure based on tech stack

**Independent Test**: Run `/doit.scaffold` after constitution and verify folder structure created

### Scaffold Command Creation

- [X] T051 [US11] Create doit.scaffold.md command file in .claude/commands/
- [X] T052 [US11] Add YAML frontmatter with description and handoffs
- [X] T053 [US11] Implement constitution reading logic (FR-056)
- [X] T054 [US11] Add tech stack clarification prompts (FR-057)

### Structure Generation Logic

- [X] T055 [US11] Implement React folder structure template in doit.scaffold.md
- [X] T056 [US11] Implement .NET folder structure template in doit.scaffold.md
- [X] T057 [US11] Implement Node.js folder structure template in doit.scaffold.md
- [X] T058 [US11] Implement Python folder structure template in doit.scaffold.md
- [X] T059 [US11] Implement Go folder structure template in doit.scaffold.md
- [X] T060 [US11] Implement Vue folder structure template in doit.scaffold.md
- [X] T061 [US11] Implement Angular folder structure template in doit.scaffold.md
- [X] T062 [US11] Implement Java folder structure template in doit.scaffold.md

### Config and Starter Files

- [X] T063 [US11] Implement config file generation (tsconfig, package.json, etc.) (FR-059)
- [X] T064 [US11] Implement starter file generation (README.md) (FR-060)
- [X] T065 [US11] Implement Dockerfile generation when containerization required (FR-061)
- [X] T066 [US11] Implement .gitignore generation for all tech stacks (FR-062)

### Multi-Stack and Analysis

- [X] T067 [US11] Implement multi-stack project support (frontend + backend) (FR-063)
- [X] T068 [US11] Implement existing project analysis mode (FR-064, FR-065)
- [X] T069 [US11] Add structure analysis report generation

**Checkpoint**: Scaffold generates appropriate structure for React, .NET, Python projects.

---

## Phase 5: US10 - GitHub Issue Templates (Priority: P1)

**Goal**: Create standardized issue templates for Epic, Feature, and Task hierarchy

**Independent Test**: View templates in GitHub UI and verify they render correctly

### Epic Template

- [X] T070 [P] [US10] Create epic.yml in .github/ISSUE_TEMPLATE/ (FR-045)
- [X] T071 [US10] Add Summary field to epic template
- [X] T072 [US10] Add Success Criteria field to epic template
- [X] T073 [US10] Add User Stories links field to epic template
- [X] T074 [US10] Add labels configuration (epic, branch-name) to epic template (FR-052)

### Feature Template

- [X] T075 [P] [US10] Create feature.yml in .github/ISSUE_TEMPLATE/ (FR-046)
- [X] T076 [US10] Add Description field to feature template
- [X] T077 [US10] Add Parent Epic link field to feature template
- [X] T078 [US10] Add Acceptance Scenarios field to feature template
- [X] T079 [US10] Add Priority field to feature template
- [X] T080 [US10] Add labels configuration (feature, priority, epic-link) (FR-053)

### Task Template

- [X] T081 [P] [US10] Create task.yml in .github/ISSUE_TEMPLATE/ (FR-047)
- [X] T082 [US10] Add Description field to task template
- [X] T083 [US10] Add Parent Feature link field to task template
- [X] T084 [US10] Add Definition of Done field to task template
- [X] T085 [US10] Add Estimated Effort field to task template
- [X] T086 [US10] Add labels configuration (task, phase, feature-link) (FR-054)

### Hierarchy Support

- [X] T087 [US10] Add "Part of" section to all templates (FR-051)

**Checkpoint**: All three templates render correctly in GitHub. Test by creating issues.

---

## Phase 6: US2 - Consolidate Specify Command (Priority: P1)

**Goal**: Integrate clarification and analysis into specify command, add issue creation

**Independent Test**: Run `/doit.specify "complex feature"` and verify clarification + issue creation

### Clarification Integration

- [X] T088 [US2] Extract 8-category ambiguity scan logic from speckit.clarify.md
- [X] T089 [US2] Add ambiguity scan to doit.specify.md workflow (FR-015)
- [X] T090 [US2] Add max 5 clarification questions capability (FR-014)
- [X] T091 [US2] Add answer integration logic to update spec draft
- [X] T092 [US2] Ensure no [NEEDS CLARIFICATION] markers in final output (FR-016)

### GitHub Issue Integration

- [X] T093 [US2] Add GitHub remote detection to doit.specify.md
- [X] T094 [US2] Implement Epic issue creation from spec summary (FR-048)
- [X] T095 [US2] Implement Feature issue creation for each user story (FR-049)
- [X] T096 [US2] Add Epic-Feature linking logic
- [X] T097 [US2] Add issue creation skip flag option
- [X] T098 [US2] Add graceful fallback when GitHub unavailable

### Handoff Updates

- [X] T099 [US2] Update handoffs to remove clarify (absorbed)
- [X] T100 [US2] Add handoff to doit.scaffold (optional)

**Checkpoint**: Specify creates spec with clarifications AND Epic/Feature issues.

---

## Phase 7: US3 - Plan Command (Priority: P1)

**Goal**: Update plan command with doit references and constitution integration

**Independent Test**: Run `/doit.plan` on a spec and verify all artifacts generated

- [X] T101 [US3] Verify doit.plan.md generates plan.md correctly (FR-017)
- [X] T102 [US3] Verify research.md generation
- [X] T103 [US3] Verify data-model.md generation
- [X] T104 [US3] Verify contracts/ directory creation
- [X] T105 [US3] Add constitution tech stack reading for architecture alignment (FR-018)
- [X] T106 [US3] Update handoffs to point to doit.tasks

**Checkpoint**: Plan command generates all design artifacts.

---

## Phase 8: US4 - Tasks Command with GitHub Issues (Priority: P1)

**Goal**: Add automatic GitHub issue creation to tasks command

**Independent Test**: Run `/doit.tasks` and verify tasks.md + GitHub issues created

### Issue Creation Integration

- [X] T107 [US4] Add GitHub remote detection to doit.tasks.md
- [X] T108 [US4] Implement Task issue creation for each task (FR-050)
- [X] T109 [US4] Add Feature-Task linking logic (find parent Feature issues)
- [X] T110 [US4] Add --skip-issues flag option (FR-021)
- [X] T111 [US4] Add graceful fallback on GitHub API failure (FR-022)

### Handoff Updates

- [X] T112 [US4] Update handoffs to point to doit.implement

**Checkpoint**: Tasks command creates both tasks.md and GitHub Task issues.

---

## Phase 9: US7 - Implement Command with Checklist Gate (Priority: P2)

**Goal**: Add checklist completion verification before implementation starts

**Independent Test**: Run `/doit.implement` with incomplete checklists and verify warning

- [X] T113 [US7] Add checklist directory scanning to doit.implement.md (FR-033)
- [X] T114 [US7] Implement checklist completion percentage calculation
- [X] T115 [US7] Add checklist status table display
- [X] T116 [US7] Add incomplete checklist warning and confirmation (FR-034)
- [X] T117 [US7] Add --skip-checklist flag option
- [X] T118 [US7] Verify task completion marking works (FR-035)
- [X] T119 [US7] Add completion summary report (FR-036)
- [X] T120 [US7] Add handoff to doit.review

**Checkpoint**: Implement warns on incomplete checklists and requires confirmation.

---

## Phase 10: US5 - New Review Command (Priority: P2)

**Goal**: Create review command for code review and manual testing

**Independent Test**: Run `/doit.review` after implementation and verify findings report

### Review Command Creation

- [X] T121 [US5] Create doit.review.md command file in .claude/commands/
- [X] T122 [US5] Add YAML frontmatter with description and handoffs

### Code Review Logic

- [X] T123 [US5] Implement spec/plan loading for comparison (FR-023)
- [X] T124 [US5] Implement implemented file detection from tasks.md
- [X] T125 [US5] Implement code analysis against requirements
- [X] T126 [US5] Implement findings generation with severity levels (FR-024)
- [X] T127 [US5] Implement findings report formatting

### Manual Testing

- [X] T128 [US5] Implement manual test item extraction from spec (FR-025)
- [X] T129 [US5] Implement sequential manual test presentation
- [X] T130 [US5] Implement test progress tracking (FR-026)
- [X] T131 [US5] Implement sign-off collection (FR-027)
- [X] T132 [US5] Implement review-report.md generation
- [X] T133 [US5] Add handoff to doit.test

**Checkpoint**: Review command performs code review and walks through manual tests.

---

## Phase 11: US6 - New Test Command (Priority: P2)

**Goal**: Create test command for automated test execution and reporting

**Independent Test**: Run `/doit.test` and verify test execution and report generation

### Test Command Creation

- [X] T134 [US6] Create doit.test.md command file in .claude/commands/
- [X] T135 [US6] Add YAML frontmatter with description and handoffs

### Test Detection and Execution

- [X] T136 [US6] Implement test framework detection (pytest, jest, etc.) (FR-028)
- [X] T137 [US6] Implement test suite execution
- [X] T138 [US6] Implement test result capture

### Test Reporting

- [X] T139 [US6] Implement test report generation with pass/fail status (FR-029)
- [X] T140 [US6] Implement requirement mapping (test → FR-XXX) (FR-030)
- [X] T141 [US6] Implement manual testing checklist (FR-031)
- [X] T142 [US6] Implement manual test result recording (FR-032)
- [X] T143 [US6] Implement test-report.md generation
- [X] T144 [US6] Add handoff to doit.checkin

**Checkpoint**: Test command executes tests and generates requirement-mapped report.

---

## Phase 12: US9 - New Checkin Command (Priority: P2)

**Goal**: Create checkin command to finalize feature and create PR

**Independent Test**: Run `/doit.checkin` and verify issues closed, roadmaps updated, PR created

### Checkin Command Creation

- [X] T145 [US9] Create doit.checkin.md command file in .claude/commands/
- [X] T146 [US9] Add YAML frontmatter with description (no handoffs - end of workflow)

### Issue Management

- [X] T147 [US9] Implement GitHub issue retrieval for feature (FR-037)
- [X] T148 [US9] Implement issue completion review
- [X] T149 [US9] Implement incomplete issue confirmation prompt (FR-038)
- [X] T150 [US9] Implement issue closing logic

### Roadmap Updates

- [X] T151 [US9] Implement roadmap_completed.md creation/update (FR-039)
- [X] T152 [US9] Implement roadmap.md update (FR-040)
- [X] T153 [US9] Handle missing roadmap files gracefully

### Documentation and PR

- [X] T154 [US9] Implement feature documentation generation in docs/ (FR-041)
- [X] T155 [US9] Implement git commit with descriptive message (FR-042)
- [X] T156 [US9] Implement PR creation via gh CLI (FR-043)
- [X] T157 [US9] Implement --target flag for alternative branch (FR-044)
- [X] T158 [US9] Implement fallback for missing develop branch
- [X] T159 [US9] Implement fallback for missing gh CLI

**Checkpoint**: Checkin closes issues, updates roadmaps, generates docs, creates PR.

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [X] T160 Validate complete workflow: constitution → scaffold → specify → plan → tasks → implement → review → test → checkin
- [X] T161 [P] Update README.md with new doit command documentation
- [X] T162 [P] Update CLAUDE.md with doit branding
- [X] T163 Verify all 9 commands listed in SC-001 are functional
- [ ] T164 Run end-to-end test creating a sample feature
- [X] T165 [P] Clean up backup files in .claude/commands/backup/
- [ ] T166 Update quickstart.md with validation results

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Setup (Phase 1)
    │
    ▼
Foundational/US1 (Phase 2) ◄── BLOCKS ALL SUBSEQUENT PHASES
    │
    ├──► US8 Constitution (Phase 3)
    │         │
    │         ▼
    │    US11 Scaffold (Phase 4)
    │
    ├──► US10 Issue Templates (Phase 5) ◄── Needed by US2, US4
    │         │
    │         ├──► US2 Specify (Phase 6)
    │         │
    │         └──► US4 Tasks (Phase 8)
    │
    ├──► US3 Plan (Phase 7)
    │
    ├──► US7 Implement (Phase 9)
    │         │
    │         ▼
    │    US5 Review (Phase 10)
    │         │
    │         ▼
    │    US6 Test (Phase 11)
    │         │
    │         ▼
    │    US9 Checkin (Phase 12)
    │
    └──► Polish (Phase 13)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Rename) | None | Phase 1 Setup |
| US8 (Constitution) | US1 | Phase 2 complete |
| US11 (Scaffold) | US8 | Phase 3 complete |
| US10 (Templates) | US1 | Phase 2 complete |
| US2 (Specify) | US1, US10 | Phase 5 complete |
| US3 (Plan) | US1 | Phase 2 complete |
| US4 (Tasks) | US1, US10 | Phase 5 complete |
| US7 (Implement) | US1 | Phase 2 complete |
| US5 (Review) | US7 | Phase 9 complete |
| US6 (Test) | US5 | Phase 10 complete |
| US9 (Checkin) | US6 | Phase 11 complete |

### Parallel Opportunities

**After Phase 2 (Foundational) completes, these can run in parallel**:
- US8 Constitution (Phase 3)
- US10 Issue Templates (Phase 5)
- US3 Plan (Phase 7)
- US7 Implement (Phase 9)

**After Phase 5 (Templates) completes**:
- US2 Specify (Phase 6)
- US4 Tasks (Phase 8)

---

## Implementation Strategy

### MVP First (Phases 1-2 + US8 + US11)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (US1 - Rename)
3. Complete Phase 3: US8 - Enhanced Constitution
4. Complete Phase 4: US11 - Scaffold Command
5. **STOP and VALIDATE**: Core workflow works with doit naming

**MVP Delivers**: Renamed commands + enhanced constitution + scaffold

### Incremental Delivery

1. **MVP** (Phases 1-4): Basic doit workflow
2. **Add Issue Tracking** (Phases 5-8): Templates + Specify + Tasks with issues
3. **Add Quality Commands** (Phases 9-12): Implement gate + Review + Test + Checkin
4. **Polish** (Phase 13): Validation and documentation

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 166 |
| Phase 1 (Setup) | 3 |
| Phase 2 (US1 Foundational) | 35 |
| Phase 3 (US8 Constitution) | 12 |
| Phase 4 (US11 Scaffold) | 19 |
| Phase 5 (US10 Templates) | 18 |
| Phase 6 (US2 Specify) | 13 |
| Phase 7 (US3 Plan) | 6 |
| Phase 8 (US4 Tasks) | 6 |
| Phase 9 (US7 Implement) | 8 |
| Phase 10 (US5 Review) | 13 |
| Phase 11 (US6 Test) | 11 |
| Phase 12 (US9 Checkin) | 15 |
| Phase 13 (Polish) | 7 |

**Parallel Opportunities**: 45 tasks marked [P]

**MVP Scope**: Phases 1-4 (69 tasks) - delivers working doit command set

---

## Notes

- [P] tasks = different files, no dependencies
- [USX] label maps task to specific user story
- Each story delivers independently testable functionality
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Manual testing via command execution is primary validation
