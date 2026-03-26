---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
effort: high
handoffs:
  - label: Review Implementation
    agent: doit.review
    prompt: Review the implemented code for quality and completeness
    send: true
  - label: Run Tests
    agent: doit.test
    prompt: Execute automated tests and generate test report
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Load Project Context

Before proceeding, load the project context to inform your responses:

```bash
doit context show
```

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:

- Reference constitution principles when making decisions
- Consider roadmap priorities
- Identify connections to related specifications

## Code Quality Guidelines

Before generating or modifying code:

1. **Search for existing implementations** - Use Glob/Grep to find similar functionality before creating new code
2. **Follow established patterns** - Match existing code style, naming conventions, and architecture
3. **Avoid duplication** - Reference or extend existing utilities rather than recreating them
4. **Check imports** - Verify required dependencies already exist in the project

**Context already loaded** (DO NOT read these files again):

- Constitution principles and tech stack
- Roadmap priorities
- Current specification
- Related specifications

## Artifact Storage

- **Temporary scripts**: Save to `.doit/temp/{purpose}-{timestamp}.sh` (or .py/.ps1)
- **Status reports**: Save to `specs/{feature}/reports/{command}-report-{timestamp}.md`
- **Create directories if needed**: Use `mkdir -p` before writing files
- Note: `.doit/temp/` is gitignored - temporary files will not be committed

## Outline

1. Run `.doit/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Check for `--skip-checklist` in $ARGUMENTS - if present, skip checklist verification
   - If not skipped, scan all checklist files in the checklists/ directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 3

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 3

3. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

4. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup:

   **Detection & Creation Logic**:
   - Check if the following command succeeds to determine if the repository is a git repo (create/verify .gitignore if so):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - Check if Dockerfile* exists or Docker in plan.md → create/verify .dockerignore
   - Check if .eslintrc* exists → create/verify .eslintignore
   - Check if eslint.config.* exists → ensure the config's `ignores` entries cover required patterns
   - Check if .prettierrc* exists → create/verify .prettierignore
   - Check if .npmrc or package.json exists → create/verify .npmignore (if publishing)
   - Check if terraform files (*.tf) exist → create/verify .terraformignore
   - Check if .helmignore needed (helm charts present) → create/verify .helmignore

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only
   **If ignore file missing**: Create with full pattern set for detected technology

   **Common Patterns by Technology** (from plan.md tech stack):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **Tool-Specific Patterns**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

6. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together  
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding

7. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

8. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

9. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

10. **Generate Completion Summary Report**:
    - Create a summary showing:

      ```text
      ## Implementation Summary

      **Feature**: [Feature name from spec.md]
      **Branch**: [Current git branch]

      ### Task Completion
      | Phase | Total | Completed | Status |
      |-------|-------|-----------|--------|
      | Setup | X | X | ✓ |
      | Core | X | X | ✓ |
      | ... | ... | ... | ... |

      ### Files Modified
      - [List of files created/modified]

      ### Tests Status
      - Unit tests: X passed, Y failed
      - Integration tests: X passed, Y failed

      ### Next Steps
      - Run `/doit.reviewit` for code review
      - Run `/doit.testit` for full test execution
      ```

    - Output summary to console for immediate feedback

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/doit.taskit` first to regenerate the task list.

---

## Error Recovery

### Missing Task List

The task list needed for implementation was not found.

**ERROR** | If `tasks.md` is not found in the feature specs directory:

1. Check if the file exists: `ls specs/*/tasks.md`
2. If missing, generate it: run `/doit.taskit` to create tasks from the plan
3. If the file exists but in a different directory, verify you're on the correct feature branch: `git branch --show-current`
4. Verify: `ls specs/$(git branch --show-current | sed 's/^[0-9]*-//')/tasks.md` should show the file

> Prevention: Always run `/doit.taskit` before `/doit.implementit`

If the above steps don't resolve the issue: verify the feature branch name matches the spec directory name.

### Task Execution Failure

A task failed during implementation, but your other completed work is safe.

**ERROR** | Your progress IS preserved — completed tasks are saved in `.doit/state/`. If a task fails during execution:

1. Note the failing task ID and error message
2. Check if the failure is due to a missing dependency or file: review the error output
3. Fix the underlying issue (install dependency, correct file path, etc.)
4. Resume implementation — the workflow will continue from the failed task
5. Verify: check the task is now marked complete in `tasks.md`

If the above steps don't resolve the issue: skip the failing task by marking it `[x]` in tasks.md with a comment explaining why, then continue with the next task.

### State File Corruption

The workflow state file has become unreadable or corrupted.

**FATAL** | Your progress in `.doit/state/` may be lost. If the workflow state file is corrupted:

1. Check the state directory: `ls -la .doit/state/`
2. If the JSON state file is unreadable, delete it: `rm .doit/state/workflow-*.json`
3. Review `tasks.md` to identify which tasks are already marked `[x]` (completed)
4. Re-run `/doit.implementit` — it will start from the first unchecked task
5. Verify: `ls .doit/state/` shows a new, valid state file

> Prevention: Avoid manually editing files in `.doit/state/` — let the workflow manage them

If the above steps don't resolve the issue: back up your work with `git stash`, run `doit init` to reinitialize the project state, then `git stash pop` and restart implementation.

### Test Failure During Implementation

Tests are failing while implementing tasks, but you can continue working.

**WARNING** | If tests fail during implementation:

1. Review the test output to identify the failing test and the cause
2. If the test failure is in code you just changed, fix the issue before proceeding
3. If the test failure is pre-existing (not related to your changes), note it and continue
4. Run the specific failing test in isolation: `pytest tests/path/to/test.py -x --tb=short`
5. Verify: `pytest tests/ -x --tb=short` passes for your changed files

> Prevention: Run tests after each task completion rather than waiting until the end

If the above steps don't resolve the issue: run `/doit.testit` for a full test analysis and detailed failure report.

### Interrupted Session

The implementation session was interrupted before all tasks were completed.

**WARNING** | Your progress IS preserved — completed tasks remain marked `[x]` in tasks.md. If the session was interrupted:

1. Check current progress: review `tasks.md` for the last completed task (marked `[x]`)
2. Note the next unchecked task — this is where implementation will resume
3. Re-run `/doit.implementit` — it will automatically continue from the first unchecked task
4. Verify: the previously completed tasks are still marked `[x]` and the next task begins execution

If the above steps don't resolve the issue: manually review `tasks.md` and mark any tasks you know were completed as `[x]`, then re-run.

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (all tasks complete)

Display the following at the end of your output:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────┐
│  Workflow Progress                                          │
│  ● specit → ● planit → ● taskit → ● implementit → ○ checkin │
└─────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.testit` to verify your implementation with tests.

**Alternative**: Run `/doit.reviewit` to request a code review.
```

### On Partial Completion (tasks remaining)

If some tasks are still incomplete:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────┐
│  Workflow Progress                                          │
│  ● specit → ● planit → ● taskit → ◐ implementit → ○ checkin │
└─────────────────────────────────────────────────────────────┘

**Status**: N tasks remaining out of M total.

**Recommended**: Continue with `/doit.implementit` to complete remaining tasks.

**Alternative**: Run `/doit.testit` for partial verification of completed work.
```
