# Doit Template System Documentation

**Version**: 1.0.0
**Last Updated**: 2026-01-10

## Overview

The doit template system provides a structured workflow for feature development, from specification through implementation and deployment. It consists of two template categories:

1. **Root Templates** - Document templates that define the structure of generated artifacts
2. **Command Templates** - Workflow definitions that orchestrate the development process

## Complete Workflow

```mermaid
flowchart TD
    subgraph "Initialization"
        A[Project Start] --> B[/doit.constitution/]
        B --> C[/doit.scaffoldit/]
    end

    subgraph "Specification Phase"
        C --> D[/doit.specit/]
        D --> E{Clarifications?}
        E -->|Yes| F[Resolve Ambiguities]
        F --> D
        E -->|No| G[spec.md Complete]
    end

    subgraph "Planning Phase"
        G --> H[/doit.planit/]
        H --> I[research.md]
        H --> J[data-model.md]
        H --> K[contracts/]
        H --> L[quickstart.md]
        I & J & K & L --> M[plan.md Complete]
    end

    subgraph "Task Generation"
        M --> N[/doit.taskit/]
        N --> O[tasks.md]
    end

    subgraph "Implementation"
        O --> P[/doit.implementit/]
        P --> Q{All Tasks Done?}
        Q -->|No| P
        Q -->|Yes| R[Implementation Complete]
    end

    subgraph "Quality Assurance"
        R --> S[/doit.reviewit/]
        S --> T[review-report.md]
        T --> U[/doit.testit/]
        U --> V[test-report.md]
    end

    subgraph "Completion"
        V --> W[/doit.checkin/]
        W --> X[PR Created]
        X --> Y[Feature Complete]
    end

    style A fill:#e1f5fe
    style Y fill:#c8e6c9
```

## Template Categories

### Root Templates (5 files)

| Template | Purpose | Output |
|----------|---------|--------|
| [spec-template.md](root-templates.md#spec-template) | Feature specification structure | `specs/XXX/spec.md` |
| [plan-template.md](root-templates.md#plan-template) | Implementation plan structure | `specs/XXX/plan.md` |
| [tasks-template.md](root-templates.md#tasks-template) | Task breakdown structure | `specs/XXX/tasks.md` |
| [checklist-template.md](root-templates.md#checklist-template) | Generic checklist format | Various checklist files |
| [agent-file-template.md](root-templates.md#agent-file-template) | AI agent context file | `CLAUDE.md` |

### Command Templates (9 files)

| Command | Purpose | Phase |
|---------|---------|-------|
| [doit.constitution](commands.md#doitconstitution) | Project principles & tech stack | Initialization |
| [doit.scaffold](commands.md#doitscaffold) | Generate project structure | Initialization |
| [doit.specify](commands.md#doitspecify) | Create feature specifications | Specification |
| [doit.plan](commands.md#doitplan) | Generate implementation plan | Planning |
| [doit.tasks](commands.md#doittasks) | Break down into tasks | Task Generation |
| [doit.implement](commands.md#doitimplement) | Execute tasks | Implementation |
| [doit.review](commands.md#doitreview) | Code review & manual testing | QA |
| [doit.test](commands.md#doittest) | Automated test execution | QA |
| [doit.checkin](commands.md#doitcheckin) | Finalize & create PR | Completion |

## Artifact Flow

```mermaid
flowchart LR
    subgraph "User Input"
        UI[Feature Description]
    end

    subgraph "Specification Artifacts"
        UI --> SPEC[spec.md]
        SPEC --> REQ[requirements.md]
    end

    subgraph "Planning Artifacts"
        SPEC --> PLAN[plan.md]
        PLAN --> RES[research.md]
        PLAN --> DM[data-model.md]
        PLAN --> CON[contracts/]
        PLAN --> QS[quickstart.md]
    end

    subgraph "Implementation Artifacts"
        PLAN --> TASKS[tasks.md]
        TASKS --> CODE[Source Code]
    end

    subgraph "Quality Artifacts"
        CODE --> REV[review-report.md]
        CODE --> TEST[test-report.md]
    end

    subgraph "Completion Artifacts"
        REV --> DOC[Feature Documentation]
        TEST --> DOC
        DOC --> PR[Pull Request]
    end
```

## Directory Structure

```text
templates/
├── agent-file-template.md      # CLAUDE.md structure
├── checklist-template.md       # Generic checklist format
├── plan-template.md            # Implementation plan structure
├── spec-template.md            # Feature specification structure
├── tasks-template.md           # Task breakdown structure
├── vscode-settings.json        # Editor configuration
└── commands/                   # Command workflow definitions
    ├── doit.checkin.md
    ├── doit.constitution.md
    ├── doit.implementit.md
    ├── doit.planit.md
    ├── doit.reviewit.md
    ├── doit.scaffoldit.md
    ├── doit.specit.md
    ├── doit.taskit.md
    └── doit.testit.md
```

## Handoff Architecture

Commands are designed to flow into each other through handoffs:

```mermaid
flowchart TB
    subgraph "Primary Flow"
        direction LR
        CONST[constitution] --> SCAFFOLD[scaffold]
        SCAFFOLD --> SPECIFY[specify]
        SPECIFY --> PLAN[plan]
        PLAN --> TASKS[tasks]
        TASKS --> IMPL[implement]
        IMPL --> REVIEW[review]
        REVIEW --> TEST[test]
        TEST --> CHECKIN[checkin]
    end

    subgraph "Alternate Paths"
        SPECIFY -.->|"Skip to scaffold"| SCAFFOLD
        REVIEW -.->|"Re-review"| IMPL
        TEST -.->|"Fix & retest"| REVIEW
    end
```

## Template Variables

Common variables used across templates:

| Variable | Description | Example |
|----------|-------------|---------|
| `$ARGUMENTS` | User input from command | "Add user authentication" |
| `FEATURE_DIR` | Feature specification directory | `/specs/005-user-auth/` |
| `BRANCH` | Git branch name | `005-user-auth` |
| `SPEC_FILE` | Path to spec.md | `/specs/005-user-auth/spec.md` |
| `IMPL_PLAN` | Path to plan.md | `/specs/005-user-auth/plan.md` |

## Enhancement Opportunities

See [Enhancement Recommendations](enhancements.md) for proposed improvements to the template system.

## Related Documentation

- [Root Templates](root-templates.md) - Detailed documentation for document templates
- [Command Templates](commands.md) - Detailed documentation for workflow commands
- [Enhancement Recommendations](enhancements.md) - Proposed improvements
