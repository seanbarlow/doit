# CLI Contract: doit init & doit verify

**Feature**: 010-cli-project-setup | **Date**: 2026-01-10 | **Type**: Command Interface

## Overview

This contract defines the command-line interface for the `doit init` and `doit verify` commands, including arguments, options, return codes, and output formats.

## Commands

### doit init

Initialize a project for the Doit workflow.

#### Synopsis

```
doit init [OPTIONS] [PATH]
```

#### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `PATH` | Path | No | Current directory | Project directory to initialize |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--agent` | `-a` | String | (prompt) | Target agent(s): `claude`, `copilot`, or `claude,copilot` |
| `--templates` | `-t` | Path | (bundled) | Custom template directory path |
| `--update` | `-u` | Flag | False | Update existing project, preserving custom files |
| `--force` | `-f` | Flag | False | Overwrite files without backup |
| `--yes` | `-y` | Flag | False | Skip confirmation prompts |
| `--verbose` | `-v` | Flag | False | Show detailed output |
| `--quiet` | `-q` | Flag | False | Suppress non-error output |

#### Exit Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | SUCCESS | Initialization completed successfully |
| 1 | ERROR | General error (see stderr for details) |
| 2 | INVALID_ARGS | Invalid arguments or options |
| 3 | PERMISSION_DENIED | No write permission to target directory |
| 4 | UNSAFE_DIRECTORY | Attempted to init in system/home directory without --force |
| 5 | TEMPLATE_ERROR | Template source invalid or missing required files |

#### Output Format

**Success (stdout)**:
```
Doit initialized successfully!

Created directories:
  .doit/
  .doit/memory/
  .doit/templates/
  .doit/scripts/
  .claude/commands/

Created files (11):
  .claude/commands/doit.checkin.md
  .claude/commands/doit.constitution.md
  ... (remaining files)

Next steps:
  1. Run /doit.constitution to set up your project constitution
  2. Run /doit.specit to create your first feature specification
  3. Run /doit.planit to create an implementation plan
```

**Error (stderr)**:
```
Error: No write permission to /path/to/project

Suggestion: Check directory permissions or run with appropriate privileges.
```

#### Behavior

1. **Agent Selection**:
   - If `--agent` provided: Use specified agent(s)
   - If existing `.claude/` found: Auto-detect Claude
   - If existing `.github/copilot-instructions.md` found: Auto-detect Copilot
   - Otherwise: Prompt user interactively (unless `--yes`)

2. **Directory Creation**:
   - Create `.doit/` with subdirectories: `memory/`, `templates/`, `scripts/`
   - Create agent-specific directories based on selection
   - Skip existing directories (no error)

3. **Template Copying**:
   - Copy templates from bundled or custom source
   - Preserve exact content (no modifications)
   - Skip existing files unless `--update` or `--force`

4. **Update Mode** (`--update`):
   - Backup existing doit-prefixed files to `.doit/backups/{timestamp}/`
   - Update doit-prefixed files to latest versions
   - Preserve non-doit-prefixed files
   - Preserve `.doit/memory/` contents

5. **Force Mode** (`--force`):
   - Overwrite all files without backup
   - Skip safety confirmations

6. **Safety Checks**:
   - Warn if in home directory or system path
   - Require confirmation or `--force` to proceed
   - Validate write permissions before any changes
   - Rollback on partial failure

---

### doit verify

Verify project setup for Doit workflow.

#### Synopsis

```
doit verify [OPTIONS] [PATH]
```

#### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `PATH` | Path | No | Current directory | Project directory to verify |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--agent` | `-a` | String | (all detected) | Agent(s) to verify: `claude`, `copilot`, or `claude,copilot` |
| `--verbose` | `-v` | Flag | False | Show detailed check results |
| `--json` | | Flag | False | Output results as JSON |

#### Exit Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | ALL_PASSED | All checks passed |
| 1 | HAS_FAILURES | One or more checks failed |
| 2 | INVALID_ARGS | Invalid arguments or options |

#### Output Format

**All Passed (stdout)**:
```
Doit project verification: PASSED

Checks:
  [PASS] .doit/ directory exists
  [PASS] .doit/memory/ directory exists
  [PASS] .claude/commands/ directory exists
  [PASS] All 11 doit commands present
  [PASS] Template versions current

Summary: 5 passed, 0 warnings, 0 failed
```

**Has Failures (stdout)**:
```
Doit project verification: FAILED

Checks:
  [PASS] .doit/ directory exists
  [PASS] .doit/memory/ directory exists
  [FAIL] .claude/commands/ directory missing
  [FAIL] Missing doit commands: doit.specit.md, doit.planit.md

Summary: 2 passed, 0 warnings, 2 failed

Suggestion: Run 'doit init --update' to fix missing components.
```

**JSON Output** (`--json`):
```json
{
  "status": "failed",
  "checks": [
    {"name": ".doit/ directory exists", "status": "pass", "message": "Directory found"},
    {"name": ".claude/commands/ directory exists", "status": "fail", "message": "Directory missing", "suggestion": "Run 'doit init --update'"}
  ],
  "summary": {"passed": 1, "warnings": 0, "failed": 1}
}
```

