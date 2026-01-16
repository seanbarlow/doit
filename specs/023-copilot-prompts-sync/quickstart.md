# Quickstart: GitHub Copilot Prompts Synchronization

**Feature**: 023-copilot-prompts-sync
**Date**: 2026-01-15

## Overview

This feature adds a CLI command to synchronize GitHub Copilot prompt files with doit command templates, ensuring both AI assistants (Claude Code and GitHub Copilot) have access to the same workflow instructions.

## Usage

### Sync All Commands

Generate prompt files for all doit commands:

```bash
doit sync-prompts
```

**Output**:
```
Syncing prompts...
✓ Created: .github/prompts/doit.checkin.prompt.md
✓ Created: .github/prompts/doit.constitution.prompt.md
✓ Created: .github/prompts/doit.documentit.prompt.md
...
✓ Sync complete: 11 created, 0 updated, 0 skipped
```

### Check Sync Status

Check if prompts are in sync without making changes:

```bash
doit sync-prompts --check
```

**Output**:
```
Checking sync status...
✓ doit.checkin: synchronized
✓ doit.constitution: synchronized
✗ doit.specit: out-of-sync (command modified 2026-01-15)
! doit.newcommand: missing

Status: 9 synchronized, 1 out-of-sync, 1 missing
```

### Sync Specific Command

Sync only a specific command:

```bash
doit sync-prompts doit.checkin
```

**Output**:
```
Syncing doit.checkin...
✓ Updated: .github/prompts/doit.checkin.prompt.md
```

### Force Overwrite

Force regeneration even if prompt is already in sync:

```bash
doit sync-prompts --force
```

## File Locations

| Type | Location |
| ---- | -------- |
| Command Templates | `.doit/templates/commands/doit.*.md` |
| Generated Prompts | `.github/prompts/doit.*.prompt.md` |

## Naming Convention

| Command Template | Generated Prompt |
| ---------------- | ---------------- |
| `doit.checkin.md` | `doit.checkin.prompt.md` |
| `doit.specit.md` | `doit.specit.prompt.md` |
| `doit.planit.md` | `doit.planit.prompt.md` |

## Integration with GitHub Copilot

After running `doit sync-prompts`, GitHub Copilot will recognize the prompt files:

1. Open your project in VS Code with GitHub Copilot enabled
2. Use `@workspace` to invoke custom agents
3. Reference the doit workflows by name (e.g., "use the doit.specit workflow")

## Workflow Integration

This command fits into the doit development workflow:

```
constitution → specit → planit → taskit → implementit → testit → reviewit → checkin
                                                                              ↓
                                                                        sync-prompts
```

Run `doit sync-prompts` after:
- Adding new doit commands
- Modifying existing command templates
- Before sharing the project with Copilot users

## Troubleshooting

### "Directory not found" Error

The `.github/prompts/` directory is created automatically. If you see this error, check write permissions.

### "Invalid YAML" Warning

If a command template has malformed YAML frontmatter:
- The sync will continue with remaining commands
- The problematic file will be reported
- Fix the YAML and re-run sync

### Drift Detection

Commands and prompts can drift when:
- Someone edits a command template directly
- A new command is added via `/doit.constitution`
- The repository is cloned without running sync

Use `--check` regularly to detect drift early.
