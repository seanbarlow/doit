# Quickstart: AI Context Optimization

**Feature**: 051-ai-context-optimization
**Date**: 2025-01-28

## Overview

This guide covers how to implement the AI Context Optimization feature, which eliminates double-injection patterns and adds standardized instruction blocks to all doit command templates.

## Prerequisites

- Python 3.11+
- Existing doit installation
- Access to `templates/commands/` directory

## Quick Implementation Guide

### Step 1: Update .gitignore

Add the temp folder exclusion:

```bash
echo ".doit/temp/" >> .gitignore
```

### Step 2: Create Temp Directory

```bash
mkdir -p .doit/temp
touch .doit/temp/.gitkeep
```

### Step 3: Identify Double-Injection Templates

Run the context audit (once implemented):

```bash
doit context audit
```

Or manually check these 6 templates:
1. `templates/commands/doit.checkin.md`
2. `templates/commands/doit.constitution.md`
3. `templates/commands/doit.planit.md`
4. `templates/commands/doit.roadmapit.md`
5. `templates/commands/doit.scaffoldit.md`
6. `templates/commands/doit.taskit.md`

### Step 4: Apply Template Modifications

For each affected template, replace explicit file read instructions with the standardized pattern:

**BEFORE** (double-injection):
```markdown
## Load Project Context

```bash
doit context show
```

...later in template...

**For this command specifically**:
- Read `.doit/memory/tech-stack.md` for technology decisions
- Read `.doit/memory/constitution.md` for principles
```

**AFTER** (single source):
```markdown
## Load Project Context

```bash
doit context show
```

**Use loaded context to**:
- Reference constitution principles when making decisions
- Consider roadmap priorities
- Use tech stack decisions from context

**Context already loaded - DO NOT read these files again**:
- `.doit/memory/constitution.md`
- `.doit/memory/tech-stack.md`
- `.doit/memory/roadmap.md`
- `.doit/memory/completed_roadmap.md`
```

### Step 5: Add Best Practices Block

Add this standardized block to ALL 12 templates after the context loading section:

```markdown
## Code Quality Guidelines

Before generating or modifying code:

1. **Search for existing implementations** - Use Glob/Grep to find similar functionality
2. **Follow established patterns** - Match existing code style and architecture
3. **Avoid duplication** - Reference or extend existing utilities rather than recreating
4. **Check imports** - Verify required dependencies already exist in the project
```

### Step 6: Add Artifact Storage Instructions

Add this block to ALL 12 templates:

```markdown
## Artifact Storage

- **Temporary scripts**: Save to `.doit/temp/{purpose}-{timestamp}.sh`
- **Status reports**: Save to `specs/{feature}/reports/{command}-report-{timestamp}.md`
- **Create directories if needed**: Use `mkdir -p` before writing files
```

## Verification

### Test Double-Injection Removal

1. Run any doit command
2. Check AI context window - each source should appear exactly once
3. Estimated token reduction: ~40%

### Test Temp Script Storage

1. Have AI generate a diagnostic script
2. Verify it appears in `.doit/temp/`
3. Verify `.doit/temp/` is not tracked by git:
   ```bash
   git status .doit/temp/
   # Should show nothing (ignored)
   ```

### Test Status Report Storage

1. Run a workflow command that generates output
2. Check `specs/{feature}/reports/` for the report file
3. Verify naming follows `{command}-report-{timestamp}.md`

## Common Issues

### Issue: AI Still Reading Files Directly

**Cause**: Template still has explicit read instructions
**Fix**: Search template for patterns like "Read `.doit/memory/" and remove

### Issue: Temp Files Being Committed

**Cause**: `.gitignore` not updated
**Fix**: Add `.doit/temp/` to `.gitignore`

### Issue: Reports Not in Spec Folder

**Cause**: Template missing artifact storage instructions
**Fix**: Add the Artifact Storage section to the template

## Next Steps

After implementing:
1. Run `doit context audit` to verify no double-injection remains
2. Test each command template manually
3. Review token usage metrics
