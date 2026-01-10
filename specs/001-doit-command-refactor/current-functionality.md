# Current Speckit Commands - Functionality Analysis

**Created**: 2026-01-09
**Purpose**: Document current speckit command functionality for refactoring to doit

## Overview

The current speckit system consists of **9 commands** defined in `.claude/commands/` as markdown files. These commands follow a sequential workflow for spec-driven development.

---

## Current Command Inventory

### 1. speckit.constitution

**File**: `.claude/commands/speckit.constitution.md` (82 lines)
**Purpose**: Establish project principles and governance rules

**Process Flow**:
1. Load constitution template from `.specify/memory/constitution.md`
2. Collect/derive values for placeholder tokens interactively or from input
3. Fill template with concrete project-specific text
4. Ensure consistency across dependent templates (plan, spec, tasks)
5. Produce sync impact report showing what changed
6. Update version according to semantic versioning

**Outputs**:
- `constitution.md` - Project principles document

**Handoffs To**: `speckit.specify`

---

### 2. speckit.specify

**File**: `.claude/commands/speckit.specify.md` (258 lines)
**Purpose**: Create feature specification from natural language description

**Process Flow**:
1. Generate 2-4 word short name from feature description
2. Check existing branches (remote, local, specs directories)
3. Calculate next feature number (N+1)
4. Run `create-new-feature.sh` to create branch and initialize spec
5. Load spec template from `.specify/templates/spec-template.md`
6. Extract key concepts: actors, actions, data, constraints
7. Make informed guesses for unclear aspects (max 3 clarification markers)
8. Fill User Scenarios & Testing section
9. Generate Functional Requirements (each must be testable)
10. Define Success Criteria (measurable, technology-agnostic)
11. Identify Key Entities if data involved
12. Write spec to `spec.md`
13. Create quality checklist at `checklists/requirements.md`
14. Run validation check against checklist
15. Handle [NEEDS CLARIFICATION] markers if present

**Outputs**:
- `spec.md` - Feature specification
- `checklists/requirements.md` - Quality validation checklist

**Handoffs To**: `speckit.clarify`, `speckit.plan`

---

### 3. speckit.clarify

**File**: `.claude/commands/speckit.clarify.md` (181 lines)
**Purpose**: Identify and resolve underspecified areas in spec via Q&A

**Process Flow**:
1. Run prerequisite check to locate spec file
2. Perform structured ambiguity scan using 8-category taxonomy:
   - Functional Scope & Behavior
   - Domain & Data Model
   - Interaction & UX Flow
   - Non-Functional Quality Attributes
   - Integration & External Dependencies
   - Edge Cases & Failure Handling
   - Constraints & Tradeoffs
   - Terminology & Consistency
3. Generate max 5 prioritized clarification questions
4. Present questions sequentially to user
5. Validate answers and integrate into spec
6. Preserve spec formatting and structure
7. Provide coverage summary report

**Outputs**:
- Updated `spec.md` with clarifications incorporated

**Handoffs To**: `speckit.plan`

---

### 4. speckit.plan

**File**: `.claude/commands/speckit.plan.md` (89 lines)
**Purpose**: Generate technical implementation plan from specification

**Process Flow**:
1. Run `setup-plan.sh` to get feature context
2. Load feature spec and constitution
3. Execute 2-phase planning:
   - **Phase 0: Research** - Resolve unknowns, mark NEEDS CLARIFICATION items
   - **Phase 1: Design & Contracts** - Generate data models, API contracts, agent context
4. Fill plan template from `.specify/templates/plan-template.md`
5. Generate supporting artifacts
6. Update agent context file
7. Re-evaluate constitution compliance post-design

**Outputs**:
- `plan.md` - Implementation plan
- `research.md` - Research findings
- `data-model.md` - Data model definitions
- `contracts/` - API contracts directory
- `quickstart.md` - Quick start guide

**Handoffs To**: `speckit.tasks`, `speckit.checklist`

