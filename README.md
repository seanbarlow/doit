<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="media/doit-logo-white.svg">
    <img src="media/doit-logo-full-color.svg" alt="Do-It Framework Logo" width="200">
  </picture>
</div>

# Do-It - Spec-Driven Development Framework

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/seanbarlow/doit?style=social)](https://github.com/seanbarlow/doit)
[![PyPI version](https://img.shields.io/pypi/v/doit-toolkit-cli.svg)](https://pypi.org/project/doit-toolkit-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**See your architecture before you build it.** Do-It is an opinionated, AI-powered framework for specification-driven development. Define specifications, auto-generate diagrams, create roadmaps, and build with confidence.

[Quick Start](#quick-start) | [Documentation](https://github.com/seanbarlow/doit/tree/main/docs) | [Contributing](#contributing)

</div>

---

## Features

- **Specification-Driven** - Define what you're building before you build it
- **Auto-Generated Diagrams** - Automatic Mermaid diagrams from specs (user journeys, architecture, ER models, task dependencies, timelines)
- **Intelligent Roadmapping** - Prioritized roadmaps with P1-P4 system and vision tracking
- **GitHub Integration** - Auto-create epics from roadmap items, link specs to issues, sync milestones with priorities
- **Guided Workflows** - Step-by-step interactive initialization with progress tracking, back navigation, and state recovery
- **Persistent Memory** - All project context stored in version-controlled `.doit/memory/` folder
- **Opinionated Approach** - Best practices built-in; strong opinions that reduce decision fatigue
- **AI-Powered** - Works with Claude Code, Cursor, and other AI coding assistants via slash commands
- **Team Collaboration** - Git-based sync, change notifications, conflict resolution, and access control
- **Living Docs** - Automatically organized and indexed project documentation

## The Problem Do-It Solves

Most projects fail not from technical debt, but from **architectural debt** - decisions made early without full context. Teams struggle with:

- Architecture decisions made in isolation
- Specifications that don't stay in sync with code
- Scattered documentation that's always out of date
- Roadmaps that don't reflect actual priorities
- Teams working from different understandings of the same system
- Manual diagram creation that becomes a chore

**Do-It solves this by making specification and decision-making the foundation of development.**

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv tool install doit-toolkit-cli

# Or using pipx
pipx install doit-toolkit-cli

# Or using pip
pip install doit-toolkit-cli
```

### Initialize Your Project

```bash
# Create a new project
doit init my-project

# Or initialize in current directory
doit init .
```

This creates the `.doit/` folder structure with:

- `memory/` - Project context files (constitution, tech-stack, etc.)
- `templates/` - Spec, plan, and task templates
- `scripts/` - Automation scripts (bash and PowerShell)

### The Do-It Workflow (AI Agent Slash Commands)

Do-It provides slash commands for AI coding assistants like Claude Code:

```markdown
# 1. Define your project principles
/doit.constitution This project follows a "Security-First" approach...

# 2. Write your specification
/doit.specit Build a collaborative task management app with real-time updates
# -> Auto-generates: user journey diagram, entity relationships

# 3. Create your technical plan
/doit.planit Use React frontend, Node.js backend, PostgreSQL database
# -> Auto-generates: architecture diagram, component dependencies

# 4. Break down into tasks
/doit.taskit
# -> Auto-generates: task dependencies, phase timeline

# 5. Implement with AI assistance
/doit.implementit

# 6. Run quality assurance
/doit.testit

# 7. Team review
/doit.reviewit

# 8. Check in and archive
/doit.checkin
```

## Commands

### Slash Commands (AI Agent)

Run these in your AI coding assistant (Claude Code, Copilot, etc.):

| Command | Purpose | Output |
|---------|---------|--------|
| **/doit.constitution** | Document project principles | constitution.md |
| **/doit.specit** | Define user stories and features | User journey diagrams, spec.md |
| **/doit.planit** | Create technical architecture | Architecture diagram, plan.md |
| **/doit.taskit** | Break down into tasks | Task dependencies, timeline, tasks.md |
| **/doit.implementit** | Implement features | Executes task queue with AI |
| **/doit.testit** | Quality assurance | Test results, coverage reports |
| **/doit.reviewit** | Team code review | Review findings, review-report.md |
| **/doit.roadmapit** | Manage priorities | roadmap.md with P1-P4 items |
| **/doit.documentit** | Organize documentation | Organized docs/, index.md |
| **/doit.scaffoldit** | Bootstrap new projects | .doit/ structure, templates |
| **/doit.fixit** | Bug-fix workflow | Investigation, fix planning, review |
| **/doit.checkin** | Archive completed work | PR creation, issue closing |

### CLI Commands (Terminal)

Run these in your terminal:

| Command | Purpose |
|---------|---------|
| `doit init` | Initialize Do-It in a project |
| `doit verify` | Verify project structure |
| `doit sync-prompts` | Sync templates to AI agents |
| `doit context show` | Display loaded project context |
| `doit hooks install` | Install git hooks for workflow enforcement |
| `doit hooks validate` | Validate branch meets requirements |
| `doit validate` | Validate spec against quality rules |
| `doit status` | Show spec status dashboard |
| `doit xref` | Cross-reference specs and tasks |
| `doit diagram` | Generate Mermaid diagrams from specs |
| `doit roadmapit show` | Display roadmap with GitHub epics |
| `doit roadmapit add` | Add item and create GitHub epic |
| `doit roadmapit sync-milestones` | Sync GitHub milestones with priorities |
| `doit team sync` | Sync shared memory files |
| `doit team status` | Show team sync status |

## Project Structure

```
your-project/
├── README.md                    # Your project README
├── .doit/                       # Do-It configuration (version control!)
│   ├── memory/
│   │   ├── constitution.md      # Project principles
│   │   ├── tech-stack.md        # Technology choices
│   │   ├── roadmap.md           # Feature priorities (P1-P4)
│   │   └── completed_roadmap.md # Archive of shipped features
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   └── task-template.md
│   └── scripts/
│       ├── bash/                # Bash automation scripts
│       └── powershell/          # PowerShell automation scripts
├── specs/                       # Feature specifications
│   └── NNN-feature-name/
│       ├── spec.md              # Feature specification
│       ├── plan.md              # Technical plan
│       ├── tasks.md             # Task breakdown
│       └── research.md          # Research notes
├── docs/                        # Project documentation
└── src/                         # Your application code
```

## Auto-Generated Diagrams

Do-It automatically generates these diagram types from your specifications:

- **User Journey** - How users interact with your system
- **Architecture** - System components and boundaries
- **Component Dependencies** - Service relationships
- **Entity Relationships** - Database schema
- **Sequence Diagrams** - Time-based interactions
- **Task Dependencies** - Execution order and critical path
- **Phase Timeline** - Gantt chart of development phases
- **Finding Distribution** - Code review findings breakdown

All diagrams are in Mermaid format, work in markdown, and update automatically when specs change.

## Persistent Memory System

Your entire project context lives in version-controlled markdown files:

```
.doit/memory/
├── constitution.md        # "Why do we exist? What are our principles?"
├── tech-stack.md          # "What technologies are we using?"
├── roadmap.md             # "What's the priority order?"
└── completed_roadmap.md   # "What have we shipped?" (20-item archive)
```

Because these files are in git:

- Your entire team sees the same context
- History is preserved (git blame, logs)
- Decisions are documented with rationale
- New team members have full context
- No external dependencies or databases

## Documentation

- [Installation Guide](docs/installation.md) - Getting started with Do-It
- [Quick Start Guide](docs/quickstart.md) - 5-minute tutorial
- [Template System](docs/templates/index.md) - Understanding templates
- [Command Reference](docs/templates/commands.md) - All slash commands explained
- [Workflow System Guide](docs/guides/workflow-system-guide.md) - Interactive workflow architecture
- [Creating Workflows Tutorial](docs/tutorials/creating-workflows.md) - Build custom workflows

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

**Quick start for contributors:**

```bash
# Clone the repo
git clone https://github.com/seanbarlow/doit.git
cd doit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run platform-specific tests
pytest -m windows  # Windows E2E tests
pytest -m macos    # macOS E2E tests (requires macOS)
```

## License

Do-It is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## Reporting Issues

Found a bug? Have a feature request?

- **[GitHub Issues](https://github.com/seanbarlow/doit/issues)** - Bug reports and feature requests
- **[Discussions](https://github.com/seanbarlow/doit/discussions)** - Questions and ideas

Please include:
- Do-It version (`doit --version`)
- Python version (`python --version`)
- Operating system
- Steps to reproduce (for bugs)
- Expected vs. actual behavior

## Status

- **Current Version:** 0.1.11
- **Python Support:** 3.11, 3.12
- **Status:** Beta
- **Last Updated:** January 2026

See [CHANGELOG.md](./CHANGELOG.md) for release notes.

## Acknowledgments

- Diagram generation powered by [Mermaid](https://mermaid.js.org/)
- CLI built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)

---

<div align="center">

Made with care by the Do-It community

[Star us on GitHub](https://github.com/seanbarlow/doit)

</div>
