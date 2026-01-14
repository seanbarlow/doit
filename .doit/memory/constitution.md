# Do-It Constitution

## Purpose & Goals

### Project Purpose

Do-It is a spec-driven development framework that enables teams to see their architecture before they build it. It provides an opinionated, AI-powered approach to specification-driven development with auto-generated diagrams, intelligent roadmapping, and persistent memory.

### Success Criteria

- Enable consistent specification and task breakdown across teams
- Reduce architectural debt through upfront specification
- Provide AI-powered workflow integration with Claude Code, Cursor, and other assistants
- Maintain all project context in version-controlled markdown files
- Auto-generate Mermaid diagrams from specifications

## Tech Stack

### Languages

Python 3.11+ (primary)

### Frameworks

- Typer (CLI framework)
- pytest (testing framework)
- Hatchling (build system)

### Libraries

- Rich (terminal formatting and output)
- httpx (HTTP client with SOCKS support)
- platformdirs (cross-platform directories)
- readchar (keyboard input)
- truststore (certificate handling)

## Infrastructure

### Hosting

PyPI (Python Package Index) - distributed as `doit-toolkit-cli`

### Cloud Provider

None (local CLI tool, no cloud infrastructure required)

### Database

None (file-based storage using markdown in `.doit/memory/`)

## Deployment

### CI/CD Pipeline

GitHub Actions

### Deployment Strategy

Manual release to PyPI via `hatch build` and `hatch publish`

### Environments

- Development (local)
- Production (PyPI)

## Core Principles

### I. Specification-First

Every feature MUST begin with a specification before implementation. Specifications define user stories, acceptance criteria, and success metrics. No code is written until the spec is approved.

### II. Persistent Memory

All project context MUST be stored in version-controlled markdown files within `.doit/memory/`. This ensures team alignment, historical context, and zero external dependencies.

### III. Auto-Generated Diagrams

Diagrams MUST be generated automatically from specifications using Mermaid syntax. Manual diagram maintenance is prohibited - diagrams are derived artifacts.

### IV. Opinionated Workflow

The framework enforces a specific workflow: constitution → specit → planit → taskit → implementit → testit → reviewit → checkin. Deviations require explicit justification.

### V. AI-Native Design

All commands MUST be designed to work with AI coding assistants via slash commands. Human-readable markdown is the universal interface.

## Quality Standards

All code MUST include tests. The test suite uses pytest and MUST pass before any release. Code coverage is tracked but not enforced with a hard minimum.

## Development Workflow

1. Create feature branch from `main`
2. Run `/doit.specit` to create specification
3. Run `/doit.planit` for technical design
4. Run `/doit.taskit` for task breakdown
5. Implement with `/doit.implementit`
6. Review with `/doit.reviewit`
7. Check in with `/doit.checkin`

## Governance

This constitution supersedes all other development practices for this project. Amendments require:

1. A specification documenting the change rationale
2. Team review and approval
3. Version bump following semantic versioning
4. Migration plan for breaking changes

All pull requests MUST verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-13