---

### 5. speckit.checklist

**File**: `.claude/commands/speckit.checklist.md` (294 lines)
**Purpose**: Generate requirement quality validation checklists

**Concept**: Checklists are "unit tests for English specifications" - they validate requirements quality, not implementation correctness

**Process Flow**:
1. Run prerequisite check for feature context
2. Derive up to 3 initial contextual clarifying questions
3. Generate up to 5 checklist items per quality dimension:
   - Requirement Completeness
   - Requirement Clarity
   - Requirement Consistency
   - Acceptance Criteria Quality
   - Scenario Coverage
   - Edge Case Coverage
   - Non-Functional Requirements
   - Dependencies & Assumptions
   - Ambiguities & Conflicts
4. Create checklist files in `checklists/` directory
5. Number items sequentially (CHK001, CHK002, etc.)
6. Provide traceability references
7. Include scenario classification (Primary, Alternate, Exception, Recovery, Non-Functional)

**Outputs**:
- `checklists/[domain].md` - Domain-specific checklists (e.g., ux.md, api.md, security.md)

**Note**: Each run creates NEW file (never overwrites)

---

### 6. speckit.tasks

**File**: `.claude/commands/speckit.tasks.md` (137 lines)
**Purpose**: Generate actionable, dependency-ordered task breakdown

**Process Flow**:
1. Run prerequisite check to get feature directory
2. Load design documents (plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md)
3. Extract tech stack, libraries, user stories with priorities (P1, P2, P3)
4. Map entities to user stories
5. Map endpoints/contracts to user stories
6. Generate phase-based task structure:
   - **Phase 1**: Setup (project initialization)
   - **Phase 2**: Foundational (blocking prerequisites)
   - **Phase 3+**: User Stories (in priority order)
   - **Final Phase**: Polish & cross-cutting concerns
7. Create strict checklist format for each task
8. Calculate parallel execution opportunities
9. Provide independent test criteria per story

**Task Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

**Task Markers**:
- `[P]` - Parallelizable
- `[US1]`, `[US2]` - User story association

**Outputs**:
- `tasks.md` - Task breakdown document

**Handoffs To**: `speckit.analyze`, `speckit.implement`

---

### 7. speckit.analyze

**File**: `.claude/commands/speckit.analyze.md` (184 lines)
**Purpose**: Cross-artifact consistency and quality audit (read-only)

**Operating Mode**: STRICTLY READ-ONLY - outputs analysis report only

**Process Flow**:
1. Run prerequisite check requiring spec.md, plan.md, tasks.md
2. Load all three artifacts progressively
3. Build semantic models:
   - Requirements inventory with stable keys/slugs
   - User story/action inventory
   - Task coverage mapping
   - Constitution rule set
4. Perform 6 detection passes (max 50 findings):
   - **Duplication Detection**
   - **Ambiguity Detection** (vague adjectives, unresolved placeholders)
   - **Underspecification** (missing objects, unmapped items)
   - **Constitution Alignment** (MUST principles compliance)
   - **Coverage Gaps** (orphaned requirements/tasks)
   - **Inconsistency** (terminology drift, contradictions)
5. Assign severity: CRITICAL, HIGH, MEDIUM, LOW

**Outputs**:
- Structured Markdown analysis report with:
  - Finding table (ID, Category, Severity, Location, Summary, Recommendation)
  - Coverage Summary
  - Constitution Alignment Issues
  - Unmapped Tasks
  - Metrics (total requirements, total tasks, coverage %, counts)
  - Next Actions recommendations

**Note**: Does not modify any files

---

### 8. speckit.implement

**File**: `.claude/commands/speckit.implement.md` (135 lines)
**Purpose**: Execute implementation tasks in dependency order

**Process Flow**:
1. Run prerequisite check requiring tasks.md
2. Check checklist completion status (if checklists exist)
   - Create status table showing completion rates
   - Pause if checklists incomplete (user confirmation required)
