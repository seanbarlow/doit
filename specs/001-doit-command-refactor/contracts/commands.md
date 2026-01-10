# Command Interface Contracts

**Branch**: `001-doit-command-refactor` | **Date**: 2026-01-09
**Purpose**: Define input/output contracts for each doit command

## Contract Format

Each command contract specifies:
- **Trigger**: How the command is invoked
- **Input**: Required and optional arguments
- **Prerequisites**: What must exist before command runs
- **Outputs**: Files and artifacts produced
- **Handoffs**: Next commands in workflow
- **Errors**: Error conditions and handling

---

## doit.constitution

**File**: `.claude/commands/doit.constitution.md`

### Trigger
```
/doit.constitution [options]
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --update | flag | No | Update existing constitution instead of creating new |
| --section | string | No | Specific section to update (with --update) |

### Prerequisites
- Git repository initialized
- `.specify/memory/` directory exists

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| constitution.md | `.specify/memory/constitution.md` | Project constitution document |

### Workflow

1. Check for existing constitution
2. If new: Prompt for all sections sequentially
   - Project purpose and goals
   - Core principles (1-5)
   - Tech stack (languages, frameworks, libraries)
   - Infrastructure (hosting, cloud, deployment)
   - Governance rules
3. If update: Load existing, prompt for specified section
4. Validate completeness
5. Write constitution.md
6. Report version and sync status

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Create Project Structure | doit.scaffold | Generate project scaffold |
| Create Feature Spec | doit.specify | Start new feature |

### Errors

| Error | Handling |
|-------|----------|
| No git repository | ERROR: Initialize git first |
| Constitution locked | ERROR: Unlock required |

---

## doit.scaffold

**File**: `.claude/commands/doit.scaffold.md`

### Trigger
```
/doit.scaffold [options]
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --analyze | flag | No | Analyze existing structure without creating |
| --force | flag | No | Overwrite existing files (starter files only) |

### Prerequisites
- Constitution exists with tech stack defined
- Git repository initialized

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Folder structure | Project root | src/, tests/, etc. |
| Config files | Project root | tsconfig.json, package.json, etc. |
| Starter files | Project root | README.md, Dockerfile, etc. |
| .gitignore | Project root | Ignore patterns for tech stack |
| Analysis report | stdout | If --analyze flag used |

### Workflow

1. Load constitution.md
2. Extract tech stack configuration
3. If --analyze:
   - Scan existing structure
   - Compare to best practices
   - Generate report
   - EXIT (no modifications)
4. If new project:
   - Prompt for clarifications if tech stack incomplete
   - Match tech stack to structure template
   - Create folder structure
   - Create config files
   - Create starter files
   - Generate .gitignore
5. Report created artifacts

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Create Feature Spec | doit.specify | Start new feature |

### Errors

| Error | Handling |
|-------|----------|
| No constitution | PROMPT: Run doit.constitution first or answer inline |
| Unsupported tech stack | WARN: Using generic structure |
| Conflicting stacks | PROMPT: Clarify architecture |

---

## doit.specify

**File**: `.claude/commands/doit.specify.md`

### Trigger
```
/doit.specify "<feature description>"
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| description | string | Yes | Natural language feature description |
| --skip-issues | flag | No | Skip GitHub issue creation |

### Prerequisites
- Git repository initialized
- Constitution exists (recommended)

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| spec.md | `specs/<branch>/spec.md` | Feature specification |
| requirements.md | `specs/<branch>/checklists/requirements.md` | Quality checklist |
| Epic issue | GitHub | Epic issue (if GitHub remote) |
| Feature issues | GitHub | Feature issues for each user story |
| Git branch | Local | Feature branch created |

### Workflow

1. Parse feature description
2. Generate short name (2-4 words)
3. Check existing branches
4. Calculate next feature number
5. Create branch and spec directory
6. **Clarification phase**:
   - Perform 8-category ambiguity scan
   - Ask up to 5 clarifying questions
   - Integrate answers
7. Generate spec using template
8. Generate quality checklist
9. Validate no [NEEDS CLARIFICATION] markers
10. If GitHub remote:
    - Create Epic issue from spec summary
    - Create Feature issues for each user story
    - Link Features to Epic
11. Report branch, spec path, issue links

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Build Technical Plan | doit.plan | Create implementation plan |

### Errors

| Error | Handling |
|-------|----------|
| Branch exists | PROMPT: Use existing or increment |
| GitHub API failure | WARN: Continue without issues |
| Empty description | ERROR: Require description |

---

## doit.plan

**File**: `.claude/commands/doit.plan.md`

### Trigger
```
/doit.plan
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --research-only | flag | No | Generate only research.md |

