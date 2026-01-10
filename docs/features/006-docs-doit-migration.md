# Documentation Doit Migration

**Completed**: 2026-01-10
**Branch**: 006-docs-doit-migration
**PR**: -

## Overview

Comprehensive audit and update of all documentation, code comments, and examples throughout the repository to migrate from the legacy "speckit" naming convention to the standardized "doit" naming convention. This ensures consistency across all artifacts and prevents confusion for users learning the system.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Update all `.specify/` path references to `.doit/` in template command files | Done |
| FR-002 | Update all `.specify/` path references to `.doit/` in bash script files | Done |
| FR-003 | Synchronize updated templates to `templates/` distribution directory | Done |
| FR-004 | Replace all `/specify.*` command references with `/doit.*` equivalents | Done |
| FR-005 | Replace all `/speckit.*` command references with `/doit.*` equivalents | Done |
| FR-006 | Verify command reference mapping is accurate | Done |
| FR-007 | Update README.md to use consistent doit terminology | N/A (no changes needed) |
| FR-008 | Update docs/ folder files to use doit terminology | Done |
| FR-009 | Update quickstart guides in specs/ to reference doit commands | Done |
| FR-010 | Preserve the word "specify" when used as a verb | Done |
| FR-011 | Update bash script comments to reference doit paths and commands | Done |
| FR-012 | Update Python docstrings and comments to reference doit terminology | N/A (no Python changes needed) |
| FR-013 | Provide grep-based validation that zero `.specify/` path references remain | Done |
| FR-014 | Provide grep-based validation that zero `/specify.` command references remain | Done |
| FR-015 | Provide grep-based validation that zero `/speckit.` command references remain | Done |
| FR-016 | DO NOT modify CHANGELOG.md historical entries | Done |
| FR-017 | DO NOT modify completed feature spec.md content | Done |

## Technical Details

### Files Modified

- `docs/quickstart.md` - Updated "Spec Kit" to "Doit", all `/speckit.*` commands to `/doit.*`
- `docs/upgrade.md` - Updated branding and command references
- `docs/installation.md` - Updated command references
- `docs/features/004-review-template-commands.md` - Updated terminology
- `spec-driven.md` - Updated all command examples to use `/doit.*` format
- `CONTRIBUTING.md` - Updated branding from "Spec Kit" to "Doit"
- `AGENTS.md` - Updated branding and GitHub Copilot mode format
- `scripts/bash/check-prerequisites.sh` - Updated error messages to reference `/doit.*` commands
- `templates/checklist-template.md` - Updated `/speckit.checklist` to `/doit.checklist`

### Preservation Rules Applied

- CHANGELOG.md - Historical entries preserved unchanged
- specs/001-005 directories - 106 historical "speckit" references preserved
- "specify" as English verb - Preserved throughout documentation
- "Specify CLI" tool references - Preserved (this is the actual CLI tool name)

## Testing

### Code Review

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 2 (acceptable) |
| Info | 1 |

### Manual Tests

| Test ID | Description | Result |
|---------|-------------|--------|
| MT-001 | US1 - Template Path Correction | PASS |
| MT-002 | US2 - Command Reference Updates | PASS |
| MT-003 | US3 - Documentation Content (zero speckit) | PASS |
| MT-004 | US4 - Code Comments | PASS |
| MT-005 | Preserve "specify" (CLI tool refs) | PASS |
| MT-006 | CHANGELOG.md unchanged | PASS |
| MT-007 | Historical specs preserved | PASS |

### Success Criteria

| ID | Criterion | Status |
|----|-----------|--------|
| SC-001 | Zero files contain `.specify/` path references (excluding historical) | PASS |
| SC-002 | Zero files contain `/specify.` command references | PASS |
| SC-003 | Zero files contain `/speckit.` command references | PASS |
| SC-004 | All 9 doit commands correctly referenced in documentation | PASS |
| SC-005 | Template distribution copies in `templates/` match source | PASS |
| SC-006 | All bash scripts execute without path-related errors | PASS |

## Related Issues

N/A - No GitHub issues created for this feature
