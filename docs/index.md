<div align="center">
  <img src="../media/doit-logo-full-color.svg" alt="Do-It Framework Logo" width="200">
</div>

# Do-It

*Build high-quality software faster.*

**An effort to allow organizations to focus on product scenarios rather than writing undifferentiated code with the help of Spec-Driven Development.**

## What is Spec-Driven Development?

Spec-Driven Development **flips the script** on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: **specifications become executable**, directly generating working implementations rather than just guiding them.

## Getting Started

- [Installation Guide](installation.md)
- [Quick Start Guide](quickstart.md)
- [Upgrade Guide](upgrade.md)
- [Local Development](local-development.md)

<!-- BEGIN:AUTO-GENERATED section="documentation-index" -->

## Features

| Document | Description | Last Modified |
| -------- | ----------- | ------------- |
| [Scaffold Doit Commands](./features/003-scaffold-doit-commands.md) | When initializing a new project using the `/doit.scaffoldit` command... | 2026-01-10 |
| [Review Template Commands](./features/004-review-template-commands.md) | Remove legacy doit templates from `templates/commands/`... | 2026-01-10 |
| [Automatic Mermaid Visualization](./features/005-mermaid-visualization.md) | Enhance the doit template system to automatically generate mermaid diagrams... | 2026-01-10 |
| [Documentation Doit Migration](./features/006-docs-doit-migration.md) | Comprehensive audit and update of all documentation... | 2026-01-10 |
| [Doit Roadmapit Command](./features/008-doit-roadmapit-command.md) | The `/doit.roadmapit` command creates and manages project roadmaps... | 2026-01-10 |
| [Doit Documentit Command](./features/009-doit-documentit-command.md) | Added `/doit.documentit` command for documentation management... | 2026-01-10 |
| [Command Workflow Recommendations](./features/012-command-recommendations.md) | Enhanced all doit workflow commands to provide context-aware recommendations... | 2026-01-10 |
| [Documentation Branding Cleanup](./features/015-docs-branding-cleanup.md) | Clean up documentation to remove legacy branding references... | 2026-01-12 |
| [Scripts Cleanup](./features/016-scripts-cleanup.md) | Cleaned up Bash and PowerShell scripts to support only Claude and Copilot... | 2026-01-12 |
| [Roadmap Template Cleanup](./features/017-roadmap-template-cleanup.md) | Updated roadmap templates to contain placeholder syntax... | 2026-01-13 |
| [Develop Branch Setup](./features/018-develop-branch-setup.md) | Implemented Gitflow-inspired branching strategy with develop branch... | 2026-01-13 |
| [Constitution Improvements](./features/020-constitution-improvements.md) | Improved `/doit.constitution` with dotfile exclusion and greenfield detection... | 2026-01-13 |
| [Copilot Prompt File Fix](./features/021-copilot-agent-fix.md) | Updated Copilot prompt files to use `agent: true` specification... | 2026-01-13 |
| [Documentation Logo Integration](./features/022-docs-logo-integration.md) | Integrated Do-It framework logos into README and documentation... | 2026-01-14 |
| [Unified Template Management](./features/024-unified-templates.md) | Consolidated command templates into single source of truth... | 2026-01-15 |
| [Git Hooks Workflow](./features/025-git-hooks-workflow.md) | Git hook integration for spec-driven workflow enforcement... | 2026-01-15 |
| [AI Context Injection](./features/026-ai-context-injection.md) | Automatic project context loading for AI assistant commands... | 2026-01-15 |
| [Template Context Injection](./features/027-template-context-injection.md) | Integrated context loading into all 11 doit command templates... | 2026-01-15 |
| [Documentation Tutorial Refresh](./features/028-docs-tutorial-refresh.md) | Refreshed tutorials and documentation for current workflow... | 2026-01-15 |
| [Spec Validation and Linting](./features/029-spec-validation-linting.md) | Added `doit validate` command with quality rules and scoring... | 2026-01-15 |
| [Guided Workflows](./features/030-guided-workflows.md) | Interactive step-by-step workflows with validation and recovery... | 2026-01-16 |
| [Init Workflow Integration](./features/031-init-workflow-integration.md) | Init command uses WorkflowEngine with state persistence... | 2026-01-16 |
| [Spec Status Dashboard](./features/032-status-dashboard.md) | Added `doit status` command for spec progress dashboard... | 2026-01-16 |
| [Spec-Task Cross References](./features/033-spec-task-crossrefs.md) | Bidirectional traceability between specs and tasks with `doit xref`... | 2026-01-16 |
| [Bug-Fix Workflow (doit.fixit)](./features/034-fixit-workflow.md) | Structured bug-fix workflow with GitHub integration... | 2026-01-16 |
| [Auto Mermaid Diagrams](./features/035-auto-mermaid-diagrams.md) | Automatic diagram generation with `doit diagram` command... | 2026-01-16 |
| [Update Doit Templates](./features/update-doit-templates.md) | Updated the template files to remove references to non-existent files... | 2026-01-10 |

