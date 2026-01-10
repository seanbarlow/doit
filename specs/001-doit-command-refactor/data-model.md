# Data Model: Doit Command Refactoring

**Branch**: `001-doit-command-refactor` | **Date**: 2026-01-09
**Purpose**: Define entities, their attributes, and relationships

## Entity Overview

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Constitution  │────>│    Scaffold     │────>│      Spec       │
│   (foundation)  │     │   (structure)   │     │  (requirements) │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         v
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Epic Issue    │<────│      Plan       │<────│  Feature Issue  │
│   (GitHub)      │     │  (architecture) │     │    (GitHub)     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 v
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Task Issue    │<────│     Tasks       │────>│   Checklist     │
│   (GitHub)      │     │  (work items)   │     │  (validation)   │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 v
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Review Report  │<────│  Implementation │────>│   Test Report   │
│  (validation)   │     │    (code)       │     │   (results)     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 v
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Roadmap      │<────│    Checkin      │────>│  Pull Request   │
│  (tracking)     │     │  (finalize)     │     │   (GitHub)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Entity Definitions

### Constitution

**Purpose**: Project foundation document establishing principles, tech stack, and infrastructure.

**Location**: `.specify/memory/constitution.md`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| project_name | string | Yes | Name of the project |
| version | semver | Yes | Constitution version (MAJOR.MINOR.PATCH) |
| ratified_date | date | Yes | Date constitution was established |
| last_amended | date | Yes | Date of last modification |
| purpose | text | Yes | Project purpose and goals |
| principles | list | Yes | Core development principles (1-N items) |
| tech_stack | object | Yes | Languages, frameworks, libraries |
| infrastructure | object | No | Hosting, cloud provider, deployment |
| governance | text | Yes | Rules for amendments and compliance |

**Tech Stack Object**:
```yaml
tech_stack:
  languages:
    - name: "Python"
      version: "3.11+"
  frameworks:
    - name: "FastAPI"
      purpose: "REST API"
  libraries:
    - name: "typer"
      purpose: "CLI framework"
```

**Infrastructure Object**:
```yaml
infrastructure:
  hosting: "AWS ECS"
  cloud_provider: "AWS"
  deployment_strategy: "Blue-green"
  ci_cd: "GitHub Actions"
```

---

### Scaffold Configuration

**Purpose**: Defines project structure generated based on tech stack.

**Location**: Generated output at project root

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| tech_stack_source | reference | Yes | Link to constitution tech stack |
| structure_template | enum | Yes | single, web, mobile, monorepo |
| folders_created | list | Yes | Directories generated |
| config_files | list | Yes | Configuration files generated |
| starter_files | list | Yes | Initial files created |
| gitignore_patterns | list | Yes | .gitignore entries |

**Structure Analysis Report** (for existing projects):

| Attribute | Type | Description |
|-----------|------|-------------|
| current_structure | tree | Existing folder structure |
| recommendations | list | Suggested improvements |
| missing_items | list | Expected but not found |
| extra_items | list | Found but not expected |

---

### Spec (Feature Specification)

**Purpose**: Captures what and why for a feature.

