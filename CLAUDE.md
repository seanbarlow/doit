# doit Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-10

## Active Technologies
- Bash 5.x (file operations only) + None (standard Unix utilities: rm, cp) (004-review-template-commands)
- N/A (file system operations) (004-review-template-commands)

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
- 004-review-template-commands: Added Bash 5.x (file operations only) + None (standard Unix utilities: rm, cp)

- 003-scaffold-doit-commands: Renamed .specify to .doit, added command template generation
- 002-update-doit-templates: Updated doit templates

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
