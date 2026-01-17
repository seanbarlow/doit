# Research: Roadmap Template Cleanup

**Feature Branch**: `017-roadmap-template-cleanup`
**Date**: 2026-01-13

## Summary

This feature requires no external research. The implementation is straightforward: copy the content from existing reference templates to the memory templates.

## Findings

### Source Templates (Reference - Correct Format)

The following files already contain the correct placeholder format:

1. **`.doit/templates/roadmap-template.md`**
   - Contains placeholders: `[PROJECT_NAME]`, `[PROJECT_VISION]`, `[P1_ITEM_1]`, etc.
   - Preserves all HTML comments for guidance
   - 62 lines total

2. **`.doit/templates/completed-roadmap-template.md`**
   - Contains placeholders: `[PROJECT_NAME]`, `[COMPLETED_ITEM]`, `[COUNT]`, etc.
   - Includes Archive section with collapsible details
   - 51 lines total

### Target Templates (Need Update)

The following files currently contain actual project data instead of placeholders:

1. **`templates/memory/roadmap.md`**
   - Currently contains: "Task Management App" example with actual task items
   - Should match: `.doit/templates/roadmap-template.md`

2. **`templates/memory/roadmap_completed.md`**
   - Currently contains: Actual doit project completed features
   - Should match: `.doit/templates/completed-roadmap-template.md`

## Decision

**Approach**: Direct file content replacement

- Copy content from `.doit/templates/roadmap-template.md` → `templates/memory/roadmap.md`
- Copy content from `.doit/templates/completed-roadmap-template.md` → `templates/memory/roadmap_completed.md`

**Rationale**: The reference templates already exist and represent the canonical format. No design decisions needed.

**Alternatives Considered**: None - the solution is self-evident given the existing reference templates.

## Technical Notes

- The `src/doit_cli/templates` directory is a symlink to `../../templates`
- Package rebuild/reinstall will propagate changes to `.venv/lib/python3.11/site-packages/doit_cli/templates/`
- No code changes required - purely file content updates
