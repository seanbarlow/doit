# Copilot Instructions for doit-toolkit-cli

## Project Overview

doit is a Python CLI tool for **Spec-Driven Development (SDD)** — an AI-assisted workflow that streamlines the software development lifecycle from requirements gathering through implementation and testing.

## Architecture

- **Language**: Python 3.11+
- **CLI Framework**: Typer with Rich terminal formatting
- **Package**: `doit-toolkit-cli` on PyPI (importable as `doit_cli`)
- **Structure**: `src/doit_cli/` with `cli/`, `services/`, `models/`, `formatters/`, `utils/`
- **Git Providers**: Abstraction layer supporting GitHub, GitLab, Azure DevOps

## Workflow Commands

The project provides 12 slash commands that form a complete SDD lifecycle. Prompt files are in `.github/prompts/`:

1. `/doit.constitution` - Define project principles and tech stack
2. `/doit.roadmapit` - Manage prioritized feature roadmap (P1-P4)
3. `/doit.scaffoldit` - Generate project structure per tech stack
4. `/doit.specit` - Create feature specifications from natural language
5. `/doit.planit` - Design implementation plans from specs
6. `/doit.taskit` - Break plans into dependency-ordered tasks
7. `/doit.implementit` - Execute tasks with progress tracking
8. `/doit.testit` - Run tests and map to requirements
9. `/doit.reviewit` - Review code against spec requirements
10. `/doit.checkin` - Finalize, close issues, create PR
11. `/doit.fixit` - Bug-fix workflow with investigation phases
12. `/doit.documentit` - Organize and audit documentation

## Code Conventions

- Use `typer` for CLI commands with type annotations
- Use `rich` for terminal output (not print statements)
- Use `httpx` for HTTP requests (not requests)
- Use `pathlib.Path` for file operations (not os.path)
- Use dataclasses for models
- Tests use `pytest` with markers: `windows`, `macos`, `e2e`, `filesystem`, `slow`
- Template files are bundled in `src/doit_cli/templates/` (not symlinked)

## Project Structure

```
.doit/memory/       # Project context (constitution, roadmap, tech-stack)
.doit/templates/    # Command templates
.doit/config/       # YAML configuration (hooks, validation rules, context)
.doit/state/        # Workflow state persistence (JSON)
specs/NNN-feature/  # Feature specifications with spec.md, plan.md, tasks.md
```

## Key Principles

- Specifications drive all implementation decisions
- Constitution defines project-wide principles and tech stack
- Roadmap items have P1-P4 priority levels
- All features flow through: spec -> plan -> tasks -> implement -> test -> review -> checkin
