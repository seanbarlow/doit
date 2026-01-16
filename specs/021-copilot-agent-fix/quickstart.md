# Quickstart: GitHub Copilot Prompt File Fix

**Feature**: 021-copilot-agent-fix
**Estimated Time**: 10 minutes

## Prerequisites

- Access to DoIt repository
- Text editor or IDE
- Terminal for validation commands

## Overview

This guide walks through updating 20 prompt files to replace the deprecated `mode: agent` YAML attribute with `agent: true`.

## Step 1: Verify Current State

Before making changes, verify the current state:

```bash
# Count files with deprecated syntax
grep -r "mode: agent" templates/prompts/ src/doit_cli/templates/prompts/ | wc -l
# Expected: 20

# Verify reference file is correct
head -3 src/doit_cli/templates/prompts/doit-testit.prompt.md
# Expected:
# ---
# agent: true
# description: ...
```

## Step 2: Update Files in /templates/prompts/

Update each file by replacing line 2:

**Before:**
```yaml
---
mode: agent
description: [description]
---
```

**After:**
```yaml
---
agent: true
description: [description]
---
```

### Files to Update

1. `doit-checkin.prompt.md`
2. `doit-constitution.prompt.md`
3. `doit-documentit.prompt.md`
4. `doit-implementit.prompt.md`
5. `doit-planit.prompt.md`
6. `doit-reviewit.prompt.md`
7. `doit-roadmapit.prompt.md`
8. `doit-scaffoldit.prompt.md`
9. `doit-specit.prompt.md`
10. `doit-taskit.prompt.md`

**Skip**: `doit-testit.prompt.md` (already correct)

## Step 3: Update Files in /src/doit_cli/templates/prompts/

Repeat the same changes for the second directory. The file list is identical.

## Step 4: Validate Changes

After all updates, run validation:

```bash
# Verify no deprecated syntax remains
grep -r "mode: agent" templates/prompts/ src/doit_cli/templates/prompts/
# Expected: No output (0 results)

# Verify correct syntax is present
grep -r "agent: true" templates/prompts/ src/doit_cli/templates/prompts/ | wc -l
# Expected: 22 (11 files × 2 directories)
```

## Step 5: Test in VS Code

1. Open VS Code with the DoIt project
2. Ensure GitHub Copilot extension is installed
3. Open a file and test invoking a DoIt prompt
4. Verify no deprecation warnings appear

## Troubleshooting

### "No prompts found"

- Ensure VS Code is version 1.106 or later
- Verify prompt files have `.prompt.md` extension
- Check that YAML frontmatter is valid (no syntax errors)

### Deprecation warnings still appear

- Double-check all files were updated
- Verify the exact line: `agent: true` (not `agent:true` or `agent: "true"`)
- Restart VS Code to reload prompt files

### Changes not reflected

- VS Code may cache prompt files
- Try: View → Command Palette → "Developer: Reload Window"

## Summary

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Check current state | 20 files with `mode: agent` |
| 2 | Update /templates/prompts/ | 10 files changed |
| 3 | Update /src/doit_cli/templates/prompts/ | 10 files changed |
| 4 | Run grep validation | 0 deprecated, 22 correct |
| 5 | Test in VS Code | No warnings |

## Next Steps

After completing this quickstart:

1. Run `/doit.reviewit` to verify implementation
2. Run `/doit.checkin` to create PR and close issues
