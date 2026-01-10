# Quickstart: Review Template Commands

**Feature**: 004-review-template-commands
**Date**: 2026-01-10

## Pre-Implementation Baseline

```bash
# Count legacy templates (should be 9)
ls templates/commands/*.md | wc -l

# List legacy template names
ls templates/commands/

# Count speckit references in legacy templates (should be 8)
grep -l "speckit" templates/commands/*.md | wc -l

# Verify doit templates exist (should be 9)
ls .doit/templates/commands/doit.*.md | wc -l
```

## Implementation Steps

### Step 1: Remove Legacy Templates

```bash
# Remove all legacy speckit templates
rm templates/commands/analyze.md
rm templates/commands/checklist.md
rm templates/commands/clarify.md
rm templates/commands/constitution.md
rm templates/commands/implement.md
rm templates/commands/plan.md
rm templates/commands/specify.md
rm templates/commands/tasks.md
rm templates/commands/taskstoissues.md

# Or in one command:
rm templates/commands/{analyze,checklist,clarify,constitution,implement,plan,specify,tasks,taskstoissues}.md
```

### Step 2: Copy Doit Templates

```bash
# Copy all doit templates to templates/commands/
cp .doit/templates/commands/doit.*.md templates/commands/
```

## Post-Implementation Verification

```bash
# Verify no legacy templates remain
ls templates/commands/*.md | grep -v "doit\." && echo "ERROR: Legacy files remain" || echo "OK: No legacy files"

# Count doit templates (should be 9)
ls templates/commands/doit.*.md | wc -l

# Verify all 9 doit templates present
for cmd in checkin constitution implement plan review scaffold specify tasks test; do
  test -f "templates/commands/doit.${cmd}.md" && echo "OK: doit.${cmd}.md" || echo "MISSING: doit.${cmd}.md"
done

# Verify files match source (should show no differences)
diff -q .doit/templates/commands/ templates/commands/ 2>/dev/null || echo "Files match or only doit files present"

# Verify zero speckit references
grep -r "speckit" templates/commands/ && echo "ERROR: speckit references found" || echo "OK: No speckit references"

# Verify zero .specify/ references
grep -r "\.specify/" templates/commands/ && echo "ERROR: .specify references found" || echo "OK: No .specify references"
```

## Success Criteria Checklist

- [ ] Zero legacy speckit templates in `templates/commands/`
- [ ] 9 doit templates in `templates/commands/`
- [ ] All templates match `.doit/templates/commands/` source
- [ ] Zero "speckit" references in templates
- [ ] Zero ".specify/" references in templates

## Rollback (if needed)

```bash
# If rollback needed, restore from git
git checkout HEAD -- templates/commands/
```