### Prerequisites
- spec.md exists in current feature directory
- Constitution exists (recommended)

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| plan.md | `specs/<branch>/plan.md` | Implementation plan |
| research.md | `specs/<branch>/research.md` | Research findings |
| data-model.md | `specs/<branch>/data-model.md` | Entity definitions |
| contracts/ | `specs/<branch>/contracts/` | Interface specs |
| quickstart.md | `specs/<branch>/quickstart.md` | Dev setup guide |

### Workflow

1. Run setup-plan.sh for context
2. Load spec.md and constitution.md
3. Fill plan template technical context
4. Check constitution compliance
5. **Phase 0 (Research)**:
   - Extract unknowns from technical context
   - Research each unknown
   - Consolidate in research.md
6. **Phase 1 (Design)**:
   - Extract entities from spec → data-model.md
   - Generate API contracts → contracts/
   - Create quickstart.md
   - Update agent context
7. Re-check constitution compliance
8. Report artifacts created

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Generate Tasks | doit.tasks | Create task breakdown |

### Errors

| Error | Handling |
|-------|----------|
| No spec.md | ERROR: Run doit.specify first |
| Constitution violation | ERROR: Justify or resolve |

---

## doit.tasks

**File**: `.claude/commands/doit.tasks.md`

### Trigger
```
/doit.tasks [options]
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --skip-issues | flag | No | Skip GitHub issue creation |
| --dry-run | flag | No | Preview tasks without creating |

### Prerequisites
- plan.md exists
- spec.md exists

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| tasks.md | `specs/<branch>/tasks.md` | Task breakdown |
| Task issues | GitHub | Task issues linked to Features |

### Workflow

1. Load plan.md, spec.md, data-model.md, contracts/
2. Extract tech stack and user stories
3. Map entities and contracts to stories
4. Generate phased task structure:
   - Phase 1: Setup
   - Phase 2: Foundation
   - Phase 3+: User stories (priority order)
   - Final: Polish
5. Calculate parallel opportunities
6. If GitHub remote and not --skip-issues:
   - Find existing Feature issues
   - Create Task issues linked to Features
7. Write tasks.md
8. Report tasks and issue links

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Start Implementation | doit.implement | Execute tasks |

### Errors

| Error | Handling |
|-------|----------|
| No plan.md | ERROR: Run doit.plan first |
| No Feature issues | WARN: Tasks created without parent links |
| GitHub API failure | WARN: Continue with local tasks only |

---

## doit.implement

**File**: `.claude/commands/doit.implement.md`

### Trigger
```
/doit.implement [options]
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --skip-checklist | flag | No | Skip checklist gate (with confirmation) |
| --task | string | No | Specific task ID to implement |

### Prerequisites
- tasks.md exists
- Checklists exist (warning if incomplete)

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Implemented code | Various | Per task specifications |
| Updated tasks.md | `specs/<branch>/tasks.md` | Completion markers |
| Summary report | stdout | Completed work summary |

### Workflow

1. Load tasks.md
2. **Checklist gate**:
   - Check checklists/ for completion status
   - Display status table
   - If incomplete: WARN and require confirmation
3. Load full context (plan, data-model, contracts, quickstart)
4. Verify project setup (git, linters, etc.)
5. Parse task structure
6. Execute phase by phase:
   - Follow dependency order
   - Execute parallel tasks where marked [P]
   - Use TDD approach
   - Mark tasks complete [X] as finished
7. Generate completion summary

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Review Code | doit.review | Perform code review |

