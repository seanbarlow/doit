# Do-It Tutorials

Welcome to the Do-It tutorials! These step-by-step guides will teach you how to use Do-It's spec-driven development workflow to build software efficiently with AI assistance.

## Choose Your Path

| Tutorial | Best For | Time |
|----------|----------|------|
| [Greenfield Project](01-greenfield-tutorial.md) | Starting a new project from scratch | ~2 hours |
| [Existing Project](02-existing-project-tutorial.md) | Adding Do-It to an existing codebase | ~90 minutes |
| [Creating Workflows](creating-workflows.md) | Building custom interactive workflows | ~60 minutes |

## Tutorial Overview

### Tutorial 1: Greenfield Project

**What you'll build**: A TaskFlow CLI application - a command-line task management tool.

**What you'll learn**:
- Initialize a new Do-It project with `doit init`
- Create a project constitution with `/doit.constitution`
- Generate project structure with `/doit.scaffoldit`
- Write feature specifications with `/doit.specit`
- Plan implementations with `/doit.planit`
- Create actionable tasks with `/doit.taskit`
- Implement features with `/doit.implementit`
- Review code with `/doit.reviewit`
- Complete features with `/doit.checkin`

**Prerequisites**:
- Do-It CLI installed (`pip install doit-cli`)
- Git installed and configured
- Claude Code or compatible AI IDE
- GitHub account (optional, for issue/PR creation)

---

### Tutorial 2: Existing Project Integration

**What you'll build**: Add a new feature to an existing Weather API project.

**What you'll learn**:
- Add Do-It to an existing codebase
- Create a constitution that reflects existing patterns
- Skip or adapt commands for existing projects
- Use the Do-It workflow alongside existing code

**Prerequisites**:
- An existing project (or use our sample Weather API)
- Do-It CLI installed
- Git initialized in your project

---

## Do-It Command Workflow

```mermaid
flowchart LR
    subgraph "Setup"
        A["doit init"] --> B["constitution"]
        B --> C["scaffoldit"]
    end

    subgraph "Feature Development"
        D["specit"] --> E["planit"]
        E --> F["taskit"]
        F --> G["implementit"]
        G --> H["reviewit"]
        H --> I["checkin"]
    end

    subgraph "Optional"
        J["testit"]
        K["roadmapit"]
        L["documentit"]
        M["fixit"]
    end

    C --> D
    G -.-> J
    I -.-> K
```

## Quick Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `doit init` | Initialize Do-It in a project | Once per project |
| `/doit.constitution` | Define project principles | After init, or to update |
| `/doit.scaffoldit` | Generate project structure | Greenfield projects |
| `/doit.specit` | Create feature specification | Start of each feature |
| `/doit.planit` | Generate implementation plan | After spec is approved |
| `/doit.taskit` | Create actionable tasks | After plan is approved |
| `/doit.implementit` | Execute tasks | During development |
| `/doit.reviewit` | Review implementation | After implementation |
| `/doit.testit` | Run automated tests | Before/after changes |
| `/doit.checkin` | Finalize feature | When feature is complete |
| `/doit.fixit` | Bug-fix workflow | When fixing bugs |
| `/doit.roadmapit` | Manage project backlog | Anytime |
| `/doit.documentit` | Organize documentation | As needed |
| `doit validate` | Validate spec quality | Before commit |
| `doit status` | Show spec dashboard | Track progress |
| `doit xref` | Cross-reference traceability | Verify coverage |
| `doit diagram` | Generate diagrams | After spec updates |

## Need Help?

- **Documentation**: [Do-It Documentation](../index.md)
- **Installation**: [Installation Guide](../installation.md)
- **GitHub Issues**: [Report a problem](https://github.com/seanbarlow/doit/issues)