## Guides

| Document | Description | Last Modified |
| -------- | ----------- | ------------- |
| [Mermaid Diagram Patterns](./guides/diagram-patterns.md) | All auto-generated diagrams use HTML comment markers to identify content... | 2026-01-10 |
| [Workflow System Guide](./guides/workflow-system-guide.md) | Interactive workflow architecture with WorkflowEngine... | 2026-01-16 |

## Tutorials

| Document | Description | Last Modified |
| -------- | ----------- | ------------- |
| [Tutorial Index](./tutorials/index.md) | Overview of Do-It tutorials and learning paths... | 2026-01-14 |
| [Greenfield Tutorial](./tutorials/01-greenfield-tutorial.md) | Building a new project from scratch with Do-It... | 2026-01-14 |
| [Existing Project Tutorial](./tutorials/02-existing-project-tutorial.md) | Adding Do-It to an existing codebase... | 2026-01-14 |
| [Creating Workflows Tutorial](./tutorials/creating-workflows.md) | Build custom interactive workflows... | 2026-01-16 |

## Templates

| Document | Description | Last Modified |
| -------- | ----------- | ------------- |
| [Template System Overview](./templates/index.md) | The doit template system provides a structured workflow for development... | 2026-01-10 |
| [Command Templates](./templates/commands.md) | Command templates define the workflow logic for the doit system... | 2026-01-10 |
| [Root Templates](./templates/root-templates.md) | Root templates define the structure and format of generated artifacts... | 2026-01-10 |
| [Template Enhancements](./templates/enhancements.md) | Opportunities to enhance the doit template system... | 2026-01-10 |

<!-- END:AUTO-GENERATED -->

## Core Philosophy

Spec-Driven Development is a structured process that emphasizes:

- **Intent-driven development** where specifications define the "*what*" before the "*how*"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

## Development Phases

| Phase | Focus | Key Activities |
|-------|-------|----------------|
| **0-to-1 Development** ("Greenfield") | Generate from scratch | <ul><li>Start with high-level requirements</li><li>Generate specifications</li><li>Plan implementation steps</li><li>Build production-ready applications</li></ul> |
| **Creative Exploration** | Parallel implementations | <ul><li>Explore diverse solutions</li><li>Support multiple technology stacks & architectures</li><li>Experiment with UX patterns</li></ul> |
| **Iterative Enhancement** ("Brownfield") | Brownfield modernization | <ul><li>Add features iteratively</li><li>Modernize legacy systems</li><li>Adapt processes</li></ul> |

## Experimental Goals

Our research and experimentation focus on:

### Technology Independence

- Create applications using diverse technology stacks
- Validate the hypothesis that Spec-Driven Development is a process not tied to specific technologies, programming languages, or frameworks

### Enterprise Constraints

- Demonstrate mission-critical application development
- Incorporate organizational constraints (cloud providers, tech stacks, engineering practices)
- Support enterprise design systems and compliance requirements

### User-Centric Development

- Build applications for different user cohorts and preferences
- Support various development approaches (from vibe-coding to AI-native development)

### Creative & Iterative Processes

- Validate the concept of parallel implementation exploration
- Provide robust iterative feature development workflows
- Extend processes to handle upgrades and modernization tasks

## Contributing

Please see our [Contributing Guide](https://github.com/seanbarlow/doit/blob/main/CONTRIBUTING.md) for information on how to contribute to this project.

## Support

For support, please open an issue on [GitHub](https://github.com/seanbarlow/doit/issues) or check our documentation.