### Errors

| Error | Handling |
|-------|----------|
| No tasks.md | ERROR: Run doit.tasks first |
| Dependency not met | ERROR: Complete blocking task first |
| Test failure | WARN: Fix before marking complete |

---

## doit.review

**File**: `.claude/commands/doit.review.md`

### Trigger
```
/doit.review
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --code-only | flag | No | Skip manual testing phase |

### Prerequisites
- Implementation complete (or in progress)
- spec.md, plan.md, tasks.md exist

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| review-report.md | `specs/<branch>/review-report.md` | Review findings |
| Sign-off status | Updated in report | User approval |

### Workflow

1. Load spec.md, plan.md, tasks.md
2. Identify implemented files from tasks.md
3. **Code review phase**:
   - Read implemented code
   - Check each FR is addressed
   - Verify architecture matches plan
   - Check for common issues
   - Generate findings (severity: CRITICAL/HIGH/MEDIUM/LOW)
4. Present findings with recommendations
5. If not --code-only:
   - **Manual testing phase**:
   - Extract manual test items from spec
   - Walk through each test step
   - Record pass/fail for each
6. **Sign-off phase**:
   - Present summary
   - Request explicit sign-off
   - Record approval in report
7. Mark feature as review-complete

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Run Tests | doit.test | Execute test suite |

### Errors

| Error | Handling |
|-------|----------|
| No implementation | WARN: Proceed with partial review |
| Critical findings | BLOCK: Require fixes before sign-off |

---

## doit.test

**File**: `.claude/commands/doit.test.md`

### Trigger
```
/doit.test [options]
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --manual-only | flag | No | Skip automated tests |
| --auto-only | flag | No | Skip manual checklist |

### Prerequisites
- Implementation exists
- Test framework configured (for automated)

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| test-report.md | `specs/<branch>/test-report.md` | Test results |

### Workflow

1. **Detection phase**:
   - Scan project for test framework markers
   - Identify test command
2. If not --manual-only:
   - **Automated testing**:
   - Execute test suite
   - Capture results
   - Map tests to requirements
3. If not --auto-only:
   - **Manual testing**:
   - Extract manual items from spec
   - Present checklist
   - Record pass/fail for each
4. Generate test-report.md
5. Report summary

### Handoffs

| Label | Agent | Description |
|-------|-------|-------------|
| Complete Feature | doit.checkin | Finalize and PR |

### Errors

| Error | Handling |
|-------|----------|
| No test framework | WARN: Skip to manual only |
| Test failures | Report but don't block |

---

## doit.checkin

**File**: `.claude/commands/doit.checkin.md`

### Trigger
```
/doit.checkin [options]
```

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| --target | string | No | Target branch (default: develop) |
| --skip-docs | flag | No | Skip documentation generation |

### Prerequisites
- Implementation complete
- Review complete (recommended)
- Tests passed (recommended)

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Closed issues | GitHub | Associated issues closed |
| roadmap_completed.md | Project root | Updated with feature |
| roadmap.md | Project root | Feature removed |
| Feature docs | `docs/` | Generated documentation |
| Git commit | Local | Changes committed |
| Pull request | GitHub | PR created |

### Workflow

1. **Issue closure**:
   - Find associated GitHub issues
   - Review each for completion
   - Prompt for confirmation on incomplete
   - Close completed issues
2. **Roadmap update**:
   - Add feature to roadmap_completed.md
   - Remove from roadmap.md (if present)
   - Create files if missing
3. If not --skip-docs:
   - **Documentation**:
   - Generate feature documentation
   - Save to docs/
4. **Commit**:
   - Stage all changes
   - Create descriptive commit message
5. **PR creation**:
   - Check target branch exists
   - Push feature branch
   - Create PR via `gh` CLI
   - Report PR URL

### Handoffs

None (workflow complete)

### Errors

| Error | Handling |
|-------|----------|
| Open issues found | PROMPT: Close or abort |
| No develop branch | PROMPT: Alternative target |
| gh CLI missing | WARN: Manual PR instructions |
| PR creation failed | WARN: Commit saved, manual PR |
