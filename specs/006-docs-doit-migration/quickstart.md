# Quickstart: Documentation Doit Migration

**Feature**: 006-docs-doit-migration
**Time Estimate**: File operations only

## Overview

This feature migrates documentation from legacy "specify/speckit" naming to standardized "doit" naming. No application code changes - only markdown and script comment updates.

## Prerequisites

- Unix-like environment with grep and sed
- Git repository checked out on branch `006-docs-doit-migration`

## Quick Reference

### Files to Update (Active)

```text
docs/
├── quickstart.md          # 27 speckit refs
├── upgrade.md             # 5 speckit refs
├── installation.md        # 3 speckit refs
└── features/
    └── 004-review-*.md    # 4 speckit refs

Root files:
├── spec-driven.md         # 6 speckit refs
├── CONTRIBUTING.md        # 1 speckit ref
└── AGENTS.md              # 1 speckit ref

scripts/bash/
└── check-prerequisites.sh # 3 speckit refs

templates/
└── checklist-template.md  # 2 speckit refs
```

### Files to Preserve (Historical)

- `CHANGELOG.md` - historical accuracy
- `specs/001-*/` through `specs/005-*/` - completed features

## Migration Steps

### Step 1: Validate Baseline

```bash
# Count current speckit references in active files
grep -r "speckit" docs/ scripts/ templates/ CONTRIBUTING.md AGENTS.md spec-driven.md \
  --include="*.md" --include="*.sh" | wc -l
```

### Step 2: Update Documentation Files

Update each file, replacing:
- "speckit" → "doit" (tool name)
- "Speckit" → "Doit" (capitalized)
- ".specify/" → ".doit/" (paths)

### Step 3: Update Scripts

Review and update comments in:
- `scripts/bash/check-prerequisites.sh`

### Step 4: Sync Templates

After updating `.doit/templates/`, sync to distribution:

```bash
cp -r .doit/templates/* templates/
```

### Step 5: Validate Migration

```bash
# Should return 0 for active files
grep -r "speckit" docs/ scripts/ templates/ CONTRIBUTING.md AGENTS.md spec-driven.md \
  --include="*.md" --include="*.sh" | wc -l

# Verify "specify" as verb preserved
grep -r "specify" docs/ --include="*.md" | head -5
# Should see uses like "you can specify" (preserved)
```

## Validation Checklist

- [ ] Zero "speckit" references in docs/
- [ ] Zero ".specify/" paths in active files
- [ ] "specify" as verb preserved
- [ ] CHANGELOG.md unchanged
- [ ] Historical specs unchanged
- [ ] templates/ synced from .doit/templates/

## Next Steps

After completing this migration:

1. Run `/doit.tasks` to generate task breakdown
2. Execute tasks in order
3. Run `/doit.review` for validation
4. Run `/doit.checkin` to finalize
