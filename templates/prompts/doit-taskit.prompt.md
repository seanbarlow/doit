---
agent: true
description: Generate actionable implementation tasks from design documents
---

# Doit Taskit - Task Generator

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

Generate implementation tasks from the plan and design documents. Follow these steps:

1. **Run prerequisites check** `.doit/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`
2. **Load design documents**:
   - `plan.md` (required) - Tech stack, architecture, structure
   - `spec.md` (required) - User stories with priorities
   - `data-model.md` (optional) - Entities
   - `contracts/` (optional) - API specifications

3. **Generate tasks.md** organized by user story with:
   - Phase 1: Setup (project initialization)
   - Phase 2: Foundation (blocking prerequisites)
   - Phase 3+: One phase per user story (priority order)
   - Final Phase: Polish & cross-cutting concerns

4. **Task format**: `- [ ] [ID] [P?] [Story] Description with file path`
   - `[P]` = Can run in parallel
   - `[Story]` = User story label (US1, US2, etc.)

5. **Generate visualizations**:
   - Task dependencies flowchart
   - Phase timeline Gantt chart

## Task Structure Example

```markdown
## Phase 3: User Story 1 - [Title] (Priority: P1)

**Goal**: [What this story delivers]
**Independent Test**: [How to verify]

### Implementation
- [ ] T007 [US1] Create model in src/models/user.py
- [ ] T008 [P] [US1] Create service in src/services/user_service.py
```
