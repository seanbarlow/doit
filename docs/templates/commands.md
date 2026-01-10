# Command Templates Documentation

Command templates define the workflow logic for the doit development system. Each command orchestrates a specific phase of the development lifecycle.

## Command Flow Overview

```mermaid
stateDiagram-v2
    [*] --> constitution: Project Setup
    constitution --> scaffold: Generate Structure
    scaffold --> specify: Define Feature
    specify --> plan: Technical Planning
    plan --> tasks: Task Breakdown
    tasks --> implement: Build Feature
    implement --> review: Quality Check
    review --> test: Run Tests
    test --> checkin: Finalize
    checkin --> [*]: Feature Complete

    review --> implement: Fix Issues
    test --> review: Re-review
```

---

## doit.constitution

**Purpose**: Create or update the project constitution with principles, tech stack, and governance

**Phase**: Initialization

**Output**: `.doit/memory/constitution.md`

### Workflow

```mermaid
flowchart TD
    A[Load Constitution Template] --> B{Section Update?}
    B -->|Specific Section| C[Focus on Section]
    B -->|Full Review| D[Review All Sections]
    C --> E[Collect Values]
    D --> E
    E --> F[Fill Placeholders]
    F --> G[Consistency Propagation]
    G --> H[Generate Sync Report]
    H --> I[Write Constitution]
    I --> J[Output Summary]
```

### Sections Managed

| Section | Placeholders | Purpose |
|---------|--------------|---------|
| Purpose & Goals | `[PROJECT_PURPOSE]`, `[SUCCESS_CRITERIA]` | Project mission |
| Tech Stack | `[PRIMARY_LANGUAGE]`, `[FRAMEWORKS]`, `[KEY_LIBRARIES]` | Technology choices |
| Infrastructure | `[HOSTING_PLATFORM]`, `[CLOUD_PROVIDER]`, `[DATABASE]` | Deployment target |
| Deployment | `[CICD_PIPELINE]`, `[DEPLOYMENT_STRATEGY]`, `[ENVIRONMENTS]` | Release process |
| Principles | Custom principle definitions | Project rules |
| Governance | `[CONSTITUTION_VERSION]`, dates | Change management |

### Section Keywords

```text
"purpose" / "goals"      → Purpose & Goals section
"tech" / "stack"         → Tech Stack section
"infrastructure"         → Infrastructure section
"deployment" / "ci"      → Deployment section
"principles"             → Core Principles section
"governance"             → Governance section
```

### Handoffs

- **Next**: `doit.scaffold` - Generate project structure based on tech stack

---

## doit.scaffold

**Purpose**: Generate project folder structure and starter files based on constitution

**Phase**: Initialization

**Output**: Project directories, config files, `.claude/commands/`

### Workflow

```mermaid
flowchart TD
    A[Load Constitution] --> B{Tech Stack Defined?}
    B -->|No| C[Prompt for Stack]
    B -->|Yes| D[Determine Structure]
    C --> D
    D --> E[Generate Directories]
    E --> F[Generate Config Files]
    F --> G[Generate Starter Files]
    G --> H{Docker Required?}
    H -->|Yes| I[Generate Docker Files]
    H -->|No| J[Generate .gitignore]
    I --> J
    J --> K[Copy Doit Commands]
    K --> L[Output Summary]
```

### Supported Tech Stacks

```mermaid
flowchart LR
    subgraph "Frontend"
        REACT[React/TypeScript]
        VUE[Vue.js]
        ANG[Angular]
    end

    subgraph "Backend"
        NODE[Node.js/Express]
        PY[Python/FastAPI]
        DOTNET[.NET/C#]
        GO[Go]
        JAVA[Java/Spring]
    end

    subgraph "Full Stack"
        FS[frontend/ + backend/]
    end
```

### Structure Templates

| Stack | Directories | Config Files |
|-------|-------------|--------------|
| React/TS | `src/components`, `hooks`, `pages` | `tsconfig.json`, `vite.config.ts` |
| Python/FastAPI | `src/api`, `models`, `services` | `pyproject.toml`, `requirements.txt` |
| .NET | `src/Controllers`, `Models`, `Services` | `*.csproj`, `appsettings.json` |
| Node.js | `src/controllers`, `routes`, `middleware` | `package.json`, `.eslintrc.js` |
| Go | `cmd/`, `internal/`, `pkg/` | `go.mod` |

### Doit Commands Generation

Copies all 9 command templates to `.claude/commands/`:

```text
.claude/commands/
├── doit.checkin.md
├── doit.constitution.md
├── doit.implement.md
├── doit.plan.md
├── doit.review.md
├── doit.scaffold.md
├── doit.specify.md
├── doit.tasks.md
└── doit.test.md
```