#### Verification Checks

| Check ID | Name | Pass Condition | Fail Suggestion |
|----------|------|----------------|-----------------|
| V001 | .doit/ exists | Directory exists | Run `doit init` |
| V002 | .doit/memory/ exists | Directory exists | Run `doit init --update` |
| V003 | Agent directory exists | .claude/commands/ or .github/prompts/ | Run `doit init --agent <name>` |
| V004 | All commands present | All 11 doit command files exist | Run `doit init --update` |
| V005 | Templates current | File hashes match bundled templates | Run `doit init --update` (warning only) |
| V006 | No duplicate commands | No conflicting command definitions | Remove duplicates manually |

---

## Interactive Prompts

### Agent Selection Prompt

When no agent is specified and none can be auto-detected:

```
? Which AI coding agent(s) do you use? (Use arrow keys, space to select)
  ● Claude Code
  ○ GitHub Copilot

Press Enter to confirm selection.
```

### Safety Confirmation Prompt

When initializing in home directory or system path:

```
⚠️  Warning: You are about to initialize doit in /home/user

This will create .doit/ and agent directories in your home directory.
This is typically not recommended. Consider initializing in a project directory instead.

? Continue anyway? [y/N]
```

### Update Confirmation Prompt

When updating existing installation:

```
? Found existing doit installation. This will:
  - Backup current commands to .doit/backups/2026-01-10T143022/
  - Update 11 command templates to latest version
  - Preserve custom files and .doit/memory/ contents

Continue? [Y/n]
```

---

## Template Contract

### Required Templates per Agent

#### Claude (11 templates)

| Template | Source | Target |
|----------|--------|--------|
| checkin | templates/commands/doit.checkin.md | .claude/commands/doit.checkin.md |
| constitution | templates/commands/doit.constitution.md | .claude/commands/doit.constitution.md |
| documentit | templates/commands/doit.documentit.md | .claude/commands/doit.documentit.md |
| implementit | templates/commands/doit.implementit.md | .claude/commands/doit.implementit.md |
| planit | templates/commands/doit.planit.md | .claude/commands/doit.planit.md |
| reviewit | templates/commands/doit.reviewit.md | .claude/commands/doit.reviewit.md |
| roadmapit | templates/commands/doit.roadmapit.md | .claude/commands/doit.roadmapit.md |
| scaffoldit | templates/commands/doit.scaffoldit.md | .claude/commands/doit.scaffoldit.md |
| specit | templates/commands/doit.specit.md | .claude/commands/doit.specit.md |
| taskit | templates/commands/doit.taskit.md | .claude/commands/doit.taskit.md |
| testit | templates/commands/doit.testit.md | .claude/commands/doit.testit.md |

#### Copilot (11 templates)

| Template | Source | Target |
|----------|--------|--------|
| checkin | templates/prompts/doit-checkin.prompt.md | .github/prompts/doit-checkin.prompt.md |
| constitution | templates/prompts/doit-constitution.prompt.md | .github/prompts/doit-constitution.prompt.md |
| documentit | templates/prompts/doit-documentit.prompt.md | .github/prompts/doit-documentit.prompt.md |
| implementit | templates/prompts/doit-implementit.prompt.md | .github/prompts/doit-implementit.prompt.md |
| planit | templates/prompts/doit-planit.prompt.md | .github/prompts/doit-planit.prompt.md |
| reviewit | templates/prompts/doit-reviewit.prompt.md | .github/prompts/doit-reviewit.prompt.md |
| roadmapit | templates/prompts/doit-roadmapit.prompt.md | .github/prompts/doit-roadmapit.prompt.md |
| scaffoldit | templates/prompts/doit-scaffoldit.prompt.md | .github/prompts/doit-scaffoldit.prompt.md |
| specit | templates/prompts/doit-specit.prompt.md | .github/prompts/doit-specit.prompt.md |
| taskit | templates/prompts/doit-taskit.prompt.md | .github/prompts/doit-taskit.prompt.md |
| testit | templates/prompts/doit-testit.prompt.md | .github/prompts/doit-testit.prompt.md |

### Copilot Instructions File

When initializing for Copilot, the command creates or updates `.github/copilot-instructions.md`:

```markdown
# Copilot Instructions

[Existing content preserved]

<!-- DOIT INSTRUCTIONS START -->
## Doit Workflow Commands

This project uses the Doit workflow for structured development. The following prompts are available in `.github/prompts/`:

| Command | Description |
|---------|-------------|
| #doit-specit | Create feature specifications |
| #doit-planit | Generate implementation plans |
| #doit-taskit | Create task breakdowns |
| #doit-implementit | Execute implementation tasks |
| #doit-testit | Run tests and generate reports |
| #doit-reviewit | Review code for quality |
| #doit-checkin | Complete feature and create PR |
| #doit-constitution | Manage project constitution |
| #doit-scaffoldit | Scaffold new projects |
| #doit-roadmapit | Manage feature roadmap |
| #doit-documentit | Manage documentation |

Use the agent mode (`@workspace /doit-*`) for multi-step workflows.
<!-- DOIT INSTRUCTIONS END -->
```
