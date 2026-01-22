# Constitution and Tech Stack Separation

**Completed**: 2026-01-22
**Branch**: 046-constitution-tech-stack-split
**Priority**: P2 - High Priority
**Epic**: [#605](https://github.com/seanbarlow/doit/issues/605)

## Overview

Separates the constitution file into two distinct documents: one focused on project principles and governance (constitution.md), and another focused on technical implementation decisions (tech-stack.md). This provides cleaner separation of concerns and enables more targeted context loading for AI agents.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Constitution.md contains only principles, standards, governance, workflow | Done |
| FR-002 | Tech-stack.md contains languages, frameworks, libraries sections | Done |
| FR-003 | Tech-stack.md contains infrastructure section | Done |
| FR-004 | Tech-stack.md contains deployment section | Done |
| FR-005 | Both files have cross-references to each other | Done |
| FR-006 | `doit init` creates both files with proper separation | Done |
| FR-007 | `/doit.constitution cleanup` migrates existing combined files | Done |
| FR-008 | Cleanup creates timestamped backup before modification | Done |
| FR-009 | Cleanup supports --dry-run and --merge flags | Done |
| FR-010 | Context loader recognizes tech_stack as loadable source | Done |
| FR-011 | Command overrides disable tech_stack for specit, constitution | Done |
| FR-012 | Planit and taskit templates reference tech-stack.md | Done |
| FR-013 | Legacy fallback for projects without tech-stack.md | Done |

## User Stories

### US1: New Project Setup (P1 - MVP)
When a developer runs `doit init` on a new project, both constitution.md and tech-stack.md are created with proper separation and cross-references.

**Test Command**: `doit init --yes` in new directory

### US2: Migrate Existing Constitution (P1)
Developers with existing combined constitution files can run `/doit.constitution cleanup` to automatically separate tech content into tech-stack.md.

**Test Command**: `doit constitution cleanup --dry-run`

### US3: AI Agent Research Phase (P2)
AI agents running `/doit.planit` and `/doit.taskit` load tech-stack.md for technical decisions.

**Test Command**: Run `/doit.planit` on a project with separated files

### US4: Context Loading Optimization (P3)
Context loading system recognizes tech-stack.md as a loadable source with command-specific configuration.

**Test Command**: `doit context show`

## Technical Details

### Architecture

**Service Layer**:
- `CleanupService` - Orchestrates constitution cleanup and migration
- `ContextLoader` - Extended with `load_tech_stack()` method

**Models**:
- `CleanupResult` - Dataclass tracking cleanup operation results
- `AnalysisResult` - Dataclass for analyzing constitution content
- `SourceConfig` - Extended with tech_stack source configuration
- `CommandOverride` - Default overrides for specit, constitution, roadmapit

### Key Decisions

1. **Cross-Reference Pattern**: Uses blockquote format `> **See also**: [File](link)` after H1 header
2. **Section Detection**: Uses TECH_SECTIONS constant with regex matching for H2 headers
3. **Backup Strategy**: Creates timestamped `.bak.YYYYMMDD_HHMMSS` files before modification
4. **Context Priority**: tech_stack has priority 2, after constitution (1), before roadmap (3)
5. **Command Overrides**: specit and constitution commands disable tech_stack loading

### Tech Sections Detection

```python
TECH_SECTIONS = ["Tech Stack", "Infrastructure", "Deployment"]
```

Headers are matched by:
1. Exact match to TECH_SECTIONS names
2. Partial match (header contains the section name)
3. Keyword detection for ambiguous headers (3+ tech keywords = tech section)

## Files Changed

### Created (5 files)
- `templates/memory/tech-stack.md` - New template for tech stack information
- `src/doit_cli/models/cleanup_models.py` - CleanupResult and AnalysisResult dataclasses
- `src/doit_cli/services/cleanup_service.py` - CleanupService implementation (~300 lines)
- `src/doit_cli/cli/constitution_command.py` - CLI command with cleanup subcommand
- `tests/unit/test_cleanup_service.py` - 19 unit tests for CleanupService

### Modified (14 files)
- `templates/memory/constitution.md` - Removed tech sections, added cross-reference
- `src/doit_cli/services/template_manager.py` - Added "tech-stack.md" to MEMORY_TEMPLATES
- `src/doit_cli/main.py` - Registered constitution command
- `src/doit_cli/models/context_config.py` - Added tech_stack source, command overrides
- `src/doit_cli/services/context_loader.py` - Added load_tech_stack() method
- `templates/config/context.yaml` - Added tech_stack configuration
- `templates/commands/doit.constitution.md` - Added cleanup subcommand docs
- `templates/commands/doit.planit.md` - Added tech-stack.md reference
- `templates/commands/doit.taskit.md` - Added tech-stack.md reference
- `docs/quickstart.md` - Updated context loading docs
- `tests/integration/test_init_command.py` - Added 6 integration tests
- `tests/unit/test_context_loader.py` - Added 7 unit tests
- `tests/unit/test_context_config.py` - Updated for new defaults

## Testing

### Automated Tests
- **Total Tests**: 1,377 tests passed
- **New Tests**: 32 tests added (19 unit + 6 integration + 7 context loader)
- **No regressions detected** - All existing functionality intact

### Test Coverage

**CleanupService Tests** (`tests/unit/test_cleanup_service.py`):
- analyze() identifies tech sections correctly
- analyze() identifies preserved sections
- analyze() handles no tech sections
- analyze() handles missing constitution
- create_backup() creates backup file
- create_backup() handles missing file
- cleanup() creates tech-stack.md
- cleanup() removes tech from constitution
- cleanup() adds cross-references
- cleanup() creates backup
- cleanup() dry_run doesn't change files
- cleanup() handles no tech sections
- cleanup() fails when tech-stack exists (no merge)
- cleanup() succeeds with merge flag

**Init Command Tests** (`tests/integration/test_init_command.py`):
- init creates both constitution.md and tech-stack.md
- constitution has cross-reference to tech-stack
- tech-stack has cross-reference to constitution
- tech-stack has required sections (Languages, Frameworks, etc.)
- constitution does not have tech sections
- update preserves existing tech-stack

## Usage

### CLI Commands

```bash
# Initialize new project with separated files
doit init --yes

# Preview cleanup of existing constitution
doit constitution cleanup --dry-run

# Perform cleanup (creates backup automatically)
doit constitution cleanup

# Merge with existing tech-stack.md if it exists
doit constitution cleanup --merge
```

### Slash Commands (Claude Code)

```
# Cleanup existing constitution
/doit.constitution cleanup

# Preview cleanup
/doit.constitution cleanup --dry-run
```

## Example Output

### Cleanup Command

```
Analyzing constitution.md...

Found 3 tech sections to extract:
  - Tech Stack
  - Infrastructure
  - Deployment

Found 4 sections to preserve:
  - Purpose & Goals
  - Core Principles
  - Quality Standards
  - Governance

Creating backup: constitution.md.bak.20260122_143052

Creating tech-stack.md from extracted sections...
Updating constitution.md with cross-references...

Cleanup complete!
  - Backup: .doit/memory/constitution.md.bak.20260122_143052
  - Created: .doit/memory/tech-stack.md
  - Updated: .doit/memory/constitution.md
```

## Success Criteria

| Criteria | Status | Verification |
|----------|--------|--------------|
| SC-001: New init creates both files | Verified | Both files exist with cross-references |
| SC-002: Cleanup migrates existing projects | Verified | Tech sections extracted correctly |
| SC-003: Backup created before modification | Verified | Timestamped .bak file created |
| SC-004: Context loading respects overrides | Verified | specit/constitution commands skip tech_stack |
| SC-005: No regressions in existing tests | Verified | 1,377 tests pass |

## Related Issues

- **Epic**: [#605](https://github.com/seanbarlow/doit/issues/605) - Constitution and Tech Stack Separation

## Impact

- **Cleaner Separation**: Principles separate from technical decisions
- **Targeted Context**: AI agents can load only relevant files
- **Migration Path**: Existing projects can cleanly migrate
- **Future-Proof**: Easier to update tech stack without touching governance

## Next Steps

1. **Merge PR**: Review and merge to main branch
2. **Close Epic**: Close GitHub issue #605
3. **Update Existing Projects**: Run `doit constitution cleanup` on projects

---

**Feature Documentation Generated**: 2026-01-22
**Generated by**: `/doit.checkin`
