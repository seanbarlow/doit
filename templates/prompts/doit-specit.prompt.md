---
agent: true
description: Create or update feature specification from natural language description
---

# Doit Specit - Feature Specification Generator

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

Create a feature specification from the user's description. Follow these steps:

1. **Parse the feature description** from the user input
2. **Generate a branch name** using format `###-short-name` (e.g., `001-user-auth`)
3. **Create the specification** at `specs/<branch-name>/spec.md` with:
   - User Scenarios & Testing (with prioritized user stories P1, P2, P3)
   - Functional Requirements (testable, numbered FR-001, FR-002, etc.)
   - Success Criteria (measurable outcomes)
   - Key Entities (if data involved)

4. **Generate visualizations**:
   - User journey flowchart (Mermaid)
   - Entity relationships diagram (if entities defined)

5. **Create requirements checklist** at `specs/<branch-name>/checklists/requirements.md`

## Template Structure

Use this structure for the specification:

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [DATE]
**Status**: Draft
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - [Title] (Priority: P1)
[Description]
**Acceptance Scenarios**:
1. **Given** [state], **When** [action], **Then** [outcome]

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST [capability]

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: [Measurable metric]
```

## Next Steps

After creating the specification, suggest running:
- `#doit-planit` to create an implementation plan
- `#doit-taskit` to generate implementation tasks
