# Project-Level Personas with Context Injection

**Completed**: 2026-03-26
**Branch**: `056-persona-context-injection`
**Epic**: #722

## Overview

Adds project-level personas as a first-class context source in the doit workflow. During roadmap creation (`/doit.roadmapit`), the system generates `.doit/memory/personas.md` using the existing `personas-output-template.md`. This file is registered as a new context source in `context.yaml` at priority 3, so that `/doit.researchit`, `/doit.planit`, and `/doit.specit` automatically receive persona context.

Builds on `053-stakeholder-persona-templates` and elevates personas from per-feature artifacts to persistent project-level knowledge.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Generate personas.md during roadmapit | Done |
| FR-002 | Derive personas from constitution/roadmap | Done |
| FR-003 | Register personas as context source | Done |
| FR-004 | Load personas when enabled and exists | Done |
| FR-005 | Skip gracefully when file missing | Done |
| FR-006 | Researchit receives persona context | Done |
| FR-007 | Specit maps user stories to persona IDs | Done |
| FR-008 | Planit receives persona context | Done |
| FR-009 | Per-command overrides disable personas | Done |
| FR-010 | Feature-level personas take precedence | Done |
| FR-011 | Preserve existing personas on re-run | Done |
| FR-012 | Load in full without truncation | Done |

## Technical Details

- **Context priority**: Personas load at priority 3 (after constitution and tech_stack, before roadmap)
- **Feature-level precedence**: `specs/{feature}/personas.md` overrides `.doit/memory/personas.md` when both exist
- **No truncation**: Personas always loaded in full; per-command overrides disable the source entirely if context budget is a concern
- **Command overrides**: Personas enabled for `researchit`, `specit`, `planit`; disabled for `constitution`, `roadmapit`, `taskit`, `implementit`, `testit`, `reviewit`, `checkin`
- **Bug fix**: Fixed pre-existing `_from_dict` command merge issue where YAML overrides replaced (instead of merging with) Python default command overrides

## Files Changed

### Python Code

- `src/doit_cli/models/context_config.py` — personas in default_sources, source_priorities, display_names, command overrides; fixed _from_dict merge
- `src/doit_cli/services/context_loader.py` — load_personas() method, wired into load(), added to get_memory_files()

### Templates

- `src/doit_cli/templates/config/context.yaml` — personas source entry, completed_roadmap added, priority alignment
- `src/doit_cli/templates/commands/doit.roadmapit.md` — Step 6b persona generation
- `src/doit_cli/templates/commands/doit.researchit.md` — persona context reference
- `src/doit_cli/templates/commands/doit.specit.md` — persona-story mapping
- `src/doit_cli/templates/commands/doit.planit.md` — persona context reference with fallback

### Configuration

- `.doit/config/context.yaml` — live config with personas source and aligned priorities

### Tests

- `tests/unit/test_context_config.py` — updated priorities, default commands assertions, merge behavior tests
- `tests/unit/test_context_loader.py` — 16 new personas tests covering all requirements

## Testing

- **Automated tests**: 127 passed, 0 failed (18 new tests added)
- **Test coverage**: 12/12 functional requirements covered (5 direct + 6 template + 1 partial with dedicated test)
- **Integration verified**: `doit context show` with/without personas file, command overrides for specit/taskit/planit

## Related Issues

- Epic: #722
- Features: #723, #724, #725, #726, #727, #728
- Tasks: #729-#742
