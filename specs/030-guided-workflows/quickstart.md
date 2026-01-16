# Quickstart: Interactive Guided Workflows

**Feature**: 030-guided-workflows
**Date**: 2026-01-15

## Overview

This guide explains how to use the interactive guided workflow system in doit commands.

---

## Basic Usage

### Interactive Mode (Default)

When you run a doit command that requires input, you'll be guided step-by-step:

```bash
$ doit init

Step 1 of 4: Select AI Tool

  ▶ claude  (Claude Code / Anthropic)
    cursor  (Cursor IDE)
    copilot (GitHub Copilot)

Use ↑/↓ to navigate, Enter to select
```

### Non-Interactive Mode

For CI/CD pipelines or scripting, use the `--non-interactive` flag:

```bash
$ doit init --non-interactive

# Or set environment variable
$ export DOIT_NON_INTERACTIVE=true
$ doit init
```

---

## Navigation Commands

During any workflow step, you can use these commands:

| Command | Action |
|---------|--------|
| Enter | Accept current selection or default value |
| `back` | Return to previous step |
| `skip` | Skip current step (optional steps only) |
| Ctrl+C | Cancel and save progress |
| Escape | Cancel selection (in choice prompts) |

---

## Progress Visualization

Multi-step workflows show your progress:

```
Step 2 of 5: Configure Project Name

  ✓ Select AI Tool: claude
  ▶ Configure Project Name
    Set Output Directory
    Add Git Integration
    Confirm Settings

Enter project name [my-project]:
```

**Legend**:
- ✓ Completed step
- ▶ Current step
- ○ Pending step
- ⊘ Skipped step

---

## Workflow Recovery

If you cancel a workflow (Ctrl+C), your progress is saved:

```bash
$ doit init
Step 2 of 5: Configure Project Name
^C
Workflow interrupted. Progress saved.

$ doit init
Resume previous workflow? (Step 2 of 5) [Y/n]:
```

Choose:
- **Y** (default): Continue from where you left off
- **n**: Start fresh (previous progress discarded)

---

## Real-Time Validation

Inputs are validated as you type:

```
Enter spec path: /invalid/path

✗ Path does not exist: /invalid/path
  Suggestion: Create the file or specify a different path

Enter spec path: specs/001-feature/spec.md
✓ Valid path
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DOIT_NON_INTERACTIVE` | Disable all prompts | `false` |
| `DOIT_STATE_DIR` | Custom state directory | `.doit/state/` |

### Cleanup Old State

State files are automatically cleaned up after 7 days. To manually cleanup:

```bash
$ doit cleanup --state
Removed 3 stale workflow states
```

---

## Examples

### Example 1: Initialize New Project

```bash
$ doit init

Step 1 of 4: Select AI Tool
  ▶ claude
    cursor
    copilot
[Enter]

Step 2 of 4: Select Script Type
  ▶ bash
    powershell
[Enter]

Step 3 of 4: Project Name
Enter project name [my-project]: awesome-app
✓ Valid project name

Step 4 of 4: Confirm Settings
  AI Tool: claude
  Script Type: bash
  Project Name: awesome-app

Create project? [Y/n]: Y

✓ Project initialized successfully!
```

### Example 2: Resume Interrupted Workflow

```bash
$ doit specit
Step 3 of 6: Define User Stories
^C
Workflow interrupted. Progress saved.

# Later...
$ doit specit
Resume previous workflow? (Step 3 of 6) [Y/n]: Y

Step 3 of 6: Define User Stories
...
```

### Example 3: Non-Interactive for CI

```bash
# In GitHub Actions workflow
- name: Initialize doit
  run: |
    doit init --non-interactive \
      --ai-tool claude \
      --script-type bash \
      --project-name "${{ github.event.repository.name }}"
```

---

## Troubleshooting

### "Workflow state corrupted"

If you see this error, the state file was damaged. The workflow will start fresh:

```bash
$ doit init
Warning: State file corrupted. Starting fresh.
Step 1 of 4: Select AI Tool
```

### "Required input missing in non-interactive mode"

Non-interactive mode requires all inputs via command-line flags:

```bash
# This will fail if --ai-tool is required
$ doit init --non-interactive
Error: Required input 'ai-tool' not provided. Use --ai-tool flag.

# This works
$ doit init --non-interactive --ai-tool claude
```

### Terminal doesn't support arrow keys

Fallback to typing numbers:

```
Select AI Tool:
  1. claude
  2. cursor
  3. copilot

Enter number [1]: 1
```
