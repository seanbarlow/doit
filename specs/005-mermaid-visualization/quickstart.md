# Quickstart: Automatic Mermaid Visualization

**Feature Branch**: `005-mermaid-visualization`
**Date**: 2026-01-10

## Overview

This feature automatically generates mermaid diagrams in your specification, planning, and task documents. Diagrams are created during the doit workflow commands and inserted into marked sections.

## Quick Reference

### Commands and Generated Diagrams

| Command | Document | Diagrams Generated |
|---------|----------|-------------------|
| `/doit.specify` | spec.md | User Journey flowchart, ER diagram |
| `/doit.plan` | plan.md | Architecture flowchart, Component dependencies |
| `/doit.plan` | data-model.md | ER diagram, State machines |
| `/doit.tasks` | tasks.md | Task dependencies flowchart, Phase gantt |
| `/doit.review` | review-report.md | Finding distribution pie, Test results |

### Auto-Generated Section Format

All auto-generated diagrams are wrapped in markers:

```markdown
<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
## User Journey Visualization

```mermaid
flowchart LR
    ...
```
<!-- END:AUTO-GENERATED -->
```

## Usage Examples

### 1. Specification Diagrams

After running `/doit.specify`, your spec.md will include:

**User Journey** (from user stories):
```mermaid
flowchart LR
    subgraph "P1: Core Feature"
        US1_A[User Action] --> US1_B[System Response]
    end
    subgraph "P2: Enhancement"
        US2_A[User Action] --> US2_B[System Response]
    end
```

**Entity Relationships** (from Key Entities):
```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
```

### 2. Planning Diagrams

After running `/doit.plan`, your plan.md will include:

**Architecture Overview**:
```mermaid
flowchart TD
    subgraph "Frontend"
        UI[React App]
    end
    subgraph "Backend"
        API[FastAPI] --> SVC[Services]
        SVC --> DB[(Database)]
    end
    UI --> API
```

**Component Dependencies**:
```mermaid
flowchart TD
    AUTH[Auth] --> USER[User Service]
    ORDER[Order] --> USER
    ORDER --> PRODUCT[Product]
```

### 3. Task Diagrams

After running `/doit.tasks`, your tasks.md will include:

**Task Dependencies**:
```mermaid
flowchart TD
    T001[Setup] --> T002[Models]
    T002 --> T003[Services]
    T002 --> T004[Tests]
    T003 & T004 --> T005[Integration]
```

**Phase Timeline**:
```mermaid
gantt
    title Implementation Phases
    dateFormat YYYY-MM-DD
    section Phase 1
    Setup :a1, 2026-01-10, 1d
    Models :a2, after a1, 2d
    section Phase 2
    Services :b1, after a2, 2d
    Tests :b2, after a2, 1d
```

## Customization

### Manual Edits

Content **outside** auto-generated markers is preserved:

```markdown
## My Custom Section
This content is never modified by auto-generation.

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
This content WILL be regenerated.
<!-- END:AUTO-GENERATED -->

## Another Custom Section
This is also preserved.
```

### Disabling Sections

To prevent a diagram from being generated, remove or rename the section:

```markdown
<!-- DISABLED:AUTO-GENERATED section="user-journey" -->
```

### Node Limits

Diagrams automatically split into subgraphs when exceeding limits:

| Diagram Type | Soft Limit | Action |
|--------------|------------|--------|
| Flowchart | 20 nodes | Group by phase/category |
| ER Diagram | 10 entities | Group by domain |
| Gantt | 15 tasks | Summarize phases |

## Troubleshooting

### Diagram Not Rendering

1. Check mermaid syntax is valid
2. Verify code fence markers: ` ```mermaid ` and ` ``` `
3. Ensure diagram type is spelled correctly

### Section Not Updating

1. Verify markers are intact: `<!-- BEGIN:AUTO-GENERATED section="..." -->`
2. Check section name matches expected value
3. Run the appropriate command to regenerate

### Large Diagrams

If a diagram is too large to read:
1. The system auto-splits at soft limits
2. Manually add subgraph boundaries if needed
3. Consider splitting across multiple diagrams

## Section Names Reference

| Document | Section Name | Diagram Type |
|----------|--------------|--------------|
| spec.md | `user-journey` | flowchart |
| spec.md | `entity-relationships` | erDiagram |
| plan.md | `architecture` | flowchart |
| plan.md | `component-dependencies` | flowchart |
| data-model.md | `er-diagram` | erDiagram |
| data-model.md | `[entity]-states` | stateDiagram-v2 |
| tasks.md | `task-dependencies` | flowchart |
| tasks.md | `phase-timeline` | gantt |
| review-report.md | `finding-distribution` | pie |
| review-report.md | `test-results` | bar |
