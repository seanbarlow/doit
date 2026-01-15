# Unified Template Management

**Completed**: 2026-01-15
**Branch**: `024-unified-templates`
**PR**: #189

## Overview

Consolidated doit command templates into a single source of truth (`templates/commands/`), eliminating the need to maintain separate template files for Claude Code commands and GitHub Copilot prompts. Copilot prompts are now generated dynamically via transformation rather than stored as duplicate files.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Use `templates/commands/` as single source of truth | Done |
| FR-002 | Generate Copilot prompts dynamically during `doit init --agent copilot` | Done |
| FR-003 | Copy command templates directly for Claude during `doit init --agent claude` | Done |
| FR-004 | Remove `templates/prompts/` directory from repository | Done |
| FR-005 | Update `TemplateManager` to generate prompts on-demand | Done |
| FR-006 | Preserve `sync-prompts` command functionality | Done |
| FR-007 | Apply appropriate transformations (strip YAML, replace placeholders) | Done |
| FR-008 | Handle both development and installed package modes | Done |
| FR-009 | Provide clear error messages on transformation failure | Done |
| FR-010 | Preserve backward compatibility for `doit init` and `sync-prompts` | Done |

## Technical Details

### Architecture Change

**Before**:
```
templates/
├── commands/       (Claude source)
│   └── doit.*.md
└── prompts/        (Copilot source - DUPLICATE)
    └── doit-*.prompt.md
```

**After**:
```
templates/
└── commands/       (Single source of truth)
    └── doit.*.md

# Copilot prompts generated dynamically during `doit init`
```

### Key Changes

1. **Agent model** (`src/doit_cli/models/agent.py`):
   - `template_directory` now returns "commands" for all agents
   - Added `needs_transformation` property (True for Copilot, False for Claude)

2. **TemplateManager** (`src/doit_cli/services/template_manager.py`):
   - Added `_get_command_templates()` to read from unified source
   - Added `_transform_and_write_templates()` for Copilot transformation
   - Updated `copy_templates_for_agent()` to use dynamic generation

3. **Deleted**: `templates/prompts/` directory (11 duplicate prompt files)

## Files Changed

### Source Code
- `src/doit_cli/models/agent.py` - Agent property changes
- `src/doit_cli/services/template_manager.py` - Dynamic generation logic

### Tests
- `tests/unit/test_agent.py` - New file with 21 tests
- `tests/unit/test_template_manager.py` - Added TestUnifiedTemplates class (8 tests)

### Deleted
- `templates/prompts/` - Entire directory removed (11 files)

## Testing

- **Automated tests**: 138 passed
- **Integration tests**: 16 passed (test_init_command.py)
- **Manual tests**: All verification checklist items passed
  - Claude init creates `.claude/commands/doit.*.md`
  - Copilot init creates `.github/prompts/doit-*.prompt.md`
  - sync-prompts reads from commands/ only
  - YAML frontmatter preserved for Claude, stripped for Copilot

## Related Issues

- Epic: #171
- Features: #172, #173, #174, #175
- Tasks: #176, #177, #178, #179, #180, #181, #182, #183, #184, #185, #186, #187, #188