### Handoffs

- **Next**: `doit.specify` - Create feature specifications

---

## doit.specify

**Purpose**: Create feature specifications from natural language descriptions

**Phase**: Specification

**Output**: `specs/XXX-feature/spec.md`, `specs/XXX-feature/checklists/requirements.md`

### Workflow

```mermaid
flowchart TD
    A[Parse Feature Description] --> B[Generate Short Name]
    B --> C[Check Existing Branches]
    C --> D[Create Feature Branch]
    D --> E[Load Spec Template]
    E --> F[Extract Key Concepts]
    F --> G[Fill User Scenarios]
    G --> H[Generate Requirements]
    H --> I[Define Success Criteria]
    I --> J[Validation Check]
    J --> K{All Valid?}
    K -->|No| L[Fix Issues]
    L --> J
    K -->|Yes| M{Clarifications?}
    M -->|Yes| N[Present Questions]
    N --> O[Update with Answers]
    O --> J
    M -->|No| P[Create Requirements Checklist]
    P --> Q[Create GitHub Issues]
    Q --> R[Report Completion]
```

### Branch Naming

```mermaid
flowchart LR
    FD[Feature Description] --> KW[Extract Keywords]
    KW --> SN[Generate Short Name]
    SN --> NUM[Find Next Number]
    NUM --> BR[Create Branch]

    subgraph "Examples"
        E1["'Add user auth' → 005-user-auth"]
        E2["'Fix payment bug' → 006-fix-payment-bug"]
    end
```

### Ambiguity Scan Categories

1. **Functional Scope & Behavior**
2. **Domain & Data Model**
3. **Interaction & UX Flow**
4. **Non-Functional Quality Attributes**
5. **Integration & External Dependencies**
6. **Edge Cases & Failure Handling**
7. **Constraints & Tradeoffs**
8. **Terminology & Consistency**

### GitHub Integration

Creates issues when remote is available:

```mermaid
flowchart TD
    A[Detect GitHub Remote] --> B{Remote Found?}
    B -->|No| C[Skip Issues]
    B -->|Yes| D[Create Epic Issue]
    D --> E[Create Feature Issues]
    E --> F[Link to Epic]
    F --> G[Report Created Issues]
```

### Handoffs

- **Next**: `doit.plan` - Create technical implementation plan
- **Alt**: `doit.scaffold` - Generate project structure

---

## doit.plan

**Purpose**: Generate implementation plan with technical design artifacts

**Phase**: Planning

**Output**: `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

### Workflow

```mermaid
flowchart TD
    A[Run setup-plan.sh] --> B[Load Spec & Constitution]
    B --> C[Extract Tech Stack]
    C --> D[Constitution Check]
    D --> E{Gates Pass?}
    E -->|No| F[ERROR: Violations]
    E -->|Yes| G[Phase 0: Research]
    G --> H[Resolve Clarifications]
    H --> I[Generate research.md]
    I --> J[Phase 1: Design]
    J --> K[Generate data-model.md]
    K --> L[Generate contracts/]
    L --> M[Generate quickstart.md]
    M --> N[Update Agent Context]
    N --> O[Report Artifacts]
```

### Phase 0: Research Output

```mermaid
flowchart LR
    subgraph "Research Document"
        D[Decision]
        R[Rationale]
        A[Alternatives]
    end

    UN[Technical Unknowns] --> D
    BP[Best Practices] --> R
    EV[Evaluation] --> A
```

### Phase 1: Design Artifacts

| Artifact | Content | Purpose |
|----------|---------|---------|
| `data-model.md` | Entities, fields, relationships | Data structure |
| `contracts/` | OpenAPI/GraphQL schemas | API definitions |
| `quickstart.md` | Setup instructions, test scenarios | Getting started |

### Constitution Check

```mermaid
flowchart TD
    A[Load Constitution] --> B[Extract Principles]
    B --> C{Tech Stack Aligned?}
    C -->|No| D[Flag Deviation]
    C -->|Yes| E[Check Constraints]
    D --> F{Justified?}
    F -->|No| G[ERROR]
    F -->|Yes| E
    E --> H[PASS]
```

### Handoffs

- **Next**: `doit.tasks` - Generate task breakdown

---

## doit.tasks

**Purpose**: Generate actionable, dependency-ordered task list

**Phase**: Task Generation

**Output**: `specs/XXX-feature/tasks.md`

### Workflow

```mermaid
flowchart TD
    A[Run check-prerequisites.sh] --> B[Load Design Documents]
    B --> C[Extract User Stories]
    C --> D[Map Entities to Stories]
    D --> E[Map Contracts to Stories]
    E --> F[Generate Phase Structure]
    F --> G[Create Task List]
    G --> H[Add Dependencies]
    H --> I[Identify Parallel Ops]
    I --> J[Validate Completeness]
    J --> K[Create GitHub Task Issues]
    K --> L[Report Summary]
