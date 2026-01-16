# Quickstart: Roadmap Template Cleanup

**Feature Branch**: `017-roadmap-template-cleanup`
**Date**: 2026-01-13

## Prerequisites

- Git repository checked out on branch `017-roadmap-template-cleanup`
- Access to file system

## Implementation Steps

### Step 1: Update roadmap.md Template

Replace the content of `templates/memory/roadmap.md` with the content from `.doit/templates/roadmap-template.md`.

**Source**: `.doit/templates/roadmap-template.md`
**Target**: `templates/memory/roadmap.md`

### Step 2: Update roadmap_completed.md Template

Replace the content of `templates/memory/roadmap_completed.md` with the content from `.doit/templates/completed-roadmap-template.md`.

**Source**: `.doit/templates/completed-roadmap-template.md`
**Target**: `templates/memory/roadmap_completed.md`

### Step 3: Verify Changes

1. Run diff to confirm templates match:
   ```bash
   diff .doit/templates/roadmap-template.md templates/memory/roadmap.md
   diff .doit/templates/completed-roadmap-template.md templates/memory/roadmap_completed.md
   ```

2. Verify no sample-specific content remains:
   ```bash
   grep -r "Task Management App" templates/memory/
   grep -r "Update Doit Templates" templates/memory/
   ```

### Step 4: Test with doit init (Optional)

1. Create a temporary test directory:
   ```bash
   mkdir /tmp/test-doit-init && cd /tmp/test-doit-init
   ```

2. Run doit init (requires package reinstall first):
   ```bash
   pip install -e /path/to/doit
   doit init
   ```

3. Verify roadmap files contain placeholders:
   ```bash
   head -10 .doit/memory/roadmap.md
   head -10 .doit/memory/roadmap_completed.md
   ```

## Verification Checklist

- [ ] `templates/memory/roadmap.md` contains `[PROJECT_NAME]` placeholder
- [ ] `templates/memory/roadmap.md` contains `[PROJECT_VISION]` placeholder
- [ ] `templates/memory/roadmap_completed.md` contains `[PROJECT_NAME]` placeholder
- [ ] `templates/memory/roadmap_completed.md` contains `[COUNT]` placeholder
- [ ] No references to "Task Management App" in memory templates
- [ ] No actual completed feature entries in memory templates

## Files Changed

| File | Action |
|------|--------|
| `templates/memory/roadmap.md` | Content replaced with placeholder template |
| `templates/memory/roadmap_completed.md` | Content replaced with placeholder template |
