# Template Enhancement Recommendations

**Created**: 2026-01-10
**Status**: Proposed

## Overview

This document identifies opportunities to enhance the doit template system based on analysis of all current templates. The primary enhancement theme is **automatic visualization generation** using mermaid diagrams.

## Enhancement Categories

```mermaid
mindmap
  root((Enhancements))
    Visualization
      Workflow Diagrams
      Entity Relationships
      Dependency Graphs
      State Machines
    Structure
      Consistency
      Modularity
      Extensibility
    Automation
      Auto-generation
      Validation
      Integration
    Documentation
      Examples
      Guidelines
      Templates
```

---

## E-001: Automatic Mermaid Visualization

### Problem

Current templates generate text-heavy documentation that can be difficult to quickly understand. Relationships between entities, workflows, and dependencies are described in prose rather than visualized.

### Proposed Enhancement

Add automatic mermaid diagram generation to key templates:

### spec-template.md Enhancements

Add a **User Journey Diagram** section:

```markdown
## User Journey Visualization

<!-- AUTO-GENERATED: Update by running /doit.specit -->

```mermaid
flowchart LR
    subgraph "User Story 1"
        US1_S[Start] --> US1_A[Action 1]
        US1_A --> US1_B[Action 2]
        US1_B --> US1_E[End]
    end
```

Add an **Entity Relationship Diagram** section:

```markdown
## Entity Relationships

<!-- AUTO-GENERATED: Update by running /doit.specit -->

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
```

### plan-template.md Enhancements

Add an **Architecture Diagram** section:

```markdown
## Architecture Overview

<!-- AUTO-GENERATED: Update by running /doit.planit -->

```mermaid
flowchart TD
    subgraph "Frontend"
        UI[React App]
    end

    subgraph "Backend"
        API[FastAPI]
        SVC[Services]
        DB[(PostgreSQL)]
    end

    UI --> API
    API --> SVC
    SVC --> DB
```

Add a **Component Dependency Diagram**:

```markdown
## Component Dependencies

```mermaid
flowchart TD
    AUTH[Auth Service] --> USER[User Service]
    ORDER[Order Service] --> USER
    ORDER --> PRODUCT[Product Service]
    ORDER --> PAYMENT[Payment Service]
```

### tasks-template.md Enhancements

Add a **Task Dependency Graph**:

```markdown
## Task Dependencies

<!-- AUTO-GENERATED: Update by running /doit.taskit -->

```mermaid
flowchart TD
    T001[Setup] --> T002[Dependencies]
    T002 --> T003[Base Models]
    T003 --> T004[User Model]
    T003 --> T005[Product Model]
    T004 --> T006[User Service]
    T005 --> T007[Product Service]
    T006 & T007 --> T008[Integration]
```

Add a **Phase Timeline**:

```markdown
## Phase Timeline

```mermaid
gantt
    title Implementation Phases
    dateFormat  YYYY-MM-DD
    section Setup
    Project Init           :a1, 2026-01-10, 1d
    Dependencies           :a2, after a1, 1d
    section User Story 1
    Models                 :b1, after a2, 2d
    Services               :b2, after b1, 2d
    Endpoints              :b3, after b2, 1d
    section User Story 2
    Models                 :c1, after a2, 2d
    Services               :c2, after c1, 2d
```

### Implementation Location

| Template | New Sections | Diagram Types |
|----------|--------------|---------------|
| spec-template.md | User Journey, Entity Relationships | flowchart, erDiagram |
| plan-template.md | Architecture, Component Dependencies | flowchart, C4 |
| tasks-template.md | Task Dependencies, Phase Timeline | flowchart, gantt |
| data-model.md | Entity Relationships | erDiagram |
| contracts/ | API Flow | sequenceDiagram |

---

## E-002: Command Template Consistency

### Problem

Command templates have inconsistent structure and documentation patterns.

### Proposed Enhancement

Standardize all command templates with:

1. **Consistent YAML Frontmatter**

```yaml
---
description: [Brief description]
version: 1.0.0
inputs:
  - name: $ARGUMENTS
    description: User input
    required: false
outputs:
  - name: [output file]
    path: [path pattern]
handoffs:
  - label: [Next Action]
    agent: [command]
    prompt: [Default prompt]
---
```

2. **Standard Outline Structure**

```markdown
## User Input
## Prerequisites
## Workflow
## Outputs
## Error Handling
## Handoffs
```

3. **Mermaid Workflow Diagram** (mandatory)

```markdown
## Workflow

```mermaid
flowchart TD
    A[Step 1] --> B[Step 2]
    B --> C{Decision?}
    C -->|Yes| D[Path A]
    C -->|No| E[Path B]
```

---

## E-003: Data Model Visualization

### Problem

The `data-model.md` artifact is text-based and doesn't automatically generate ER diagrams.

### Proposed Enhancement

Add automatic ER diagram generation in `/doit.planit`:

```markdown
## Entity Relationship Diagram

<!-- AUTO-GENERATED from entity definitions below -->

```mermaid
erDiagram
    USER {
        uuid id PK
        string email UK
        string name
        datetime created_at
    }
    ORDER {
        uuid id PK
        uuid user_id FK
        decimal total
        string status
    }
    USER ||--o{ ORDER : places
```

### Implementation

1. Parse entity definitions from `data-model.md`
2. Extract fields and relationships
3. Generate mermaid erDiagram syntax
4. Insert at top of document

---

## E-004: API Contract Visualization

### Problem

API contracts in `contracts/` are defined in OpenAPI/GraphQL but not visualized.

### Proposed Enhancement

Add automatic sequence diagrams for API flows:

```markdown
## API Flow: User Registration

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant V as Validator
    participant D as Database

    C->>A: POST /users
    A->>V: Validate input
    V-->>A: Valid
    A->>D: Insert user
    D-->>A: User created
    A-->>C: 201 Created
```

### Implementation

1. Parse OpenAPI/GraphQL schemas
2. Identify request/response flows
3. Generate sequenceDiagram for each endpoint group
4. Add to contracts documentation

---

## E-005: State Machine Visualization

### Problem

Entity state transitions are described in text but not visualized.

### Proposed Enhancement

Add state machine diagrams for entities with status fields:

```markdown
## Order State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Order Created
    Pending --> Processing: Payment Received
    Processing --> Shipped: Items Dispatched
    Shipped --> Delivered: Delivery Confirmed
    Delivered --> [*]

    Pending --> Cancelled: User Cancelled
    Processing --> Cancelled: Refund Requested
    Cancelled --> [*]
```

### Detection

Automatically detect state machine candidates:
- Fields named `status`, `state`, `stage`
- Enums with transition-like values
- Lifecycle patterns in requirements

---

## E-006: Review Report Visualization

### Problem

Review reports are table-heavy and don't visualize quality metrics.

### Proposed Enhancement

Add quality dashboard visualization in `/doit.reviewit`:

```markdown
## Quality Overview

```mermaid
pie title Finding Distribution
    "Critical" : 0
    "Major" : 2
    "Minor" : 5
    "Info" : 3
```

```mermaid
xychart-beta
    title "Test Results by Category"
    x-axis [Unit, Integration, E2E, Manual]
    y-axis "Tests" 0 --> 50
    bar [35, 12, 8, 6]
    line [35, 12, 8, 6]
```

---

## E-007: Checkin Summary Visualization

### Problem

Checkin summaries don't visualize the feature's impact.

### Proposed Enhancement

Add impact visualization in `/doit.checkin`:

```markdown
## Feature Impact

```mermaid
flowchart LR
    subgraph "Files Changed"
        NEW[12 New]
        MOD[8 Modified]
        DEL[3 Deleted]
    end

    subgraph "Lines"
        ADD[+847]
        REM[-123]
    end

    NEW --> ADD
    MOD --> ADD & REM
    DEL --> REM
```

---

## E-008: Template Validation

### Problem

No automated validation that generated documents conform to template structure.

### Proposed Enhancement

Add a validation schema for each template:

```yaml
# spec-template.schema.yaml
required_sections:
  - "User Scenarios & Testing"
  - "Requirements"
  - "Success Criteria"

required_patterns:
  - pattern: "### User Story \\d+ - .+ \\(Priority: P\\d+\\)"
    min_count: 1
  - pattern: "FR-\\d{3}"
    min_count: 1
  - pattern: "SC-\\d{3}"
    min_count: 1

forbidden_patterns:
  - pattern: "\\[NEEDS CLARIFICATION\\]"
    max_count: 3
```

### Implementation

Add validation step to each command that generates documents.

---

## E-009: Cross-Reference Visualization

### Problem

Relationships between spec requirements, tasks, and tests are tracked but not visualized.

### Proposed Enhancement

Add traceability matrix visualization:

```markdown
## Traceability Matrix

```mermaid
flowchart LR
    subgraph "Requirements"
        FR001[FR-001]
        FR002[FR-002]
        FR003[FR-003]
    end

    subgraph "Tasks"
        T010[T010]
        T011[T011]
        T012[T012]
    end

    subgraph "Tests"
        TEST1[test_user_create]
        TEST2[test_user_auth]
    end

    FR001 --> T010 --> TEST1
    FR001 --> T011 --> TEST2
    FR002 --> T012
```

---

## E-010: Interactive Documentation

### Problem

Generated documentation is static and doesn't update as the project evolves.

### Proposed Enhancement

Add update markers that commands can refresh:

```markdown
<!-- BEGIN:AUTO-UPDATE section="task-progress" -->
## Task Progress

```mermaid
pie title Task Status
    "Completed" : 15
    "In Progress" : 3
    "Pending" : 12
```
<!-- END:AUTO-UPDATE -->
```

Commands would parse these markers and update content between them while preserving manual additions.

---

## Implementation Priority

```mermaid
quadrantChart
    title Enhancement Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Quick Wins
    quadrant-2 Major Projects
    quadrant-3 Fill Ins
    quadrant-4 Time Sinks

    E-001: [0.7, 0.9]
    E-002: [0.3, 0.6]
    E-003: [0.4, 0.8]
    E-004: [0.5, 0.7]
    E-005: [0.4, 0.6]
    E-006: [0.3, 0.5]
    E-007: [0.3, 0.4]
    E-008: [0.6, 0.7]
    E-009: [0.5, 0.8]
    E-010: [0.8, 0.6]
```

### Recommended Order

1. **E-001**: Automatic Mermaid Visualization (highest impact)
2. **E-003**: Data Model Visualization
3. **E-009**: Cross-Reference Visualization
4. **E-004**: API Contract Visualization
5. **E-002**: Command Template Consistency
6. **E-008**: Template Validation
7. **E-005**: State Machine Visualization
8. **E-006**: Review Report Visualization
9. **E-007**: Checkin Summary Visualization
10. **E-010**: Interactive Documentation

---

## Next Steps

1. Create feature specification for E-001 using `/doit.specit`
2. Implement visualization generation logic
3. Update all templates with diagram placeholders
4. Add documentation for diagram customization
5. Create examples gallery showing generated visualizations
