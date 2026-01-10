# Research: Documentation Doit Migration

**Feature**: 006-docs-doit-migration
**Date**: 2026-01-10
**Status**: Complete

## Executive Summary

Audit of the repository identified **31 files** with `.specify/` path references and **27 files** with "speckit" terminology references. Most references are in historical spec documents from completed features, with some in active documentation and scripts that require updating.

## Scope Analysis

### Category 1: .specify/ Path References (31 files)

Files containing legacy `.specify/` path references:

| Location | Files | Priority | Action |
| -------- | ----- | -------- | ------ |
| specs/001-doit-command-refactor/ | 7 | Low | Historical - preserve |
| specs/002-update-doit-templates/ | 5 | Low | Historical - preserve |
| specs/003-scaffold-doit-commands/ | 7 | Low | Historical - preserve |
| specs/004-review-template-commands/ | 6 | Low | Historical - preserve |
| specs/006-docs-doit-migration/ | 2 | N/A | Current feature |
| docs/features/ | 3 | Medium | Update to doit terminology |
| docs/templates/ | 1 | High | Active documentation |

**Decision**: Historical spec files (001-004) should be preserved as-is for accuracy. Active docs/ files should be updated.

### Category 2: speckit References (27 files, 196 occurrences)

Files containing "speckit" terminology:

| Location | Files | Occurrences | Priority |
| -------- | ----- | ----------- | -------- |
| specs/001-*/ | 7 | 105 | Low - Historical |
| specs/003-*/ | 1 | 1 | Low - Historical |
| specs/004-*/ | 7 | 41 | Low - Historical |
| docs/ | 4 | 35 | High - Active docs |
| Root files | 4 | 11 | High - Active |
| scripts/ | 1 | 3 | High - Active |
| templates/ | 1 | 2 | High - Active |

**Files requiring updates** (non-historical):

1. `docs/quickstart.md` - 27 occurrences
2. `docs/upgrade.md` - 5 occurrences
3. `docs/installation.md` - 3 occurrences
4. `docs/features/004-review-template-commands.md` - 4 occurrences
5. `spec-driven.md` - 6 occurrences
6. `CONTRIBUTING.md` - 1 occurrence
7. `AGENTS.md` - 1 occurrence
8. `scripts/bash/check-prerequisites.sh` - 3 occurrences
9. `templates/checklist-template.md` - 2 occurrences

### Category 3: /specify. Command References (10 files)

Files with legacy `/specify.` command patterns:

- Most in historical specs (001, 003, 004)
- `docs/features/004-review-template-commands.md` - needs update

## Preservation Rules

### DO Update

- `docs/` folder (except features/ for completed features)
- Root markdown files (`CONTRIBUTING.md`, `AGENTS.md`, `spec-driven.md`)
- `scripts/bash/` files
- `templates/` distribution files

### DO NOT Update

- `CHANGELOG.md` - preserve historical accuracy
- `specs/001-*/` through `specs/005-*/` - completed feature history
- Any file where "specify" is used as a verb (e.g., "you can specify")

## Command Mapping

| Legacy Command | Doit Equivalent |
| -------------- | --------------- |
| /specify.plan | /doit.plan |
| /specify.tasks | /doit.tasks |
| /specify.implement | /doit.implement |
| /specify.review | /doit.review |
| /speckit (tool name) | doit |

## Validation Strategy

### Pre-Migration Baseline

```bash
# Count .specify/ references (excluding historical)
grep -r "\.specify/" docs/ scripts/ templates/ CONTRIBUTING.md AGENTS.md --include="*.md" --include="*.sh" | wc -l

# Count speckit references (excluding historical)
grep -r "speckit" docs/ scripts/ templates/ CONTRIBUTING.md AGENTS.md spec-driven.md --include="*.md" --include="*.sh" | wc -l
```

### Post-Migration Validation

```bash
# Should return 0
grep -r "\.specify/" docs/ scripts/ templates/ CONTRIBUTING.md AGENTS.md --include="*.md" --include="*.sh" | wc -l

# Should return 0 (excluding CHANGELOG.md)
grep -r "speckit" docs/ scripts/ templates/ CONTRIBUTING.md AGENTS.md spec-driven.md --include="*.md" --include="*.sh" | wc -l
```

## Risks and Mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Breaking "specify" as verb | Manual review of each replacement |
| CHANGELOG accuracy loss | Exclude from updates |
| Missing files | Comprehensive grep audit first |
| Sync issues | Update .doit/ sources first, then copy to templates/ |

## Recommendations

1. **Phase approach**: Update active docs first, then scripts, then templates
2. **Manual review**: Each file should be reviewed after automated replacement
3. **Validation gates**: Run grep validation after each phase
4. **Sync last**: Ensure .doit/templates/ → templates/ sync happens after all updates
