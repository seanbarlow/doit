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
- 020-constitution-improvements: Added Markdown (command templates), Claude Code slash command system + None (template-based execution by AI agent)
- 019-doit-tutorials: Added Markdown (documentation), Mermaid (diagrams) + None (documentation only)
- 017-roadmap-template-cleanup: Added Markdown (file content only - no code changes) + None (file system operations only)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
