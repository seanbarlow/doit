# Root Templates Documentation

Root templates define the structure and format of generated documentation artifacts. They serve as blueprints that command templates fill in during workflow execution.

## Template Relationships

```mermaid
flowchart TD
    subgraph "Templates"
        ST[spec-template.md]
        PT[plan-template.md]
        TT[tasks-template.md]
        CT[checklist-template.md]
        AT[agent-file-template.md]
    end

    subgraph "Generated Artifacts"
        SPEC[spec.md]
        PLAN[plan.md]
        TASKS[tasks.md]
        CL[requirements.md]
        CLAUDE[CLAUDE.md]
    end

    ST -->|"doit.specify"| SPEC
    PT -->|"doit.plan"| PLAN
    TT -->|"doit.tasks"| TASKS
    CT -->|"doit.specify"| CL
    AT -->|"doit.plan"| CLAUDE

    SPEC --> PLAN
    PLAN --> TASKS
```

---

## spec-template.md

**Purpose**: Defines the structure for feature specifications

**Used By**: `/doit.specit` command

**Output**: `specs/XXX-feature-name/spec.md`

### Structure

```mermaid
flowchart TD
    subgraph "Specification Structure"
        H[Header & Metadata]
        US[User Scenarios & Testing]
        REQ[Requirements]
        SC[Success Criteria]
    end

    H --> US
    US --> REQ
    REQ --> SC

    subgraph "User Scenarios Detail"
        US1[User Story 1 - P1]
        US2[User Story 2 - P2]
        US3[User Story N - PN]
        EC[Edge Cases]
    end

    US --> US1 & US2 & US3 & EC
```

### Key Sections

| Section | Purpose | Required |
|---------|---------|----------|
| Header | Feature name, branch, status, date | Yes |
| User Scenarios | Prioritized user journeys with acceptance criteria | Yes |
| Functional Requirements | FR-XXX formatted requirements | Yes |
| Key Entities | Data entities (if applicable) | Conditional |
| Success Criteria | Measurable outcomes | Yes |

### User Story Format

Each user story follows this structure:

```markdown
### User Story N - [Title] (Priority: PN)

[Description]

**Why this priority**: [Justification]

**Independent Test**: [How to verify independently]

**Acceptance Scenarios**:
1. **Given** [state], **When** [action], **Then** [outcome]
```

### Guidelines

- **Focus on WHAT and WHY**, not HOW
- Requirements must be testable and unambiguous
- Success criteria must be technology-agnostic
- Maximum 3 `[NEEDS CLARIFICATION]` markers allowed
- Each user story should be independently deliverable

---

## plan-template.md

**Purpose**: Defines the implementation plan structure

**Used By**: `/doit.planit` command

**Output**: `specs/XXX-feature-name/plan.md`

### Structure

```mermaid
flowchart TD
    subgraph "Plan Structure"
        H[Header & Summary]
        TC[Technical Context]
        CC[Constitution Check]
        PS[Project Structure]
        CT[Complexity Tracking]
    end

    H --> TC --> CC --> PS --> CT

    subgraph "Technical Context"
        LANG[Language/Version]
        DEPS[Dependencies]
        STORE[Storage]
        TEST[Testing]
        PLAT[Platform]
    end

    TC --> LANG & DEPS & STORE & TEST & PLAT
```

### Key Sections

| Section | Purpose | Required |
|---------|---------|----------|
| Header | Branch, date, spec link | Yes |
| Summary | Primary requirement + technical approach | Yes |
| Technical Context | Tech stack details | Yes |
| Constitution Check | Gate validation | Yes |
| Project Structure | Directory layout | Yes |
| Complexity Tracking | Justifications for violations | Conditional |

### Technical Context Fields

```markdown
**Language/Version**: [e.g., Python 3.11]
**Primary Dependencies**: [e.g., FastAPI, Pydantic]
**Storage**: [e.g., PostgreSQL or N/A]
**Testing**: [e.g., pytest]
**Target Platform**: [e.g., Linux server]
**Project Type**: [single/web/mobile]
**Performance Goals**: [domain-specific]
**Constraints**: [specific limitations]
**Scale/Scope**: [expected volume]
```

### Project Structure Options

The template supports three structure options:

```mermaid
flowchart LR
    subgraph "Option 1: Single Project"
        S1[src/]
        T1[tests/]
    end

    subgraph "Option 2: Web App"
        BE[backend/]
        FE[frontend/]
    end

    subgraph "Option 3: Mobile + API"
        API[api/]
        IOS[ios/]
        AND[android/]
    end
```

---

## tasks-template.md

**Purpose**: Defines the task breakdown structure

