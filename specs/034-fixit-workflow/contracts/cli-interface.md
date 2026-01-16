# CLI Interface Contract: doit fixit

**Date**: 2026-01-16
**Feature**: 034-fixit-workflow

## Command Overview

```bash
doit fixit [ISSUE_ID] [OPTIONS]
```

The `fixit` command provides a structured workflow for fixing bugs from GitHub issues.

---

## Commands

### Main Command: `doit fixit`

Start or resume a bug fix workflow.

#### Usage

```bash
# Start fix for specific issue
doit fixit 123

# Browse and select from open bugs
doit fixit

# Resume interrupted workflow
doit fixit --resume
doit fixit --resume 123
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `ISSUE_ID` | int | No | GitHub issue number to fix |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--resume` | `-r` | flag | false | Resume interrupted workflow |
| `--manual` | `-m` | flag | false | Skip GitHub fetch, enter details manually |
| `--branch` | `-b` | str | auto | Custom branch name (overrides default) |

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Issue not found |
| 2 | Workflow error (state corruption, etc.) |
| 3 | GitHub API unavailable (offline) |
| 4 | User cancelled |

---

### Subcommand: `doit fixit list`

List open bug issues without starting a workflow.

#### Usage

```bash
# List all open bugs
doit fixit list

# Filter by label
doit fixit list --label priority:high

# JSON output for scripting
doit fixit list --format json
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--label` | `-l` | str | "bug" | Filter by label (can repeat) |
| `--format` | `-f` | enum | table | Output format: table, json, markdown |
| `--limit` | `-n` | int | 20 | Maximum issues to display |

#### Output Formats

**Table (default)**:
```
Bug Issues (showing 3 of 15)
┌────────┬────────────────────────────────┬───────────────────┬────────────┐
│ ID     │ Title                          │ Labels            │ Created    │
├────────┼────────────────────────────────┼───────────────────┼────────────┤
│ #123   │ Button click causes error      │ bug, priority:hi  │ 2 days ago │
│ #119   │ Login fails on mobile          │ bug, mobile       │ 5 days ago │
│ #115   │ Data not saving                │ bug               │ 1 week ago │
└────────┴────────────────────────────────┴───────────────────┴────────────┘
```

**JSON**:
```json
{
  "total": 15,
  "issues": [
    {"number": 123, "title": "Button click causes error", "labels": ["bug", "priority:high"], "created_at": "2026-01-14T..."}
  ]
}
```

---

### Subcommand: `doit fixit status`

Show status of current or specific fix workflow.

#### Usage

```bash
# Show current workflow (if on fix branch)
doit fixit status

# Show specific workflow
doit fixit status 123
```

#### Output

```
Fix Workflow: #123 - Button click causes error
Branch: fix/123-button-click-error
Phase: investigating (2 of 5)

Progress:
● Initialized     ✓ Complete
● Investigating   ◐ In Progress (3/5 checkpoints)
○ Planning        ○ Not started
○ Reviewing       ○ Not started
○ Implementing    ○ Not started

Investigation Findings: 2
  - Hypothesis: Event handler not bound correctly
  - Affected File: src/components/Button.tsx

Next Step: Complete investigation checkpoints, then run 'doit fixit plan'
```

---

### Subcommand: `doit fixit investigate`

Begin or continue the investigation phase.

#### Usage

```bash
# Start investigation (creates investigation-plan.md)
doit fixit investigate

# Add a finding
doit fixit investigate --add-finding "hypothesis" "Event handler missing"

# Mark checkpoint complete
doit fixit investigate --checkpoint 1 --done
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--add-finding` | str str | Add finding (type, description) |
| `--checkpoint` | int | Checkpoint number to update |
| `--done` | flag | Mark checkpoint as complete |

---

### Subcommand: `doit fixit plan`

Generate fix plan after investigation.

#### Usage

```bash
# Generate fix-plan.md from investigation findings
doit fixit plan

# Open generated plan for editing
doit fixit plan --edit
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--edit` | flag | Open plan in editor after generation |
| `--output` | str | Custom output path (default: fix-plan.md) |

---

### Subcommand: `doit fixit cancel`

Cancel and clean up a fix workflow.

#### Usage

```bash
# Cancel current workflow
doit fixit cancel

# Cancel specific workflow
doit fixit cancel 123

# Cancel and delete branch
doit fixit cancel --delete-branch
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--delete-branch` | flag | Also delete the fix branch |
| `--force` | flag | Skip confirmation prompt |

---

## Interactive Prompts

### Issue Selection (when no ISSUE_ID provided)

```
? Select a bug to fix:
  ❯ #123 - Button click causes error (priority:high, 2 days ago)
    #119 - Login fails on mobile (mobile, 5 days ago)
    #115 - Data not saving (1 week ago)
    [Enter issue number manually]
    [Cancel]
```

### Workflow Phase Transitions

```
Investigation phase complete.

Findings:
  ✓ Root cause confirmed: Event handler not bound
  ✓ Affected files: src/components/Button.tsx
  ✓ Reproduction steps documented

? Ready to create fix plan?
  ❯ Yes, generate fix-plan.md
    No, continue investigating
    Cancel workflow
```

### Branch Conflict

```
⚠ A fix branch already exists for issue #123:
  fix/123-button-click-error (remote: origin)

? How would you like to proceed?
  ❯ Continue with existing branch
    Create new branch: fix/123-button-click-error-2
    Cancel
```

---

## Error Messages

| Scenario | Message |
|----------|---------|
| Issue not found | `Error: Issue #123 not found. Check the issue number and try again.` |
| GitHub offline | `Warning: GitHub API unavailable. Use --manual to enter issue details.` |
| No open bugs | `No open bugs found. Check issue labels or create a new issue.` |
| Already closed | `Warning: Issue #123 is already closed. Continue anyway? [y/N]` |
| State corrupted | `Error: Workflow state corrupted. Run 'doit fixit cancel 123' to reset.` |
| Not on fix branch | `Error: Not on a fix branch. Run 'doit fixit' to start a workflow.` |

---

## Integration with Other Commands

### With `/doit.reviewit`

After fix plan is generated:
```bash
# Fixit sets up reviewit with fix-plan.md as artifact
doit fixit plan
# Then user runs:
doit reviewit
# Which reviews fix-plan.md
```

### With `/doit.taskit`

After fix plan is approved:
```bash
# Generate tasks from approved fix plan
doit taskit
# Reads fix-plan.md and generates tasks.md
```

### With `/doit.checkin`

On checkin completion:
```bash
# Checkin detects fix branch and closes issue
doit checkin
# If branch is fix/123-*, automatically closes #123 on merge
```

---

## Configuration

Configuration in `.doit/config/fixit.yaml` (optional):

```yaml
# Default labels for bug filtering
bug_labels:
  - bug
  - defect

# Branch naming pattern
branch_pattern: "fix/{issue_id}-{slug}"

# Auto-close issues on checkin
auto_close_issues: true

# Investigation checkpoints template
investigation_checkpoints:
  - "Reproduce the bug"
  - "Identify related code"
  - "Analyze root cause"
  - "Document findings"
```