```

### Task Generation Rules

```mermaid
flowchart TD
    subgraph "Sources"
        SPEC[spec.md - User Stories]
        DM[data-model.md - Entities]
        CON[contracts/ - Endpoints]
        RES[research.md - Decisions]
    end

    subgraph "Task Mapping"
        SPEC --> US[User Story Tasks]
        DM --> MOD[Model Tasks]
        CON --> API[API Tasks]
        RES --> SET[Setup Tasks]
    end

    subgraph "Output"
        US & MOD & API & SET --> TASKS[tasks.md]
    end
```

### Phase Structure

```text
Phase 1: Setup           - Project initialization (no [Story] label)
Phase 2: Foundational    - Blocking prerequisites (no [Story] label)
Phase 3: User Story 1    - P1 implementation ([US1] label)
Phase 4: User Story 2    - P2 implementation ([US2] label)
...
Phase N: Polish          - Cross-cutting concerns (no [Story] label)
```

### Handoffs

- **Next**: `doit.implement` - Execute tasks

---

## doit.implement

**Purpose**: Execute implementation tasks from tasks.md

**Phase**: Implementation

**Output**: Source code, updated tasks.md (marked complete)

### Workflow

```mermaid
flowchart TD
    A[Run check-prerequisites.sh] --> B{Checklists Complete?}
    B -->|No| C[Show Incomplete]
    C --> D{Proceed Anyway?}
    D -->|No| E[HALT]
    D -->|Yes| F[Load Context]
    B -->|Yes| F
    F --> G[Verify Project Setup]
    G --> H[Parse Tasks]
    H --> I[Execute Phase by Phase]
    I --> J{Task Success?}
    J -->|No| K[Report Error]
    J -->|Yes| L[Mark Task Complete]
    L --> M{More Tasks?}
    M -->|Yes| I
    M -->|No| N[Generate Summary]
    N --> O[Report Completion]
```

### Execution Rules

```mermaid
flowchart LR
    subgraph "Sequential"
        S1[T001] --> S2[T002]
        S2 --> S3[T003]
    end

    subgraph "Parallel [P]"
        P1[T004]
        P2[T005]
        P3[T006]
    end

    S3 --> P1 & P2 & P3
```

### Ignore File Generation

| Technology | Ignore File | Key Patterns |
|------------|-------------|--------------|
| Git | `.gitignore` | IDE, build, env |
| Docker | `.dockerignore` | node_modules, .git |
| ESLint | `.eslintignore` | dist, coverage |
| Terraform | `.terraformignore` | .terraform, tfstate |

### Handoffs

- **Next**: `doit.review` - Code review
- **Alt**: `doit.test` - Run tests

---

## doit.review

**Purpose**: Code review and manual testing workflow

**Phase**: Quality Assurance

**Output**: `specs/XXX-feature/review-report.md`

### Workflow

```mermaid
flowchart TD
    A[Load Review Context] --> B[Detect Implemented Files]
    B --> C[Execute Code Review]
    C --> D[Generate Findings]
    D --> E[Extract Manual Tests]
    E --> F[Present Test MT-001]
    F --> G{User Response}
    G -->|PASS/FAIL/SKIP| H[Record Result]
    H --> I{More Tests?}
    I -->|Yes| F
    I -->|No| J[Present Summary]
    J --> K{Sign Off?}
    K -->|Yes| L[Generate Report]
    K -->|No| M[Note Rejection]
    L --> N[Output Report Path]
    M --> N
```

### Finding Severity Levels

```mermaid
flowchart LR
    subgraph "Severity"
        CRIT[CRITICAL]
        MAJ[MAJOR]
        MIN[MINOR]
        INFO[INFO]
    end

    subgraph "Examples"
        CRIT --> C1[Security issue]
        CRIT --> C2[Requirement missing]
        MAJ --> M1[Partial implementation]
        MAJ --> M2[Performance concern]
        MIN --> N1[Code style]
        MIN --> N2[Documentation gap]
        INFO --> I1[Suggestion]
        INFO --> I2[Best practice]
    end
```

### Manual Test Flow

```mermaid
sequenceDiagram
    participant R as Review Command
    participant U as User
    participant Rep as Report

    R->>U: Present MT-001
    U->>R: PASS
    R->>Rep: Record PASS

    R->>U: Present MT-002
    U->>R: FAIL (description)
    R->>Rep: Record FAIL

    R->>U: Present Summary
    U->>R: Sign Off: Yes
    R->>Rep: Generate review-report.md
