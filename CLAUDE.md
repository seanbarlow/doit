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
- **Error handling**: raise a subclass of `doit_cli.errors.DoitError` at boundaries; chain with `raise X(...) from e` inside `except` blocks (ruff B904 enforced)
- **Exit codes**: every `typer.Exit(code=…)` call uses a `doit_cli.exit_codes.ExitCode` constant, never a numeric literal
- **Output formats**: CLI commands that produce reports accept `--format/-f` declared via `doit_cli.cli.output.format_option()` with a per-command `allowed` subset
- **Python modernity**: every `src/doit_cli/**/*.py` starts with `from __future__ import annotations`; type hints use `list[X] / X | None`, not `List/Optional`

## AI Integration

Two template layouts ship side by side during the April 2026 Agent Skills transition:

- **Claude Code (skills, current)**: 1 skill so far at `src/doit_cli/templates/skills/doit.constitution/SKILL.md`; the other 12 templates migrate in follow-ups (Phase 5b, 5c). Format documented in `docs/templates/agent-skills.md`.
- **Claude Code (commands, legacy)**: 13 flat files in `src/doit_cli/templates/commands/doit.*.md`; still works per Anthropic's back-compat window. Synced to `.claude/commands/` by `doit sync-prompts`.
- **GitHub Copilot**: 13 `.prompt.md` files in `.github/prompts/`, generated from the command sources by `PromptTransformer` (April 2026 Copilot schema: `agent: agent`, `tools: [...]`, `${input:args}` placeholders). Format documented in `docs/templates/copilot-prompts.md`.
- **Workflow**: constitution → roadmap → researchit → specit → planit → taskit → implementit → testit → reviewit → fixit → documentit → scaffoldit → checkin

## Testing

- 1,800+ tests across unit, integration, contract, and E2E
- Platform-specific tests use markers: `@pytest.mark.windows`, `@pytest.mark.macos`
- CI runs on push/PR to main and develop branches
- Contract tests (`tests/contract/`) include a shipped-prompt validator that fails if `.github/prompts/` drifts from the transformer output — re-run `doit sync-prompts --agent copilot` if it fails
- Run mypy manually (non-blocking during the type-hardening window): `pre-commit run mypy --hook-stage manual --all-files`

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

## Active Technologies
- Python 3.11+ (per constitution) + mcp (official MCP Python SDK with FastMCP), typer (CLI), rich (output) (055-mcp-server)
- File-based (markdown in `.doit/memory/`, JSON in `.doit/state/`) (055-mcp-server)
- Python 3.11+ + Typer (CLI), Rich (output), PyYAML (config), httpx (HTTP) (056-persona-context-injection)
- File-based — markdown in `.doit/memory/`, YAML in `.doit/config/` (056-persona-context-injection)
- Python 3.11+ (constitution baseline), but this feature is template-only (Markdown) + None — changes are to Markdown command templates processed by AI assistants (057-persona-aware-user-story-generation)
- File-based — Markdown files in `.doit/memory/` and `specs/{feature}/` (057-persona-aware-user-story-generation)
- N/A — Markdown template authoring only + None — no code changes (058-error-recovery-patterns)
- File-based — Markdown templates in `.doit/templates/commands/` (058-error-recovery-patterns)
- April 2026 modernization sweep: ruff + mypy + DoitError hierarchy + context_loader package split + ExitCode / OutputFormat CLI conventions + Agent Skills layout for Claude + native Copilot `.prompt.md` frontmatter
- Python 3.11+ (per constitution; consistent with rest of repo) + Typer (CLI), Rich (logging), PyYAML (already declared `pyyaml>=6.0` in `pyproject.toml:31`) (059-constitution-frontmatter-migration)
- File-based — markdown in `.doit/memory/constitution.md` (059-constitution-frontmatter-migration)
- Python 3.11+ (constitution baseline) + Typer (CLI), Rich (logging), PyYAML (already declared); no new deps (060-memory-files-migration)
- File-based — markdown in `.doit/memory/{roadmap,tech-stack}.md` (060-memory-files-migration)

## Recent Changes
- 055-mcp-server: Added Python 3.11+ (per constitution) + mcp (official MCP Python SDK with FastMCP), typer (CLI), rich (output)
