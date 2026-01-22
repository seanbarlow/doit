# Quickstart: GitHub Milestone Generation

**Feature**: 041-milestone-generation
**Command**: `doit roadmapit sync-milestones`

## What This Feature Does

Automatically creates GitHub milestones for your roadmap priorities (P1, P2, P3, P4) and assigns epics to the appropriate milestones. This provides a GitHub-native view of your roadmap without manual milestone management.

**Before Sync**:
- Roadmap items scattered across GitHub without milestone organization
- Manual milestone creation and epic assignment
- No visual priority grouping in GitHub UI

**After Sync**:
- 4 priority milestones created: "P1 - Critical", "P2 - High Priority", etc.
- All epics automatically assigned to their priority milestone
- Team can view priorities directly in GitHub milestone view

## Prerequisites

Before using this feature:

1. **GitHub CLI installed and authenticated**:
   ```bash
   # Check if gh CLI is installed
   gh --version

   # If not installed, visit: https://cli.github.com

   # Authenticate if needed
   gh auth status
   gh auth login  # If not authenticated
   ```

2. **Repository must be GitHub-based**:
   ```bash
   # Verify remote is GitHub
   git remote -v
   # Should show: github.com/owner/repo
   ```

3. **Roadmap must exist with GitHub epic references**:
   ```bash
   # Verify roadmap exists
   cat .doit/memory/roadmap.md
   ```

4. **User must have write access to repository**:
   ```bash
   # Test by creating a test issue
   gh issue list
   ```

## Quick Start

### 1. Preview Changes (Dry Run)

See what would be created without making changes:

```bash
doit roadmapit sync-milestones --dry-run
```

**Example Output**:
```
🔍 Dry Run - No changes will be made

Milestones to Create:
  ✓ P3 - Medium Priority (currently missing)
  ✓ P4 - Low Priority (currently missing)

Epic Assignments to Update:
  #587 → P2 - High Priority (currently: unassigned)
  #590 → P2 - High Priority (currently: Sprint 5)
  #594 → P3 - Medium Priority (currently: unassigned)

Milestones Already Exist:
  • P1 - Critical (3 epics assigned)
  • P2 - High Priority (2 epics assigned)

Run without --dry-run to apply these changes.
```

### 2. Execute Sync

Apply the changes:

```bash
doit roadmapit sync-milestones
```

**Example Output**:
```
🚀 Syncing roadmap priorities to GitHub milestones...

✓ Created milestone: P3 - Medium Priority (#7)
✓ Created milestone: P4 - Low Priority (#8)
✓ Assigned epic #594 to P3 - Medium Priority
⚠️  Epic #590 reassigned from "Sprint 5" to "P2 - High Priority" (roadmap priority)
✓ Assigned epic #587 to P2 - High Priority

Summary:
  • Milestones created: 2
  • Epics assigned: 3
  • Errors: 0

View milestones: https://github.com/owner/repo/milestones
```

### 3. Verify in GitHub

Open your repository's milestones page:

```bash
# Open in browser
gh browse --repo owner/repo --milestones

# Or list via CLI
gh api repos/owner/repo/milestones --jq '.[] | {title, open_issues}'
```

**Expected Result**:
```json
[
  {
    "title": "P1 - Critical",
    "open_issues": 3
  },
  {
    "title": "P2 - High Priority",
    "open_issues": 3
  },
  {
    "title": "P3 - Medium Priority",
    "open_issues": 1
  },
  {
    "title": "P4 - Low Priority",
    "open_issues": 0
  }
]
```

## Common Workflows

### Workflow 1: Initial Setup (No Milestones Exist)

```bash
# 1. Verify roadmap has GitHub epic references
grep "GitHub: #" .doit/memory/roadmap.md

# 2. Preview what will be created
doit roadmapit sync-milestones --dry-run

# 3. Create milestones and assign epics
doit roadmapit sync-milestones

# 4. View results in browser
gh browse --milestones
```

### Workflow 2: Reprioritize Roadmap Item

When you move an item from P3 to P1:

```bash
# 1. Edit roadmap.md - move item to P1 section
vim .doit/memory/roadmap.md

# 2. Sync to update epic's milestone
doit roadmapit sync-milestones

# Output:
# ⚠️  Epic #594 reassigned from "P3 - Medium Priority" to "P1 - Critical" (roadmap priority)
```

### Workflow 3: Complete All P1 Items

When all P1 items are done:

```bash
# 1. Mark items complete or run /doit.checkin
# (items moved to completed_roadmap.md)

# 2. Sync to detect completion
doit roadmapit sync-milestones

# Output:
# ℹ️  All P1 - Critical items completed. Close milestone? [y/N]

# 3. Type 'y' to close milestone
```

### Workflow 4: Add New Roadmap Item with Epic