```

### Handoffs

- **Next**: `doit.test` - Automated tests
- **Next**: `doit.checkin` - Finalize feature

---

## doit.test

**Purpose**: Execute automated tests and generate coverage reports

**Phase**: Quality Assurance

**Output**: `specs/XXX-feature/test-report.md`

### Workflow

```mermaid
flowchart TD
    A[Load Test Context] --> B[Detect Test Framework]
    B --> C{Framework Found?}
    C -->|No| D[Suggest Adding Tests]
    C -->|Yes| E[Execute Test Suite]
    E --> F[Parse Results]
    F --> G[Map to Requirements]
    G --> H[Generate Coverage Matrix]
    H --> I[Create Manual Checklist]
    I --> J{--manual flag?}
    J -->|Yes| K[Execute Manual Tests]
    J -->|No| L[Output Checklist]
    K --> M[Generate Report]
    L --> M
    M --> N[Report Summary]
```

### Framework Detection

| Framework | Detection Files | Command |
|-----------|-----------------|---------|
| pytest | `pytest.ini`, `conftest.py` | `pytest -v --tb=short` |
| Jest | `jest.config.js` | `npm test` |
| Vitest | `vitest.config.ts` | `npx vitest run` |
| Go | `*_test.go` | `go test ./...` |
| Maven | `pom.xml` | `mvn test` |
| Cargo | `Cargo.toml` | `cargo test` |

### Requirement Coverage Matrix

```mermaid
flowchart LR
    subgraph "Mapping"
        T1[test_login] --> FR001[FR-001]
        T2[test_auth] --> FR001
        T3[test_session] --> FR003[FR-003]
    end

    subgraph "Status"
        FR001 --> COV[COVERED]
        FR002[FR-002] --> NOT[NOT COVERED]
        FR003 --> COV
    end
```

### Handoffs

- **Next**: `doit.checkin` - Finalize feature
- **Alt**: `doit.review` - Re-review after fixes

---

## doit.checkin

**Purpose**: Finalize feature, close issues, create pull request

**Phase**: Completion

**Output**: Feature documentation, PR, closed issues

### Workflow

```mermaid
flowchart TD
    A[Load Checkin Context] --> B[Retrieve GitHub Issues]
    B --> C[Review Issue Status]
    C --> D{Issues Open?}
    D -->|Yes| E[Prompt to Close]
    E --> F{User Approves?}
    F -->|Yes| G[Close Issues]
    F -->|No| H[Keep Open]
    D -->|No| I[Update Roadmap]
    G --> I
    H --> I
    I --> J[Generate Feature Doc]
    J --> K[Prepare Commit]
    K --> L{gh CLI Available?}
    L -->|Yes| M[Create PR]
    L -->|No| N[Manual Instructions]
    M --> O[Report Summary]
    N --> O
```

### Roadmap Updates

```mermaid
flowchart LR
    subgraph "Input"
        SPEC[spec.md]
        TASKS[tasks.md]
        REV[review-report.md]
    end

    subgraph "Updates"
        RM[roadmap.md - Mark Complete]
        RC[roadmap_completed.md - Add Entry]
        DOC[docs/features/XXX.md - Create]
    end

    SPEC --> RM & RC & DOC
    TASKS --> DOC
    REV --> DOC
```

### PR Template Structure

```markdown
## Summary
[Brief description from spec.md]

## Changes
- [List of key changes]

## Testing
- [ ] Automated tests pass
- [ ] Manual testing complete
- [ ] Code review approved

## Requirements
| ID | Description | Status |
|----|-------------|--------|
| FR-XXX | ... | Done |

## Related Issues
Closes #XXX, #YYY, #ZZZ
```

### Fallback Handling

| Scenario | Action |
|----------|--------|
| No gh CLI | Output manual PR instructions |
| No develop branch | Check main/master |
| No GitHub remote | Skip issue management |
| API failure | Log error, continue with local operations |

---

## Command Dependencies Summary

```mermaid
flowchart TD
    subgraph "Independent"
        CONST[constitution]
    end

    subgraph "Requires Constitution"
        SCAFFOLD[scaffold]
    end

    subgraph "Requires Spec"
        PLAN[plan]
    end

    subgraph "Requires Plan"
        TASKS[tasks]
    end

    subgraph "Requires Tasks"
        IMPL[implement]
    end

    subgraph "Requires Implementation"
        REV[review]
        TEST[test]
    end

    subgraph "Requires QA"
        CHECK[checkin]
    end

    CONST --> SCAFFOLD
    SCAFFOLD --> SPECIFY[specify]
    SPECIFY --> PLAN
    PLAN --> TASKS
    TASKS --> IMPL
    IMPL --> REV & TEST
    REV & TEST --> CHECK
```
