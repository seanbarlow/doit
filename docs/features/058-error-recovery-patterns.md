# Error Recovery Patterns in All Commands

**Completed**: 2026-03-26
**Branch**: `058-error-recovery-patterns`
**Epic**: #767

## Overview

Added structured `## Error Recovery` sections to all 13 command templates, following the pattern established by `doit.fixit.md`. Previously, only 1 of 13 templates had error recovery documentation. This feature closes that gap — every command now provides 3-5 documented error scenarios with plain-language summaries, severity indicators, numbered recovery steps, verification commands, prevention tips, and escalation paths.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Every template has `## Error Recovery` section | Done |
| FR-002 | 3-5 error scenarios per template | Done |
| FR-003 | Formatted as subsections with summary, steps, escalation | Done |
| FR-004 | Plain-language summary (≤25 words, no jargon) | Done |
| FR-005 | State preservation guidance for stateful commands | Done |
| FR-006 | Escalation path per scenario | Done |
| FR-007 | Migrated existing On Error subsections | Done |
| FR-008 | Consistent AI-parseable format | Done |
| FR-009 | Compatible with Claude Code + Copilot | Done |
| FR-010 | Severity indicators (WARNING/ERROR/FATAL) | Done |
| FR-011 | Verification steps per scenario | Done |
| FR-012 | Prevention tips where applicable | Done |

## Technical Details

- **Scope**: Documentation/template only — zero Python code changes
- **Pattern**: Each error scenario follows: plain-language summary → `**SEVERITY** | If [condition]:` → numbered recovery steps → `> Prevention:` tip → escalation path
- **Reference**: `doit.fixit.md` established the pattern; all 12 other templates now match
- **Migration**: 9 templates had existing `### On Error` subsections that were migrated and expanded; 3 templates (researchit, scaffoldit, roadmapit) were written from scratch
- **Sync**: All templates synced across 4 locations via `doit sync-prompts`

## Files Changed

### Templates (13 files × 4 locations = 52 files)
- `.doit/templates/commands/doit.{checkin,constitution,documentit,fixit,implementit,planit,researchit,reviewit,roadmapit,scaffoldit,specit,taskit,testit}.md`
- `src/doit_cli/templates/commands/` (package source — identical)
- `.claude/commands/` (Claude Code — identical)
- `.github/prompts/` (GitHub Copilot — identical)

### Tests (1 new file)
- `tests/unit/test_error_recovery_patterns.py` — 159 parametrized tests covering all 13 manual test items (MT-001 through MT-013) plus FR-002 scenario count validation

### Config
- `CLAUDE.md` — agent context update (automated)

## Testing

- **Automated tests**: 1418 passed, 0 failed (159 new + 1259 existing)
- **Requirement coverage**: 12/12 (100%)
- **Review findings**: 0 critical, 0 major, 0 minor (all findings fixed during review)

## Related Issues

- Epic: #767
- Features: #768, #769, #770, #771, #772, #773, #774, #775
- Tasks: #776, #777, #778, #779, #780, #781, #782, #783
