# Quickstart: Update Doit Templates

**Branch**: `002-update-doit-templates` | **Date**: 2026-01-09

## Prerequisites

- Git repository cloned
- Access to edit markdown files

## Verification Steps

### Before Implementation

Run these commands to see current invalid references:

```bash
# Check for /doit.checklist references (should find matches)
grep -r "/doit.checklist" .specify/templates/

# Check for /doit.clarify references (should find matches)
grep -r "/doit.clarify" .claude/commands/

# Check for invalid path reference
grep -r "templates/commands/plan.md" .specify/templates/
```

### After Implementation

Run these commands to verify fixes:

```bash
# Should return NO matches
grep -r "/doit.checklist" .specify/templates/
grep -r "/doit.clarify" .claude/commands/
grep -r "templates/commands/plan.md" .specify/templates/

# Should return matches (valid references)
grep -r "/doit.plan" .specify/templates/
grep -r "/doit.tasks" .specify/templates/
```

## Files Changed

1. `.specify/templates/checklist-template.md` - Updated command reference
2. `.specify/templates/plan-template.md` - Fixed path reference
3. `.claude/commands/doit.specify.md` - Removed invalid command reference

## Success Criteria

All grep commands for invalid references return empty results.
