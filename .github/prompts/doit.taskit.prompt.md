# Doit Taskit

Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.

## User Input

Consider any arguments or options the user provides.

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

## Outline

1. **Setup**: Run `.doit/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map endpoints to user stories
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate task completeness (each user story has all needed tasks, independently testable)

4. **Generate tasks.md**: Use `.doit/templates/tasks-template.md` as structure, fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing story completion order
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

5. **Generate Mermaid Visualizations** (FR-008, FR-009, FR-010):

   After generating the task list, create visual diagrams to show execution order and timelines:

   a. **Task Dependencies Flowchart**:
      - Parse all generated tasks and their dependencies
      - Identify parallel tasks (marked with [P])
      - Group tasks by phase using subgraphs
      - Generate flowchart showing task execution order
      - Use `&` syntax for parallel tasks: `T003 --> T004 & T005`
      - Replace content in `<!-- BEGIN:AUTO-GENERATED section="task-dependencies" -->` markers

      ```mermaid
      flowchart TD
          subgraph "Phase 1: Setup"
              T001[T001: Project init]
          end

          subgraph "Phase 2: Foundation"
              T002[T002: Dependencies]
              T003[T003: Core setup]
          end

          subgraph "Phase 3: US1"
              T004[T004: Model A]
              T005[T005: Model B]
              T006[T006: Service]
          end

          T001 --> T002 --> T003
          T003 --> T004 & T005
          T004 & T005 --> T006
      ```

   b. **Phase Timeline Gantt Chart**:
      - Extract phases and their task counts
      - Estimate duration based on task complexity (1 task ≈ 0.5-1 day)
      - Generate gantt chart showing phase timeline
      - Use `after` syntax for dependencies
      - Replace content in `<!-- BEGIN:AUTO-GENERATED section="phase-timeline" -->` markers

      ```mermaid
      gantt
          title Implementation Phases
          dateFormat YYYY-MM-DD

          section Phase 1: Setup
          Project initialization    :a1, 2024-01-01, 1d

          section Phase 2: Foundation
          Core infrastructure       :b1, after a1, 2d

          section Phase 3: US1 (P1)
          User Story 1 implementation :c1, after b1, 3d

          section Phase 4: US2 (P2)
          User Story 2 implementation :d1, after c1, 2d

          section Final: Polish
          Cross-cutting concerns    :e1, after d1, 1d
      ```

   c. **Parallel Task Detection**:
      - Scan all tasks for [P] markers
      - Group consecutive parallel tasks for diagram optimization
      - In flowchart: Connect parallel tasks with `&` syntax
      - Add legend note: "[P] = Can run in parallel"

   d. **Diagram Validation**:
      - Verify mermaid syntax is valid
      - Check task count per subgraph (max 15 per phase)
      - If exceeding limits, group smaller tasks into summary nodes
      - Ensure all task IDs in diagram match task list

6. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

7. **GitHub Issue Integration**:
   - Check for `--skip-issues` in the user's input - if present, skip issue creation
   - Detect GitHub remote: `git remote get-url origin`
   - If GitHub remote found and not skipped:
     - For each generated task, create a GitHub Task issue using the task.yml template
     - Find parent Feature issues by searching for feature labels matching current spec
     - Link Task issues to parent Feature using "Part of Feature #XXX" in body
     - Add phase label (e.g., "Phase 3 - Core Implementation")
     - Add effort estimate if extractable from task description
   - If GitHub unavailable or API fails: Log warning and continue without issues
   - Report: Number of issues created, any linking errors

Context for task generation: the user's input

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: REQUIRED for user story phase tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - Setup phase: NO story label
   - Foundational phase: NO story label  
   - User Story phases: MUST have story label
   - Polish phase: NO story label
5. **Description**: Clear action with exact file path

**Examples**:

- ✅ CORRECT: `- [ ] T001 Create project structure per implementation plan`
- ✅ CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ WRONG: `- [ ] Create User model` (missing ID and Story label)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)
- ❌ WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- ❌ WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase
   - Map all related components to their story:
     - Models needed for that story
     - Services needed for that story
     - Endpoints/UI needed for that story
     - If tests requested: Tests specific to that story
   - Mark story dependencies (most stories should be independent)

2. **From Contracts**:
   - Map each contract/endpoint → to the user story it serves
   - If tests requested: Each contract → contract test task [P] before implementation in that story's phase

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it
   - If entity serves multiple stories: Put in earliest story or Setup phase
   - Relationships → service layer tasks in appropriate story phase

4. **From Setup/Infrastructure**:
   - Shared infrastructure → Setup phase (Phase 1)
   - Foundational/blocking tasks → Foundational phase (Phase 2)
   - Story-specific setup → within that story's phase

### Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Each phase should be a complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (tasks generated)

Display the following at the end of your output:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────┐
│  Workflow Progress                                          │
│  ● specit → ● planit → ● taskit → ○ implementit → ○ checkin │
└─────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.implementit` to start executing the implementation tasks.
```

### On Error (missing plan.md)

If the command fails because plan.md is not found:

```markdown
---

## Next Steps

**Issue**: No implementation plan found. The taskit command requires plan.md to exist.

**Recommended**: Run `/doit.planit` to create an implementation plan first.
```

### On Error (missing spec.md)

If the command fails because spec.md is not found:

```markdown
---

## Next Steps

**Issue**: No feature specification found.

**Recommended**: Run `/doit.specit [feature description]` to create a feature specification first.
```

### On Error (other issues)

If the command fails for another reason:

```markdown
---

## Next Steps

**Issue**: [Brief description of what went wrong]

**Recommended**: [Specific recovery action based on the error]
```