```bash
# 1. Create GitHub epic
gh issue create --title "New Feature" --label epic,priority:P2

# 2. Add to roadmap.md under P2 section
echo "- [ ] New Feature" >> .doit/memory/roadmap.md
echo "  - **Rationale**: Description" >> .doit/memory/roadmap.md
echo "  - **GitHub**: #595" >> .doit/memory/roadmap.md

# 3. Sync to assign epic to P2 milestone
doit roadmapit sync-milestones

# Output:
# ✓ Assigned epic #595 to P2 - High Priority
```

## Understanding Sync Behavior

### What Gets Synced?

**Created**:
- Missing priority milestones (P1-P4)
- Milestone descriptions include "Auto-managed by doit"

**Updated**:
- Epic milestone assignments (if priority changed)
- Previous assignments are overwritten

**Preserved**:
- Existing milestones with matching titles
- Manual milestone descriptions (won't overwrite)
- Closed milestones (won't reopen)

**Skipped**:
- Roadmap items without GitHub epic references
- Epics already assigned to correct milestone
- Items marked completed

### Milestone Naming Convention

Milestones are created with exact titles:

| Priority | Milestone Title | Description |
|----------|-----------------|-------------|
| P1 | P1 - Critical | Auto-managed by doit. Contains all P1 - Critical roadmap items. |
| P2 | P2 - High Priority | Auto-managed by doit. Contains all P2 - High Priority roadmap items. |
| P3 | P3 - Medium Priority | Auto-managed by doit. Contains all P3 - Medium Priority roadmap items. |
| P4 | P4 - Low Priority | Auto-managed by doit. Contains all P4 - Low Priority roadmap items. |

**Important**: Don't rename these milestones. Sync detects them by exact title match.

## Troubleshooting

### Error: "gh CLI not found"

```bash
# Install GitHub CLI
# macOS:
brew install gh

# Linux:
sudo apt install gh

# Windows:
winget install GitHub.cli

# Then authenticate
gh auth login
```

### Error: "Not a GitHub repository"

```bash
# Check remote URL
git remote -v

# If not GitHub, this feature won't work
# doit milestone sync only supports GitHub
```

### Error: "Permission denied"

```bash
# Verify you have write access
gh repo view owner/repo --json viewerPermission

# Should show: "viewerPermission": "WRITE" or "ADMIN"
# If not, request access from repository owner
```

### Warning: "Epic #123 not found"

```bash
# Epic referenced in roadmap but doesn't exist in GitHub
# Options:
# 1. Create the epic:
gh issue create --title "Epic Title" --label epic

# 2. Remove reference from roadmap:
vim .doit/memory/roadmap.md
# Delete or comment out the "GitHub: #123" line
```

### Warning: "Milestone title conflict"

```bash
# You manually created "P1 - Critical" before running sync
# Sync will use existing milestone, not create duplicate

# To verify:
gh api repos/owner/repo/milestones --jq '.[] | select(.title == "P1 - Critical")'
```

## Advanced Usage

### Sync on CI/CD

Add to `.github/workflows/roadmap-sync.yml`:

```yaml
name: Sync Roadmap Milestones

on:
  push:
    paths:
      - '.doit/memory/roadmap.md'
    branches:
      - main

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup doit CLI
        run: pip install doit-toolkit-cli

      - name: Sync milestones
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          doit roadmapit sync-milestones
```

### Sync Only Specific Priority

Currently not supported - sync operates on all priorities (P1-P4).

**Workaround**: Temporarily comment out priorities you don't want synced:

```markdown
<!-- ### P4 - Low Priority -->
```

### Manual Milestone Management

To prevent sync from managing certain milestones:

1. **Don't** use exact titles (e.g., "P1 - Critical")
2. **Use** custom titles (e.g., "Sprint 5", "Q1 2026")
3. Sync will only create/update priority milestones with standard titles

## Best Practices

### ✅ Do

- Run `--dry-run` before first sync to preview changes
- Keep epic references in roadmap up-to-date
- Use priority labels on epics (`priority:P1`, `priority:P2`)
- Run sync after reprioritizing roadmap items
- Close milestones when all items complete

### ❌ Don't

- Rename auto-generated milestones (breaks detection)
- Manually assign epics to different milestones (sync will overwrite)
- Delete priority milestones (they'll be recreated)
- Mix manual and auto milestone management (choose one approach)

## Next Steps

After syncing milestones:

1. **View in GitHub**: Browse to repo milestones page to see priority organization
2. **Plan work**: Use milestone filters to focus on P1/P2 items
3. **Track progress**: Monitor milestone completion percentages
4. **Reprioritize**: Update roadmap.md and re-sync as priorities change

## Related Documentation

- [Feature Specification](spec.md) - Detailed requirements and user stories
- [Implementation Plan](plan.md) - Technical design and architecture
- [Data Model](data-model.md) - Entity definitions and relationships
- [GitHub API Contract](contracts/github-api.md) - API endpoints and responses

## Feedback

Found a bug or have a feature request?

```bash
# Report via GitHub issue
gh issue create --title "Milestone Sync: [issue description]" --label bug
```
