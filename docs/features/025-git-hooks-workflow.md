# Git Hook Integration for Workflow Enforcement

**Completed**: 2026-01-15
**Branch**: 025-git-hooks-workflow
**PR**: (pending)

## Overview

Add Git hook integration to the doit CLI that enforces the spec-driven development workflow. Pre-commit and pre-push hooks validate that code changes are associated with properly documented specifications, ensuring team compliance with the spec-first methodology.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | `doit hooks install` command installs pre-commit and pre-push Git hooks | Done |
| FR-002 | `doit hooks uninstall` command removes installed hooks | Done |
| FR-003 | Pre-commit hook validates feature branches have corresponding spec.md | Done |
| FR-004 | Pre-commit hook checks spec status is not "Draft" for code commits | Done |
| FR-005 | Pre-push hook validates required workflow artifacts (spec.md, plan.md, tasks.md) | Done |
| FR-006 | System skips validation for protected branches (main, develop) | Done |
| FR-007 | Configuration file support via `.doit/config/hooks.yaml` | Done |
| FR-008 | Backup existing hooks before overwriting with `doit hooks restore` | Done |
| FR-009 | Log all hook bypass events (`--no-verify`) to `.doit/logs/hook-bypasses.log` | Done |
| FR-010 | `doit hooks status` command shows hook configuration and installation state | Done |
| FR-011 | Clear, actionable error messages when commits/pushes are blocked | Done |
| FR-012 | `exempt_branches` configuration for branches that bypass validation | Done |
| FR-013 | `exempt_paths` configuration for file patterns that don't require specs | Done |

## Technical Details

### Architecture

- **HookManager** (`src/doit_cli/services/hook_manager.py`): Handles hook installation, uninstallation, backup, and restore
- **HookValidator** (`src/doit_cli/services/hook_validator.py`): Validates workflow compliance for pre-commit and pre-push hooks
- **HookConfig** (`src/doit_cli/models/hook_config.py`): Configuration dataclasses for customizing hook behavior
- **CLI Commands** (`src/doit_cli/cli/hooks_command.py`): Typer-based CLI commands for `doit hooks` subcommand group

### Key Decisions

1. **Shell Templates**: Hook scripts are bash templates that call `doit hooks validate` internally
2. **YAML Configuration**: Uses PyYAML for `.doit/config/hooks.yaml` configuration parsing
3. **Branch Pattern Matching**: Uses `fnmatch` for glob pattern matching on exempt branches/paths
4. **Spec Status Detection**: Parses `**Status**:` field from spec.md using regex

## Files Changed

### New Files

- `src/doit_cli/templates/hooks/pre-commit.sh`
- `src/doit_cli/templates/hooks/pre-push.sh`
- `src/doit_cli/templates/hooks/post-commit.sh`
- `src/doit_cli/models/hook_config.py`
- `src/doit_cli/services/hook_manager.py`
- `src/doit_cli/services/hook_validator.py`
- `src/doit_cli/cli/hooks_command.py`
- `tests/unit/test_hook_manager.py`
- `tests/unit/test_hook_validator.py`
- `tests/unit/test_hook_config.py`
- `tests/integration/test_hooks_command.py`

### Modified Files

- `pyproject.toml` - Added PyYAML dependency
- `src/doit_cli/main.py` - Registered hooks_app subcommand

## Testing

- **Unit Tests**: 64 tests covering HookManager, HookValidator, and HookConfig
- **Integration Tests**: 10 tests covering CLI command execution
- **Total**: 74 hook-specific tests, 212 total project tests passing

## CLI Commands

| Command | Description |
|---------|-------------|
| `doit hooks install` | Install pre-commit and pre-push hooks |
| `doit hooks uninstall` | Remove installed hooks |
| `doit hooks status` | Show installation and configuration status |
| `doit hooks restore` | Restore backed up hooks |
| `doit hooks validate <type>` | Run validation (called by hooks) |
| `doit hooks report` | Show bypass audit log |

## Related Issues

- Epic: #190
- Features: #191, #192, #193, #194, #195
- Tasks: #196-#222

## User Stories

1. **US-1 Hook Installation** (P1): Install workflow enforcement hooks with a single command
2. **US-2 Pre-Commit Validation** (P1): Block commits without associated specifications
3. **US-3 Pre-Push Validation** (P2): Validate workflow artifacts before pushing
4. **US-4 Hook Configuration** (P2): Customizable enforcement rules via configuration file
5. **US-5 Hook Bypass** (P3): Audit trail for `--no-verify` usage
