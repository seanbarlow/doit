# Quick Start Guide

This guide will help you get started with Spec-Driven Development using DoIt.

> [!NOTE]
> All automation scripts provide both Bash (`.sh`) and PowerShell (`.ps1`) variants. The `doit` CLI auto-selects based on OS unless you pass `--script sh|ps`.

## The DoIt Workflow

> [!TIP]
> **Context Awareness**: DoIt commands automatically detect the active feature based on your current Git branch (e.g., `001-feature-name`). To switch between different specifications, simply switch Git branches.

### Step 1: Install DoIt

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

| Command | Purpose | When to Use |
| ------- | ------- | ----------- |
| `doit init` | Initialize DoIt in a project | Once per project |
| `/doit.constitution` | Define project principles | After init, or to update |
| `/doit.scaffoldit` | Generate project structure | Greenfield projects only |
| `/doit.specit` | Create feature specification | Start of each feature |
| `/doit.planit` | Generate implementation plan | After spec is approved |
| `/doit.taskit` | Create actionable tasks | After plan is approved |
| `/doit.implementit` | Execute tasks | During development |
| `/doit.reviewit` | Review implementation | After implementation |
| `/doit.testit` | Run automated tests | Before/after changes |
| `/doit.checkin` | Finalize feature | When feature is complete |
| `/doit.roadmapit` | Manage project backlog | Anytime |
| `/doit.documentit` | Organize documentation | As needed |

## Key Principles

- **Be explicit** about what you're building and why
- **Don't focus on tech stack** during specification phase
- **Iterate and refine** your specifications before implementation
- **Let the AI agent handle** the implementation details

## Next Steps

- Follow the [Greenfield Tutorial](./tutorials/01-greenfield-tutorial.md) for a complete walkthrough
- Follow the [Existing Project Tutorial](./tutorials/02-existing-project-tutorial.md) to add DoIt to existing code
- Read the [complete methodology](./index.md) for in-depth guidance
- Explore the [source code on GitHub](https://github.com/seanbarlow/doit)
