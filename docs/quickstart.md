# Quick Start Guide

This guide will help you get started with Spec-Driven Development using Do-It.

> [!NOTE]
> All automation scripts provide both Bash (`.sh`) and PowerShell (`.ps1`) variants. The `doit` CLI auto-selects based on OS unless you pass `--script sh|ps`.

## The Do-It Workflow

> [!TIP]
> **Context Awareness**: Do-It commands automatically detect the active feature based on your current Git branch (e.g., `001-feature-name`). To switch between different specifications, simply switch Git branches.

### Step 1: Install Do-It

**In your terminal**, run the `doit` CLI command to initialize your project:

```bash
# Create a new project directory
uvx doit-toolkit-cli init <PROJECT_NAME>

# OR initialize in the current directory
uvx doit-toolkit-cli init .
```

Pick script type explicitly (optional):

```bash
uvx doit-toolkit-cli init <PROJECT_NAME> --script ps  # Force PowerShell
uvx doit-toolkit-cli init <PROJECT_NAME> --script sh  # Force POSIX shell
```

### Step 2: Define Your Constitution

**In your AI Agent's chat interface**, use the `/doit.constitution` slash command to establish the core rules and principles for your project.

```markdown
/doit.constitution This project follows a "Library-First" approach. All features must be implemented as standalone libraries first. We use TDD strictly. We prefer functional programming patterns.
```

### Step 3: Scaffold Your Project (Greenfield Only)

For new projects, use `/doit.scaffoldit` to generate the initial project structure:

```markdown
/doit.scaffoldit
```

This creates the folder structure and starter files based on your constitution.

### Step 4: Create a Feature Specification

**In the chat**, use the `/doit.specit` slash command to describe what you want to build. Focus on the **what** and **why**, not the tech stack.

```markdown
/doit.specit Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping. Within each album, photos are previewed in a tile-like interface.
```

The specit command will:

- Create a feature branch
- Ask clarifying questions to resolve ambiguities
- Generate a complete specification document

### Step 5: Create a Technical Implementation Plan

**In the chat**, use the `/doit.planit` slash command to generate a technical implementation plan:

```markdown
/doit.planit
```

This creates an implementation plan with architecture decisions, component contracts, and technical approach.

### Step 6: Generate Implementation Tasks

**In the chat**, use the `/doit.taskit` slash command to create an actionable task list:

```markdown
/doit.taskit
```

### Step 7: Implement the Feature

Use the `/doit.implementit` slash command to execute the tasks:

```markdown
/doit.implementit
```

This iterates through each task, implementing code and marking tasks complete.

### Step 8: Review Your Implementation

Use the `/doit.reviewit` slash command to review the implemented code:

```markdown
/doit.reviewit
```

This checks code against the specification and identifies any issues.

### Step 9: Complete the Feature

Use the `/doit.checkin` slash command to finalize the feature:

```markdown
/doit.checkin
```

This closes GitHub issues, creates a commit, and optionally opens a pull request.

---

## Detailed Example: Building Taskify

Here's a complete example of building a team productivity platform:

### Step 1: Initialize Project

```bash
uvx doit-toolkit-cli init taskify --ai claude
cd taskify
```

### Step 2: Define Constitution

Initialize the project's constitution to set ground rules:

```markdown
/doit.constitution Taskify is a "Security-First" application. All user inputs must be validated. We use a microservices architecture. Code must be fully documented.
```

### Step 3: Scaffold the Project

```markdown
/doit.scaffoldit
```

### Step 4: Create Feature Specification with `/doit.specit`

```markdown
/doit.specit Develop Taskify, a team productivity platform. It should allow users to create projects, add team members, assign tasks, comment and move tasks between boards in Kanban style. Users will be predefined (5 users: one product manager and four engineers). Create three sample projects with standard Kanban columns: "To Do," "In Progress," "In Review," and "Done." No login required for this initial testing phase.
```

The AI will ask clarifying questions like:

- "How should task cards display user assignments?"
- "Should comments be editable by the commenter only?"
- "What colors should indicate different task states?"

Answer these questions to refine the specification.

### Step 5: Generate Implementation Plan with `/doit.planit`

```markdown
/doit.planit
```

The plan will include:

- Architecture decisions
- Component interfaces
- Data models
- API contracts

### Step 6: Create Tasks with `/doit.taskit`

```markdown
/doit.taskit
```

### Step 7: Implement with `/doit.implementit`

```markdown
/doit.implementit
```

### Step 8: Review with `/doit.reviewit`

```markdown
/doit.reviewit
```

### Step 9: Finalize with `/doit.checkin`

```markdown
/doit.checkin
```

---

## Quick Command Reference

### CLI Commands (Terminal)

Run these commands in your terminal:

| Command | Purpose | When to Use |
| ------- | ------- | ----------- |
| `doit init` | Initialize Do-It in a project | Once per project |
| `doit verify` | Verify project structure | After init or to troubleshoot |
| `doit sync-prompts` | Sync templates to AI agents | After template updates |
| `doit context show` | Display loaded project context | Debug context injection |
| `doit hooks install` | Install git hooks for workflow | Once per repo clone |
| `doit hooks validate` | Validate branch meets requirements | Before commit/push |
| `doit validate` | Validate spec against quality rules | Before commit or review |
| `doit status` | Show spec status dashboard | Track spec progress |
| `doit xref` | Cross-reference specs and tasks | Verify traceability |
| `doit diagram` | Generate Mermaid diagrams | After spec/plan updates |

### Slash Commands (AI Agent)

Run these commands in your AI coding assistant (Claude Code, Copilot, etc.):

| Command | Purpose | When to Use |
| ------- | ------- | ----------- |
| `/doit.constitution` | Define project principles | After init, or to update |
| `/doit.scaffoldit` | Generate project structure | Greenfield projects only |
| `/doit.researchit` | Capture business requirements | Before spec (Product Owners) |
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

## Project Context

Do-It automatically loads project context before executing slash commands, providing AI assistants with your project's principles, priorities, and current work.

### View Loaded Context

Use the `doit context show` command to see what context is available:

```bash
# View context summary
doit context show

# View full context in YAML format
doit context show --format yaml
```

### What Gets Loaded

| Context Source | Description | When Loaded |
| -------------- | ----------- | ----------- |
| `constitution.md` | Project principles and governance | Always |
| `tech-stack.md` | Languages, frameworks, infrastructure | Always |
| `roadmap.md` | Current priorities (P1-P4 items) | Always |
| Current spec | Feature specification for active branch | When on feature branch |
| Related specs | Specifications matching keywords | As relevant |

### Configure Context

The context system uses `.doit/context.yaml` for configuration:

```yaml
# .doit/config/context.yaml
max_related_specs: 3      # Maximum related specs to include
include_roadmap: true     # Include roadmap priorities
include_constitution: true # Include project principles
include_tech_stack: true  # Include tech stack details
```

Context injection ensures AI assistants understand your project's constraints, goals, and current priorities without manual copy-pasting.

## Workflow Enforcement (Optional)

Do-It can enforce spec-first development using Git hooks, ensuring code changes are always backed by specifications.

### Install Hooks

```bash
# Install pre-commit and pre-push hooks
doit hooks install

# Remove installed hooks
doit hooks uninstall
```

### What Hooks Validate

| Hook | Validates | When |
| ---- | --------- | ---- |
| pre-commit | Feature branch has spec.md | Before each commit |
| pre-commit | Spec status is not "Draft" for code changes | Before each commit |
| pre-push | Required artifacts exist (spec.md, plan.md, tasks.md) | Before push |

### Configure Hooks

Customize validation in `.doit/hooks.yaml`:

```yaml
# .doit/hooks.yaml
protected_branches:
  - main
  - develop
require_spec: true
require_plan: true
require_tasks: true
allow_draft_commits: false  # Block commits with Draft specs
```

### Bypass (Emergency)

For emergency fixes, bypass hooks with `--no-verify`:

```bash
git commit --no-verify -m "hotfix: critical production issue"
```

> [!WARNING]
> Use `--no-verify` sparingly. Bypassed commits should be retroactively documented.

## Git Provider Configuration

Do-It integrates with multiple git providers for issue tracking, pull/merge requests, and milestone management.

### Supported Providers

| Provider | Features | Setup |
|----------|----------|-------|
| GitHub | Issues, PRs, Milestones | `doit provider wizard` or `GITHUB_TOKEN` |
| GitLab | Issues, MRs, Milestones | `doit provider wizard` or `GITLAB_TOKEN` |
| Azure DevOps | Work Items, PRs, Iterations | `doit provider wizard` or `AZURE_DEVOPS_TOKEN` |

### Quick Setup

Run the interactive provider wizard:

```bash
doit provider wizard
```

The wizard will:
1. Auto-detect your provider from the git remote URL
2. Prompt for your Personal Access Token
3. Validate the token against the provider API
4. Save configuration to `.doit/config/provider.yaml`

### Provider-Specific Tutorials

- [GitLab Provider Tutorial](./tutorials/04-gitlab-provider-tutorial.md) - Complete guide for GitLab integration

## Key Principles

- **Be explicit** about what you're building and why
- **Don't focus on tech stack** during specification phase
- **Iterate and refine** your specifications before implementation
- **Let the AI agent handle** the implementation details

## Next Steps

- Follow the [Greenfield Tutorial](./tutorials/01-greenfield-tutorial.md) for a complete walkthrough
- Follow the [Existing Project Tutorial](./tutorials/02-existing-project-tutorial.md) to add Do-It to existing code
- Read the [complete methodology](./index.md) for in-depth guidance
- Explore the [source code on GitHub](https://github.com/seanbarlow/doit)