3. Load full implementation context (tasks.md, plan.md, data-model.md, contracts/, research.md, quickstart.md)
4. Verify project setup:
   - Detect: git repository, Docker, ESLint, Prettier, Terraform, Kubernetes
   - Create/verify ignore files (.gitignore, .dockerignore, .eslintignore, etc.)
   - Add technology-specific patterns
5. Parse tasks.md structure (phases, dependencies, parallel markers)
6. Execute phase-by-phase:
   - Respect sequential vs parallel task execution
   - Follow TDD approach (tests before code)
   - Validate each phase completion
7. Track progress and mark tasks complete `[X]`
8. Report final status with completed work summary

**Technology Support**: Node.js, Python, Java, C#/.NET, Go, Ruby, PHP, Rust, Kotlin, C++, C, Swift, R

**Outputs**:
- Implemented code
- Updated tasks.md with completion markers

---

### 9. speckit.taskstoissues

**File**: `.claude/commands/speckit.taskstoissues.md` (30 lines)
**Purpose**: Convert tasks to GitHub issues

**Process Flow**:
1. Run prerequisite check requiring tasks.md
2. Extract task list from tasks.md
3. Get Git remote URL
4. **CRITICAL**: Only proceed if remote is GitHub URL
5. Create GitHub issues for each task via GitHub MCP server

**Safety Mechanisms**:
- Multiple checks to prevent accidental issue creation in wrong repos
- Never creates issues in repositories that don't match remote URL

**Tools Required**: GitHub MCP server (`github/github-mcp-server/issue_write`)

**Outputs**:
- GitHub issues created for each task

---

## Current Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SPECKIT WORKFLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   constitution   │  ← Establish project principles (FIRST)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     specify      │  ← Create spec from description
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│clarify │ │    plan      │  ← Technical design
└────┬───┘ └──────┬───────┘
     │            │
     └─────┬──────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
┌──────────┐ ┌───────┐
│checklist │ │ tasks │  ← Generate tasks + quality checklists
└────┬─────┘ └───┬───┘
     │           │
     └─────┬─────┘
           │
           ▼
    ┌─────────────┐
    │   analyze   │  ← Cross-artifact audit (optional)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  implement  │  ← Execute tasks
    └──────┬──────┘
           │
           ▼
   ┌───────────────┐
   │ taskstoissues │  ← Sync to GitHub (optional)
   └───────────────┘
```

---

## File Structure

```
.claude/
└── commands/
    ├── speckit.constitution.md
    ├── speckit.specify.md
    ├── speckit.clarify.md
    ├── speckit.plan.md
    ├── speckit.checklist.md
    ├── speckit.tasks.md
    ├── speckit.analyze.md
    ├── speckit.implement.md
    └── speckit.taskstoissues.md

.specify/
├── memory/
│   └── constitution.md          # Project constitution template
├── templates/
│   ├── spec-template.md         # Specification template
│   ├── plan-template.md         # Plan template
│   ├── tasks-template.md        # Tasks template
│   ├── checklist-template.md    # Checklist template
│   └── agent-file-template.md   # Agent context template
└── scripts/
    └── bash/
        ├── create-new-feature.sh
        ├── setup-plan.sh
        ├── check-prerequisites.sh
        └── update-agent-context.sh
```

---

## Summary Statistics

| Command | Lines | Primary Output | Handoffs |
|---------|-------|----------------|----------|
| constitution | 82 | constitution.md | specify |
| specify | 258 | spec.md, checklists/ | clarify, plan |
| clarify | 181 | updated spec.md | plan |
| plan | 89 | plan.md, research.md, data-model.md, contracts/ | tasks, checklist |
| checklist | 294 | checklists/*.md | - |
| tasks | 137 | tasks.md | analyze, implement |
| analyze | 184 | analysis report | - |
| implement | 135 | completed code | - |
| taskstoissues | 30 | GitHub issues | - |

**Total**: 9 commands, 1,390 lines of command definitions