**Location**: `specs/<branch>/spec.md`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| feature_name | string | Yes | Human-readable feature name |
| branch | string | Yes | Git branch name (###-feature-name) |
| created_date | date | Yes | Specification creation date |
| status | enum | Yes | Draft, Review, Approved, Implemented |
| user_stories | list | Yes | Prioritized user scenarios |
| functional_requirements | list | Yes | FR-### numbered requirements |
| success_criteria | list | Yes | SC-### measurable outcomes |
| edge_cases | list | Yes | Boundary conditions |
| assumptions | list | No | Working assumptions |
| dependencies | list | No | External dependencies |
| out_of_scope | list | No | Explicit exclusions |

**User Story Object**:
```yaml
user_story:
  id: "US-001"
  title: "Rename Base Command"
  priority: "P1"
  description: "As a developer..."
  acceptance_scenarios:
    - given: "initial state"
      when: "action"
      then: "expected outcome"
```

---

### Plan (Implementation Plan)

**Purpose**: Technical architecture and design decisions.

**Location**: `specs/<branch>/plan.md`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| branch | string | Yes | Git branch name |
| spec_reference | reference | Yes | Link to spec.md |
| summary | text | Yes | Technical approach summary |
| technical_context | object | Yes | Language, dependencies, platform |
| constitution_check | object | Yes | Compliance verification |
| project_structure | tree | Yes | Source code layout |
| architecture_decisions | list | Yes | AD-### numbered decisions |
| risk_assessment | list | No | Identified risks |

---

### Task

**Purpose**: Actionable work item with dependencies.

**Location**: `specs/<branch>/tasks.md`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Task identifier (T-###) |
| description | text | Yes | What needs to be done |
| phase | integer | Yes | Implementation phase |
| priority | enum | Yes | P1, P2, P3 |
| user_story | reference | No | Associated user story |
| dependencies | list | No | Blocking tasks |
| parallelizable | boolean | Yes | Can run alongside others |
| status | enum | Yes | pending, in_progress, completed |
| file_paths | list | No | Files to be created/modified |

---

### GitHub Issue Types

#### Epic Issue

**Purpose**: Top-level issue representing entire feature spec.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Epic: <feature-name> |
| summary | text | Yes | From spec summary |
| success_criteria | list | Yes | From spec SC items |
| feature_issues | list | Yes | Links to child Features |
| labels | list | Yes | ["epic", "<branch-name>"] |
| branch | string | Yes | Feature branch name |

#### Feature Issue

**Purpose**: Issue representing a user story.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Feature: <user-story-title> |
| description | text | Yes | User story description |
| parent_epic | reference | Yes | Link to Epic issue |
| acceptance_scenarios | list | Yes | Given/When/Then |
| priority | enum | Yes | P1, P2, P3 |
| labels | list | Yes | ["feature", "P#", "epic:#"] |

#### Task Issue

**Purpose**: Issue representing an individual task.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Task: <task-description> |
| description | text | Yes | Task details |
| parent_feature | reference | Yes | Link to Feature issue |
| definition_of_done | list | Yes | Completion criteria |
| estimated_effort | enum | No | XS, S, M, L, XL |
| phase | integer | Yes | Implementation phase |
| labels | list | Yes | ["task", "phase:#", "feature:#"] |

---

### Review Report

**Purpose**: Code review findings and manual testing results.

**Location**: `specs/<branch>/review-report.md`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| review_date | datetime | Yes | When review was performed |
| reviewer | string | Yes | Who performed review |
| findings | list | Yes | Code review issues |
| manual_tests | list | Yes | Manual test results |
| sign_off | boolean | Yes | User approval status |
| sign_off_date | datetime | No | When approved |

**Finding Object**:
```yaml
finding:
  id: "F-001"
  severity: "HIGH"
  location: "src/commands/specify.md:45"
  description: "Missing error handling"
  recommendation: "Add try-catch block"
```

---

### Test Report

**Purpose**: Automated and manual test results.

**Location**: `specs/<branch>/test-report.md`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| test_date | datetime | Yes | When tests were run |
| framework | string | Yes | Test framework used |
| automated_results | object | Yes | Pass/fail counts |
| test_details | list | Yes | Individual test outcomes |
| requirement_mapping | list | Yes | Test → FR mapping |
| manual_checklist | list | No | Manual test items |

---

### Roadmap

**Purpose**: Project-level feature tracking.

**Location**: `roadmap.md` (project root)

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| planned_features | list | Yes | Features in progress or planned |
| backlog | list | No | Future feature ideas |

**Roadmap Entry**:
```yaml
entry:
  feature: "Doit Command Refactor"
  branch: "001-doit-command-refactor"
  status: "In Progress"
  priority: "P1"
```

---

### Roadmap Completed

**Purpose**: Archive of completed features.

**Location**: `roadmap_completed.md` (project root)

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| completed_features | list | Yes | Finished features |

**Completed Entry**:
```yaml
entry:
  feature: "Doit Command Refactor"
  branch: "001-doit-command-refactor"
  completed_date: "2026-01-15"
  pr_number: 42
  pr_url: "https://github.com/org/repo/pull/42"
```

---

## State Transitions

### Spec Status
```
Draft → Review → Approved → Implemented
```

### Task Status
```
pending → in_progress → completed
```

### Issue Status
```
open → in_progress → closed
```

### Feature Workflow
```
constitution → scaffold → specify → plan → tasks → implement → review → test → checkin
```
