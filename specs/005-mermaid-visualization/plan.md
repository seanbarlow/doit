# Implementation Plan: Automatic Mermaid Visualization

**Branch**: `005-mermaid-visualization` | **Date**: 2026-01-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-mermaid-visualization/spec.md`

## Summary

Enhance the doit template system to automatically generate mermaid diagrams during specification, planning, and task generation phases. This feature adds visualization capabilities to 4 command templates (doit.specify, doit.plan, doit.tasks, doit.review) and updates 3 document templates (spec-template, plan-template, tasks-template) to include diagram sections.

## Technical Context

**Language/Version**: Markdown (templates), Bash 5.x (helper scripts if needed)
**Primary Dependencies**: Mermaid syntax (rendered by GitHub/VS Code), Claude Code slash command system
**Storage**: N/A (file-based template system)
**Testing**: Manual verification via markdown preview
**Target Platform**: Any markdown renderer with mermaid support (GitHub, VS Code, etc.)
**Project Type**: Template enhancement (no application code)
**Performance Goals**: Diagram generation adds < 2 seconds per document
**Constraints**: Generated mermaid must be valid syntax; preserve existing manual content
**Scale/Scope**: 4 command templates, 3 document templates, 6 diagram types

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS - No constitution violations

The project constitution is a template (not yet filled in for this project). This feature:
- Uses existing technologies (Markdown, Bash) already in use
- Follows established patterns from the doit command system
- Does not introduce new frameworks or breaking changes
- Enhances documentation without modifying core architecture

## Project Structure

### Documentation (this feature)

```text
specs/005-mermaid-visualization/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # Requirements tracking
└── tasks.md             # Phase 2 output (/doit.tasks)
```

### Source Files (affected)

```text
templates/
├── spec-template.md         # Add User Journey, ER diagram sections
├── plan-template.md         # Add Architecture, Component diagram sections
└── tasks-template.md        # Add Task Dependency, Timeline sections

templates/commands/
├── doit.specify.md          # Add diagram generation instructions
├── doit.plan.md             # Add diagram generation instructions
├── doit.tasks.md            # Add diagram generation instructions
└── doit.review.md           # Add diagram generation instructions

.doit/templates/commands/    # Authoritative source - update first
├── doit.specify.md
├── doit.plan.md
├── doit.tasks.md
└── doit.review.md
```

**Structure Decision**: Template enhancement pattern - modifications to existing markdown template files. No new source code directories needed.

## Complexity Tracking

No complexity violations - this feature follows the established template pattern and adds only markdown content.

## Diagram Types

| Type | Mermaid Syntax | Use Case |
|------|----------------|----------|
| flowchart | `flowchart TD/LR` | User journeys, architecture, task dependencies |
| erDiagram | `erDiagram` | Entity relationships |
| sequenceDiagram | `sequenceDiagram` | API flows |
| stateDiagram-v2 | `stateDiagram-v2` | State machines |
| gantt | `gantt` | Phase timelines |
| pie | `pie` | Distribution charts |

## Auto-Generation Pattern

All auto-generated diagrams will follow this pattern:

```markdown
<!-- BEGIN:AUTO-GENERATED section="[section-name]" -->
## [Section Title]

```mermaid
[diagram content]
```
<!-- END:AUTO-GENERATED -->
```

This allows:
- Clear identification of auto-generated content
- Safe updates without overwriting manual edits
- Consistent structure across all templates

## Implementation Phases

### Phase 1: Template Foundation (P1 Requirements)

Update document templates with diagram section placeholders:
1. Add User Journey section to spec-template.md
2. Add Entity Relationships section to spec-template.md
3. Update doit.specify.md with diagram generation instructions

**Files**: spec-template.md, doit.specify.md
**Requirements**: FR-001, FR-002, FR-003, FR-013

### Phase 2: Planning Diagrams (P2 Requirements)

Extend diagram support to planning phase:
1. Add Architecture Overview section to plan-template.md
2. Add Component Dependencies section to plan-template.md
3. Add ER diagram generation to data-model.md workflow
4. Add state machine detection and generation
5. Update doit.plan.md with diagram generation instructions

**Files**: plan-template.md, doit.plan.md
**Requirements**: FR-004, FR-005, FR-006, FR-007, FR-013

### Phase 3: Task Diagrams (P3 Requirements)

Add task visualization capabilities:
1. Add Task Dependencies section to tasks-template.md
2. Add Phase Timeline section to tasks-template.md
3. Implement parallel task ([P]) detection
4. Update doit.tasks.md with diagram generation instructions

**Files**: tasks-template.md, doit.tasks.md
**Requirements**: FR-008, FR-009, FR-010, FR-013

### Phase 4: Review Diagrams (P4 Requirements)

Add review visualization capabilities:
1. Add Finding Distribution section to review workflow
2. Add Test Results visualization
3. Update doit.review.md with diagram generation instructions

**Files**: doit.review.md
**Requirements**: FR-011, FR-012, FR-013

### Phase 5: Cross-Cutting Concerns

Implement validation and size management:
1. Add mermaid syntax validation
2. Implement diagram size detection
3. Add automatic subgraph splitting for large diagrams
4. Verify manual content preservation

**Files**: All affected templates
**Requirements**: FR-014, FR-015, FR-016

## Design Artifacts

- [research.md](research.md) - Mermaid syntax patterns and integration strategies
- [data-model.md](data-model.md) - Entity definitions and relationships
- [quickstart.md](quickstart.md) - Usage guide and examples

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Invalid mermaid syntax | Medium | Low | Validation before insertion |
| Large diagrams unreadable | Medium | Medium | Auto-split at 20 nodes |
| Overwrite manual content | Low | High | Clear section markers |
| Inconsistent rendering | Low | Low | Test in GitHub + VS Code |

## Success Metrics

Mapped from spec.md Success Criteria:

| Metric | Target | Measurement |
|--------|--------|-------------|
| User Journey coverage | 100% specs with stories | Manual review |
| Architecture coverage | 100% plans with tech stack | Manual review |
| Task dependency coverage | 100% tasks.md files | Manual review |
| Syntax validity | 0 invalid diagrams | Render test |
| Generation time | < 2 seconds/diagram | Timing |
| Large diagram handling | Auto-split at 20+ nodes | Node count |
