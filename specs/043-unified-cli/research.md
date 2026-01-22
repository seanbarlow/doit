# Research: Unified CLI Package

**Feature**: `043-unified-cli`
**Date**: 2026-01-22
**Purpose**: Investigate package structure, identify conflicts, and determine migration strategy

## Executive Summary

Analysis confirms that `doit_toolkit_cli` can be fully merged into `doit_cli` with minimal conflicts. Only one naming conflict exists (`github_service.py`), which can be resolved by merging complementary functionality. The migration is low-risk as most imports are internal to `doit_toolkit_cli`.

## Current Package Analysis

### doit_cli (Main Package)

**Location**: `src/doit_cli/`
**File Count**: 94 Python files
**Structure**:

```text
src/doit_cli/
├── __init__.py
├── main.py              # Entry point
├── cli/                 # Command modules (14 files)
├── formatters/          # Output formatters (5 files)
├── models/              # Data models (19 files)
├── prompts/             # Interactive prompts (2 files)
├── rules/               # Validation rules (2 files)
└── services/            # Business logic (52 files)
```

**Commands**: init, status, sync-prompts, validate, verify, analytics, context, diagram, fixit, hooks, memory, roadmapit, team, xref

### doit_toolkit_cli (Secondary Package)

**Location**: `src/doit_toolkit_cli/`
**File Count**: 18 Python files
**Structure**:

```text
src/doit_toolkit_cli/
├── commands/            # 1 file (roadmapit.py)
├── models/              # 7 files
├── services/            # 5 files
└── utils/               # 4 files
```

**Purpose**: GitHub integration, milestone management, roadmap services

## Naming Conflict Analysis

### Single Conflict Identified

| File | doit_cli Version | doit_toolkit_cli Version |
|------|------------------|--------------------------|
| `github_service.py` | Issue operations (fixit command) | Epic/milestone operations (roadmapit command) |

### Detailed Comparison

**doit_cli/services/github_service.py**:
- `GitHubService` class with issue operations
- Methods: `get_issue`, `list_bugs`, `close_issue`, `add_comment`, `check_branch_exists`, `create_branch`
- Used by: `fixit_command.py`

**doit_toolkit_cli/services/github_service.py**:
- `GitHubService` class with epic/milestone operations
- Methods: `fetch_epics`, `fetch_features_for_epic`, `create_epic`, `get_all_milestones`, `create_milestone`, `close_milestone`
- Additional errors: `GitHubAuthError`, `GitHubAPIError`
- Used by: `roadmapit.py`, `milestone_service.py`

### Resolution Decision

**Decision**: Merge both into single comprehensive `github_service.py`

**Rationale**:
- Methods are complementary, not duplicated
- Same underlying pattern (gh CLI subprocess calls)
- Reduces import complexity
- Single point for GitHub authentication checks

**Alternatives Rejected**:
- Separate files (`github_issues_service.py`, `github_epics_service.py`) - adds unnecessary complexity
- Keep toolkit version only - loses fixit functionality

## Import Dependency Analysis

### Files Requiring Import Updates

**In src/ (8 files)**:
1. `doit_cli/cli/roadmapit_command.py` - wrapper import
2. `doit_toolkit_cli/commands/roadmapit.py` - main roadmapit logic
3. `doit_toolkit_cli/services/github_service.py` - model imports
4. `doit_toolkit_cli/services/github_cache_service.py` - model imports
5. `doit_toolkit_cli/services/milestone_service.py` - model/service imports
6. `doit_toolkit_cli/services/roadmap_merge_service.py` - model imports
7. `doit_toolkit_cli/models/github_epic.py` - model import
8. `doit_toolkit_cli/models/roadmap.py` - model import

**In tests/ (5 files)**:
- Test files importing from `doit_toolkit_cli` for testing

### Import Change Strategy

All `from doit_toolkit_cli.` imports become `from doit_cli.` with paths:

| Old Path | New Path |
|----------|----------|
| `doit_toolkit_cli.commands.roadmapit` | `doit_cli.cli.roadmapit_impl` |
| `doit_toolkit_cli.models.*` | `doit_cli.models.*` |
| `doit_toolkit_cli.services.*` | `doit_cli.services.*` |
| `doit_toolkit_cli.utils.*` | `doit_cli.utils.*` |

## Migration Strategy

### Phase 1: Prepare doit_cli Structure

1. Create `src/doit_cli/utils/` directory (doesn't exist yet)
2. Verify no circular import risks

### Phase 2: Move doit_toolkit_cli Modules

**Models** (move to `doit_cli/models/`):
- `github_epic.py` → `doit_cli/models/github_epic.py`
- `github_feature.py` → `doit_cli/models/github_feature.py`
- `milestone.py` → `doit_cli/models/milestone.py`
- `priority.py` → `doit_cli/models/priority.py`
- `roadmap.py` → `doit_cli/models/roadmap.py`
- `sync_metadata.py` → `doit_cli/models/sync_metadata.py`
- `sync_operation.py` → `doit_cli/models/sync_operation.py`

**Services** (move to `doit_cli/services/`):
- `github_cache_service.py` → `doit_cli/services/github_cache_service.py`
- `github_linker.py` → `doit_cli/services/github_linker.py`
- `milestone_service.py` → `doit_cli/services/milestone_service.py`
- `roadmap_matcher.py` → `doit_cli/services/roadmap_matcher.py`
- `roadmap_merge_service.py` → `doit_cli/services/roadmap_merge_service.py`
- `github_service.py` → MERGE with existing

**Utils** (create `doit_cli/utils/` and move):
- `fuzzy_match.py` → `doit_cli/utils/fuzzy_match.py`
- `github_auth.py` → `doit_cli/utils/github_auth.py`
- `priority_mapper.py` → `doit_cli/utils/priority_mapper.py`
- `spec_parser.py` → `doit_cli/utils/spec_parser.py`

**Commands**:
- `commands/roadmapit.py` → `doit_cli/cli/roadmapit_impl.py` (rename to avoid conflict with wrapper)

### Phase 3: Merge github_service.py

1. Copy `GitHubAuthError`, `GitHubAPIError` from toolkit version
2. Add epic/milestone methods to existing `GitHubService` class
3. Unify authentication checking approach
4. Update all imports to use merged service

### Phase 4: Update Imports

1. Update all moved files with new import paths
2. Update `doit_cli/cli/roadmapit_command.py` wrapper
3. Update test files
4. Run `grep -r "doit_toolkit_cli"` to verify none remain

### Phase 5: Update Configuration

1. Update `pyproject.toml`:
   - Remove `src/doit_toolkit_cli` from `packages`
   - Keep only `src/doit_cli`
2. Delete `src/doit_toolkit_cli/` directory

### Phase 6: Verification

1. Run full test suite
2. Build wheel and verify contents
3. Install in fresh virtualenv
4. Test all CLI commands

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Circular imports | Low | High | Check import order before moving |
| Test failures | Medium | Medium | Update imports incrementally |
| Missing file in wheel | Low | High | Verify with `hatch build` after each phase |
| Breaking change | Low | High | No public API changes, internal only |

## Recommendations

1. **Execute migration in atomic phases** - complete each phase before starting next
2. **Commit after each phase** - enables rollback if issues found
3. **Run tests after each phase** - catch issues early
4. **Use search-replace for imports** - consistent, less error-prone

## Conclusion

The migration is straightforward with well-defined phases. The single naming conflict has a clear resolution path. Low external dependency risk as `doit_toolkit_cli` was never a public API.
