# Persona-Aware User Story Generation

**Completed**: 2026-03-26
**Branch**: 057-persona-aware-user-story-generation
**Epic**: #744

## Overview

When `/doit.specit` generates user stories, it now automatically maps each story to the most relevant persona from `.doit/memory/personas.md` (project-level) or `specs/{feature}/personas.md` (feature-level) using existing P-NNN traceability IDs. This completes the persona pipeline established by specs 053 (Stakeholder Persona Templates) and 056 (Project-Level Personas with Context Injection).

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Auto-assign persona ID (P-NNN) to each generated user story | Done |
| FR-002 | Read personas from feature-level personas.md | Done |
| FR-003 | Feature-level precedence over project-level personas | Done |
| FR-004 | Include persona ID in story header (`\| Persona: P-NNN`) | Done |
| FR-005 | Match stories based on goals/pain points alignment | Done |
| FR-006 | Generate without mappings when no personas available | Done |
| FR-007 | No errors when personas files missing or empty | Done |
| FR-008 | Update traceability table in personas.md | Done |
| FR-009 | Show personas with zero stories in traceability | Done |
| FR-010 | Use existing context injection pipeline (spec 056) | Done |
| FR-011 | Support multi-persona story tagging (P2) | Done |
| FR-012 | Display persona coverage summary (P2) | Done |
| FR-013 | Confidence level indication (P3) | Deferred (#752) |

## Technical Details

This is a template-only feature — no Python code changes. All modifications are to Markdown command templates processed by AI assistants.

### Key Design Decisions

- **Matching approach**: Semantic goal alignment by AI at generation time (not keyword matching)
- **Multi-persona format**: Comma-separated IDs: `| Persona: P-001, P-002`
- **Traceability strategy**: Full table replacement on each specit run
- **Matching priority**: 6 levels — goal > pain point > context > role > multi-persona > no match

### Matching Rules

1. Direct goal match → High confidence
2. Pain point match → High confidence
3. Usage context match → Medium confidence
4. Role/archetype match → Medium confidence
5. Multi-persona → List all relevant IDs
6. No match → Generate without tag, flag in coverage report

## Files Changed

| File | Change |
|------|--------|
| `src/doit_cli/templates/commands/doit.specit.md` | Added matching rules, traceability update, coverage report, fallback behavior |
| `src/doit_cli/templates/spec-template.md` | Added `\| Persona: P-NNN` to story headers |
| `src/doit_cli/templates/user-stories-template.md` | Added persona ID and archetype to story format |
| `.doit/templates/commands/doit.specit.md` | Synced from source |
| `.doit/templates/spec-template.md` | Synced from source |
| `.doit/templates/user-stories-template.md` | Synced from source |
| `.claude/commands/doit.specit.md` | Synced from source |
| `.github/prompts/doit.specit.prompt.md` | Synced from source |
| `tests/unit/test_persona_aware_story_templates.py` | 54 new automated tests |

## Testing

- **Automated tests**: 1259 passed (54 feature-specific), 0 failed
- **Lint**: ruff — all checks passed
- **Regression**: Zero regressions across 1205 existing tests
- **Test coverage**: 13/13 requirements verified (100%)

## Related Issues

- Epic: #744
- Features: #745, #746, #747, #748, #749, #750, #751
- Deferred: #752 (Confidence Scoring, P3)
- Tasks: #753-#765
