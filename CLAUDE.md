# doit-toolkit-cli Development Guidelines

## Project Overview

doit is a Python CLI tool for **Spec-Driven Development (SDD)** — an AI-assisted workflow that streamlines the software development lifecycle from requirements gathering through implementation and testing. Published on PyPI as `doit-toolkit-cli`.

## Tech Stack

- **Language**: Python 3.11+ (required minimum)
- **CLI**: Typer (type-safe commands)
- **Output**: Rich (terminal formatting — use Rich, not print)
- **HTTP**: httpx (with SOCKS proxy support)
- **Config**: PyYAML for YAML configs, JSON for state
- **File ops**: pathlib.Path (not os.path)
- **Testing**: pytest with markers (`windows`, `macos`, `e2e`, `filesystem`, `slow`, `ci`)
- **Linting**: ruff
- **Build**: hatchling

## Project Structure

```text
src/doit_cli/
  cli/              # Typer CLI commands (18 subcommands)
  services/         # Business logic (69 service modules)
  models/           # Dataclasses (31 model modules)
  formatters/       # Output formatters (Rich, JSON, Markdown)
  utils/            # Shared utilities
  templates/        # Bundled templates (copied to .doit/ on init)
  prompts/          # Interactive prompt helpers
  rules/            # Built-in validation rules
tests/
  unit/             # Unit tests
  integration/      # Integration tests
  contract/         # Contract tests
  e2e/              # End-to-end tests (windows/, macos/)
specs/              # Feature specifications (NNN-feature-name/)
docs/               # Documentation (70+ markdown files)
.doit/              # Reference implementation of project structure
  memory/           # Constitution, roadmap, tech-stack (version controlled)
  templates/        # Command templates
  config/           # YAML configs (hooks, validation rules, context)
  state/            # Workflow state persistence (JSON, gitignored)
  scripts/          # Bash and PowerShell automation scripts
  hooks/            # Git hook scripts
```

## Key Commands

```bash
# Development
pip install -e ".[dev]"        # Install with dev dependencies
pytest tests/unit/             # Run unit tests
pytest tests/ -x --tb=short    # Run all tests, stop on first failure
ruff check src/ tests/         # Lint
ruff format src/ tests/        # Format

# CLI
doit init                      # Initialize .doit/ structure in a project
doit status                    # Show spec status dashboard
doit validate                  # Validate specs against rules
doit verify                    # Verify project structure
doit sync-prompts              # Sync templates to AI agents
```

## Code Conventions

- Use `dataclasses` for models with `__post_init__` validation where needed
- Use abstract base classes for extensible patterns (e.g., `BaseProvider`, `StatusFormatter`)
- Git providers: GitHub, GitLab, Azure DevOps via `services/providers/` abstraction
- Templates are **bundled** in the package at `src/doit_cli/templates/` (not symlinked — avoids Windows issues)
- All `shutil.copy2` calls should use `TemplateManager._safe_copy()` to avoid SameFileError
- Use `httpx` for API calls, never `requests`
- Keep subprocess calls as list arguments (no `shell=True`)

## AI Integration

- **Claude Code**: 12 slash commands in `.claude/commands/` (skills with frontmatter)
- **GitHub Copilot**: 12 prompt files in `.github/prompts/`
- **Workflow**: constitution -> roadmap -> spec -> plan -> tasks -> implement -> test -> review -> checkin

## Testing

- 1749+ tests across unit, integration, contract, and E2E
- Platform-specific tests use markers: `@pytest.mark.windows`, `@pytest.mark.macos`
- CI runs on push/PR to main and develop branches

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

## Active Technologies
- Python 3.11+ (per constitution) + mcp (official MCP Python SDK with FastMCP), typer (CLI), rich (output) (055-mcp-server)
- File-based (markdown in `.doit/memory/`, JSON in `.doit/state/`) (055-mcp-server)
- Python 3.11+ + Typer (CLI), Rich (output), PyYAML (config), httpx (HTTP) (056-persona-context-injection)
- File-based — markdown in `.doit/memory/`, YAML in `.doit/config/` (056-persona-context-injection)
- Python 3.11+ (constitution baseline), but this feature is template-only (Markdown) + None — changes are to Markdown command templates processed by AI assistants (057-persona-aware-user-story-generation)
- File-based — Markdown files in `.doit/memory/` and `specs/{feature}/` (057-persona-aware-user-story-generation)

## Recent Changes
- 055-mcp-server: Added Python 3.11+ (per constitution) + mcp (official MCP Python SDK with FastMCP), typer (CLI), rich (output)
