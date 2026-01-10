# Quickstart: Scaffold Doit Commands

**Feature**: 003-scaffold-doit-commands
**Date**: 2026-01-09

## Verification Commands

### Pre-Implementation Baseline

```bash
# Count .specify references (should be ~50)
grep -r "\.specify" --include="*.md" --include="*.sh" --include="*.ps1" --include="*.py" --include="*.json" . 2>/dev/null | wc -l

# List current templates
ls -la .specify/templates/

# List current commands
ls -la .claude/commands/

# Verify .specify folder exists
test -d .specify && echo "EXISTS: .specify" || echo "MISSING: .specify"
```

### Post-Implementation Verification

```bash
# Verify .doit folder exists
test -d .doit && echo "EXISTS: .doit" || echo "MISSING: .doit"

# Verify .specify folder is gone
test -d .specify && echo "ERROR: .specify still exists" || echo "OK: .specify removed"

# Count remaining .specify references (should be 0 in active files)
grep -r "\.specify" --include="*.md" --include="*.sh" --include="*.ps1" .claude/ .doit/ 2>/dev/null | wc -l

# Verify command templates exist
ls -la .doit/templates/commands/

# Count command templates (should be 9)
ls .doit/templates/commands/*.md 2>/dev/null | wc -l

# Verify unused templates removed
test -f .doit/templates/agent-file-template.md && echo "ERROR: agent-file-template.md exists" || echo "OK: removed"
test -f .doit/templates/checklist-template.md && echo "ERROR: checklist-template.md exists" || echo "OK: removed"

# Verify active templates kept
test -f .doit/templates/spec-template.md && echo "OK: spec-template.md" || echo "ERROR: missing"
test -f .doit/templates/plan-template.md && echo "OK: plan-template.md" || echo "ERROR: missing"
test -f .doit/templates/tasks-template.md && echo "OK: tasks-template.md" || echo "ERROR: missing"

# Verify bash scripts moved
ls -la .doit/scripts/bash/
```

### Scaffold Command Test

```bash
# Create test directory
mkdir -p /tmp/test-scaffold-project
cd /tmp/test-scaffold-project

# After scaffold, verify commands exist
ls -la .claude/commands/doit.*.md

# Count generated commands (should be 9)
ls .claude/commands/doit.*.md | wc -l

# Clean up
rm -rf /tmp/test-scaffold-project
```

## Implementation Order

1. **Rename folder**: `.specify/` → `.doit/`
2. **Update references**: All files referencing `.specify`
3. **Remove unused templates**: `agent-file-template.md`, `checklist-template.md`
4. **Create command templates**: Copy from `.claude/commands/` to `.doit/templates/commands/`
5. **Update scaffold command**: Add command copying logic
6. **Run verification**: All checks should pass

## Success Criteria Checklist

- [ ] `.doit/` folder exists with correct structure
- [ ] `.specify/` folder no longer exists
- [ ] Zero `.specify` references in active command files
- [ ] 9 command templates in `.doit/templates/commands/`
- [ ] 3 active templates (spec, plan, tasks)
- [ ] 2 unused templates removed
- [ ] Scaffold command generates all doit commands
