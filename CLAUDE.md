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
- 011-init-scripts-copy: Added Python 3.11+ + yper, rich, shutil (stdlib), pathlib (stdlib)

- 009-doit-documentit-command: Added Markdown (command definitions), file-based storage (.doit/memory/, docs/) + Claude Code slash command system
- 008-doit-roadmapit-command: Added Markdown (command definitions), file-based storage (.doit/memory/) + Claude Code slash command system

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