**Used By**: `/doit.taskit` command

**Output**: `specs/XXX-feature-name/tasks.md`

### Structure

```mermaid
flowchart TD
    subgraph "Task Phases"
        P1[Phase 1: Setup]
        P2[Phase 2: Foundational]
        P3[Phase 3: User Story 1]
        P4[Phase 4: User Story 2]
        PN[Phase N: Polish]
    end

    P1 --> P2
    P2 --> P3 & P4
    P3 --> PN
    P4 --> PN

    subgraph "Task Format"
        CB[Checkbox]
        ID[Task ID]
        PM[Parallel Marker]
        SL[Story Label]
        DESC[Description + Path]
    end
```

### Task Format

```text
- [ ] T001 [P] [US1] Description with exact/file/path.py
```

| Component | Description | Example |
|-----------|-------------|---------|
| Checkbox | `- [ ]` for pending, `- [X]` for complete | `- [ ]` |
| Task ID | Sequential identifier | `T001` |
| [P] | Parallel marker (optional) | `[P]` |
| [Story] | User story reference | `[US1]` |
| Description | Action with file path | `Create User model in src/models/user.py` |

### Phase Organization

```mermaid
flowchart TD
    subgraph "Phase 1: Setup"
        T1[Project structure]
        T2[Dependencies]
        T3[Configuration]
    end

    subgraph "Phase 2: Foundational"
        T4[Database schema]
        T5[Auth framework]
        T6[Base models]
    end

    subgraph "Phase 3+: User Stories"
        T7[Tests - if requested]
        T8[Models]
        T9[Services]
        T10[Endpoints]
    end

    subgraph "Final Phase: Polish"
        T11[Documentation]
        T12[Cleanup]
        T13[Validation]
    end
```

### Parallel Execution Rules

- Tasks marked `[P]` can run concurrently
- Tasks affecting the same file must run sequentially
- User stories can be worked in parallel after foundational phase

---

## checklist-template.md

**Purpose**: Generic checklist format for validation

**Used By**: `/doit.specit` (requirements checklist)

**Output**: Various checklist files in `specs/XXX/checklists/`

### Structure

```markdown
# [CHECKLIST TYPE] Checklist: [FEATURE NAME]

**Purpose**: [Description]
**Created**: [DATE]
**Feature**: [Link to spec.md]

## [Category 1]

- [ ] CHK001 First checklist item
- [ ] CHK002 Second checklist item

## [Category 2]

- [ ] CHK003 Category item
- [ ] CHK004 Another item

## Notes

- Additional guidance
```

### Usage Patterns

| Checklist Type | Purpose | Generated By |
|----------------|---------|--------------|
| Requirements | Spec quality validation | doit.specify |
| Code Review | Implementation review | doit.review |
| Manual Test | Testing verification | doit.test |

---

## agent-file-template.md

**Purpose**: AI agent context file structure

**Used By**: `/doit.planit` command

**Output**: `CLAUDE.md` (or equivalent agent file)

### Structure

```markdown
# [PROJECT NAME] Development Guidelines

Auto-generated from all feature plans. Last updated: [DATE]

## Active Technologies

[Extracted from plan files]

## Project Structure

```text
[Actual structure from plans]
```

## Commands

[Only commands for active technologies]

## Code Style

[Language-specific guidance]

## Recent Changes

[Last 3 features and additions]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
```

### Update Process

```mermaid
sequenceDiagram
    participant Plan as doit.plan
    participant Script as update-agent-context.sh
    participant Claude as CLAUDE.md

    Plan->>Script: Execute update
    Script->>Claude: Read existing content
    Script->>Script: Extract tech from plan.md
    Script->>Script: Preserve manual additions
    Script->>Claude: Write updated content
```

### Key Features

- Auto-generated from feature plans
- Preserves manual additions between markers
- Updates technology list incrementally
- Tracks recent feature changes

---

## Template Interaction Summary

```mermaid
flowchart TD
    subgraph "Input"
        FD[Feature Description]
    end

    subgraph "Specification"
        ST[spec-template] --> SPEC[spec.md]
        CT[checklist-template] --> REQ[requirements.md]
    end

    subgraph "Planning"
        PT[plan-template] --> PLAN[plan.md]
        AT[agent-template] --> CLAUDE[CLAUDE.md]
    end

    subgraph "Implementation"
        TT[tasks-template] --> TASKS[tasks.md]
    end

    FD --> ST
    SPEC --> PT
    PLAN --> TT
    PLAN --> AT

    style FD fill:#e3f2fd
    style SPEC fill:#e8f5e9
    style PLAN fill:#fff3e0
    style TASKS fill:#fce4ec
```
