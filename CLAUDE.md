# doit Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-10

## Active Technologies
- Bash 5.x (file operations only) + None (standard Unix utilities: rm, cp) (004-review-template-commands)
- N/A (file system operations) (004-review-template-commands)
- Markdown (templates), Bash 5.x (helper scripts if needed) + Mermaid syntax (rendered by GitHub/VS Code), Claude Code slash command system (005-mermaid-visualization)
- N/A (file-based template system) (005-mermaid-visualization)
- Bash 5.x (text processing), Markdown (documentation) + grep, sed (standard Unix utilities) (006-docs-doit-migration)
- N/A (file-based documentation) (006-docs-doit-migration)
- Python 3.11+ + yper, rich, shutil (stdlib), pathlib (stdlib) (011-init-scripts-copy)
- File system only (011-init-scripts-copy)
- Markdown (command templates), Bash 5.x (scripts) + Claude Code slash command system, existing doit template structure (012-command-recommendations)
- N/A (file-based templates only) (012-command-recommendations)
- Python 3.11+ + hatchling (build), typer (CLI), rich (formatting) (013-publish-pypi)
- N/A (no database) (013-publish-pypi)
- Bash scripts, gh CLI, Markdown (YAML for templates) + gh CLI (GitHub CLI), Gi (014-github-repo-protections)
- N/A (GitHub API / repository settings) (014-github-repo-protections)
- Markdown, JSON (documentation files) + None (text editing only) (015-docs-branding-cleanup)
- N/A (file system) (015-docs-branding-cleanup)
- Bash 5.x, PowerShell 7.x + Standard Unix utilities (grep, sed, diff, cp), Git CLI (016-scripts-cleanup)
- N/A (file system only) (016-scripts-cleanup)
- Markdown (file content only - no code changes) + None (file system operations only) (017-roadmap-template-cleanup)
- Markdown (documentation), Mermaid (diagrams) + None (documentation only) (019-doit-tutorials)
- N/A (file system - docs directory) (019-doit-tutorials)
- Markdown (command templates), Claude Code slash command system + None (template-based execution by AI agent) (020-constitution-improvements)
- N/A (file system - reads project directories) (020-constitution-improvements)
- Markdown (YAML frontmatter) + None (text files only) (021-copilot-agent-fix)
- N/A (no database involved) (021-copilot-agent-fix)
- Python 3.11+ (per constitution) + Typer (CLI), Rich (output formatting), pathlib (file operations) (023-copilot-prompts-sync)
- File-based (markdown files in `.github/prompts/`) (023-copilot-prompts-sync)
- Python 3.11+ (per constitution) + Typer, Rich, pytest (per constitution) (024-unified-templates)
- File-based (markdown templates in `templates/commands/`) (024-unified-templates)
- Python 3.11+ (per constitution) + Typer (CLI), Rich (output), PyYAML (configuration) (025-git-hooks-workflow)
- File-based - `.doit/config/hooks.yaml` for configuration, `.doit/logs/hook-bypasses.log` for audit (025-git-hooks-workflow)
- Python 3.11+ (per constitution) + Typer, Rich, PyYAML (for configuration) (026-ai-context-injection)
- File-based (markdown in `.doit/memory/`) (026-ai-context-injection)
- Markdown (command templates are markdown files) + None (template modifications only) (027-template-context-injection)
- N/A (file-based templates in `templates/commands/`) (027-template-context-injection)
- N/A (Markdown documentation only) (028-docs-tutorial-refresh)
- Python 3.11+ (per constitution) + Typer (CLI), Rich (output formatting), PyYAML (custom rules configuration) (029-spec-validation-linting)
- File-based (markdown specs in `specs/` directory) (029-spec-validation-linting)
- Python 3.11+ + Typer (CLI), Rich (terminal formatting/progress), readchar (keyboard input) (030-guided-workflows)
- File-based JSON in `.doit/state/` for workflow state persistence (030-guided-workflows)
- Python 3.11+ (from constitution) + Typer (CLI), Rich (terminal UI), pytest (testing) (031-init-workflow-integration)
- File-based (`.doit/state/` for workflow state, `.doit/memory/` for project context) (031-init-workflow-integration)
- Python 3.11+ (per constitution) + Typer (CLI), Rich (terminal formatting) (032-status-dashboard)
- File-based (reads `specs/` directory and spec.md files) (032-status-dashboard)
- Python 3.11+ (per constitution) + Typer (CLI), Rich (output formatting), httpx (GitHub API) (034-fixit-workflow)
- File-based markdown in `.doit/memory/` and feature directory (034-fixit-workflow)
- Python 3.11+ (per constitution) + Typer (CLI), Rich (terminal output), httpx (HTTP client) (039-github-roadmap-sync)
- File-based markdown in `.doit/memory/` + GitHub API (read/write) (039-github-roadmap-sync)
- Python 3.11+ (per constitution) + Typer (CLI framework), Rich (terminal output), httpx (GitHub API client) (040-spec-github-linking)
- File-based (`.doit/memory/roadmap.md` for roadmap data, spec frontmatter for link metadata) (040-spec-github-linking)
- Python 3.11+ + Typer (CLI), Rich (terminal output), httpx (HTTP client), pytest (testing) (041-milestone-generation)
- File-based markdown in `.doit/memory/roadmap.md` and `.doit/memory/completed_roadmap.md` (041-milestone-generation)
- Python 3.11+ + Typer (CLI), Rich (terminal output), PyYAML (configuration), watchdog (file monitoring) (042-team-collaboration)
- File-based YAML in `.doit/config/team.yaml`, JSON in `.doit/state/`, markdown in `.doit/memory/` (042-team-collaboration)
- Python 3.11+ (from constitution) + Typer, Rich, httpx, pytest (from constitution) (043-unified-cli)
- File-based markdown (no database) (043-unified-cli)
- Python 3.11+ + Typer (CLI), Rich (output), httpx (HTTP client), pytest (testing) (044-git-provider-abstraction)
- File-based (`.doit/config/provider.yaml` for provider settings) (044-git-provider-abstraction)
- Python 3.11+ + Typer (CLI), Rich (terminal formatting), readchar (keyboard input) (046-constitution-tech-stack-split)

- Markdown (command definitions), Bash 5.x (scripts), Python 3.11+ (CLI) + Claude Code slash command system, GitHub MCP server, typer, rich, httpx (001-doit-command-refactor)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Markdown (command definitions), Bash 5.x (scripts), Python 3.11+ (CLI): Follow standard conventions

## Recent Changes
- 046-constitution-tech-stack-split: Added Python 3.11+ + Typer (CLI), Rich (terminal formatting), readchar (keyboard input)
- 044-git-provider-abstraction: Added Python 3.11+ + Typer (CLI), Rich (output), httpx (HTTP client), pytest (testing)
- 043-unified-cli: Added Python 3.11+ (from constitution) + Typer, Rich, httpx, pytest (from constitution)



<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
