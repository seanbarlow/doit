# GitHub Issue Template Contracts

**Branch**: `001-doit-command-refactor` | **Date**: 2026-01-09
**Purpose**: Define structure for Epic, Feature, and Task issue templates

## Template Location

All templates stored in `.github/ISSUE_TEMPLATE/`

---

## Epic Issue Template

**File**: `.github/ISSUE_TEMPLATE/epic.yml`

### Structure

```yaml
name: Epic
description: Create an Epic issue for a feature specification
title: "Epic: "
labels: ["epic"]
body:
  - type: markdown
    attributes:
      value: |
        ## Epic Issue
        This issue tracks an entire feature specification (Epic level).

  - type: input
    id: branch
    attributes:
      label: Feature Branch
      description: The git branch for this feature
      placeholder: "001-feature-name"
    validations:
      required: true

  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: Brief description of the epic from spec.md
      placeholder: "Describe what this epic delivers..."
    validations:
      required: true

  - type: textarea
    id: success-criteria
    attributes:
      label: Success Criteria
      description: Measurable outcomes from spec.md
      placeholder: |
        - SC-001: ...
        - SC-002: ...
    validations:
      required: true

  - type: textarea
    id: user-stories
    attributes:
      label: User Stories
      description: Links to Feature issues (auto-populated)
      placeholder: |
        - [ ] #XX Feature: Story 1
        - [ ] #XX Feature: Story 2
    validations:
      required: false

  - type: textarea
    id: acceptance-criteria
    attributes:
      label: Acceptance Criteria
      description: High-level acceptance criteria
      placeholder: |
        - All user stories completed
        - All tests passing
        - Documentation complete
    validations:
      required: true
```

### Labels
- `epic` (always)
- `<branch-name>` (feature branch identifier)

### Created By
- `doit.specify` command

---

## Feature Issue Template

**File**: `.github/ISSUE_TEMPLATE/feature.yml`

### Structure

```yaml
name: Feature
description: Create a Feature issue for a user story
title: "Feature: "
labels: ["feature"]
body:
  - type: markdown
    attributes:
      value: |
        ## Feature Issue
        This issue tracks a user story (Feature level).

  - type: input
    id: parent-epic
    attributes:
      label: Part of Epic
      description: Link to parent Epic issue
      placeholder: "#XX"
    validations:
      required: true

  - type: input
    id: priority
    attributes:
      label: Priority
      description: User story priority
      placeholder: "P1, P2, or P3"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: User story description
      placeholder: "As a [user], I want [goal] so that [benefit]..."
    validations:
      required: true

  - type: textarea
    id: acceptance-scenarios
    attributes:
      label: Acceptance Scenarios
      description: Given/When/Then scenarios from spec
      placeholder: |
        1. **Given** [context], **When** [action], **Then** [outcome]
        2. **Given** [context], **When** [action], **Then** [outcome]
    validations:
      required: true

  - type: textarea
    id: tasks
    attributes:
      label: Tasks
      description: Links to Task issues (auto-populated by doit.tasks)
      placeholder: |
        - [ ] #XX Task: ...
        - [ ] #XX Task: ...
    validations:
      required: false
```

### Labels
- `feature` (always)
- `P1`, `P2`, or `P3` (priority)
- `epic:#XX` (parent epic number)

### Created By
- `doit.specify` command

---

## Task Issue Template

**File**: `.github/ISSUE_TEMPLATE/task.yml`

### Structure

```yaml
name: Task
description: Create a Task issue for an implementation task
title: "Task: "
labels: ["task"]
body:
  - type: markdown
    attributes:
      value: |
        ## Task Issue
        This issue tracks an individual implementation task.

  - type: input
    id: parent-feature
    attributes:
      label: Part of Feature
      description: Link to parent Feature issue
      placeholder: "#XX"
    validations:
      required: true

  - type: input
    id: phase
    attributes:
      label: Phase
      description: Implementation phase number
      placeholder: "1, 2, 3, etc."
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: What needs to be done
      placeholder: "Implement [specific functionality]..."
    validations:
      required: true

  - type: textarea
    id: definition-of-done
    attributes:
      label: Definition of Done
      description: Checklist for completion
      placeholder: |
        - [ ] Code implemented
        - [ ] Tests written
        - [ ] Tests passing
        - [ ] Code reviewed
    validations:
      required: true

  - type: dropdown
    id: effort
    attributes:
      label: Estimated Effort
      description: T-shirt size estimate
      options:
        - XS (< 1 hour)
        - S (1-4 hours)
        - M (4-8 hours)
        - L (1-2 days)
        - XL (> 2 days)
    validations:
      required: false

  - type: textarea
    id: files
    attributes:
      label: Files to Modify
      description: List of files that will be created or changed
      placeholder: |
        - src/commands/new-file.md (create)
        - src/utils/helper.sh (modify)
    validations:
      required: false
```

### Labels
- `task` (always)
- `phase:#` (implementation phase)
- `feature:#XX` (parent feature number)

### Created By
- `doit.tasks` command

---

## Issue Hierarchy Visualization

```text
Epic #10: Doit Command Refactoring
├── labels: [epic, 001-doit-command-refactor]
├── Feature #11: Rename Base Command (P1)
│   ├── labels: [feature, P1, epic:10]
│   ├── Task #15: Rename command files
│   │   └── labels: [task, phase:1, feature:11]
│   └── Task #16: Update references
│       └── labels: [task, phase:1, feature:11]
├── Feature #12: Consolidate Specify (P1)
│   ├── labels: [feature, P1, epic:10]
│   └── Task #17: Integrate clarify
│       └── labels: [task, phase:2, feature:12]
└── Feature #13: New Review Command (P2)
    ├── labels: [feature, P2, epic:10]
    └── Task #18: Implement review
        └── labels: [task, phase:3, feature:13]
```

---

## Navigation Pattern

### From Task to Epic

```markdown
## Hierarchy
- **Task**: Rename command files
- **Part of Feature**: #11 - Rename Base Command
- **Part of Epic**: #10 - Doit Command Refactoring
```

### Automated Backlinks

GitHub automatically creates "mentioned in" links when issues reference each other:
- Epic shows all Features that mention it
- Features show all Tasks that mention them
- Provides bi-directional navigation
