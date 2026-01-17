# Init Workflow Integration

**Completed**: 2026-01-16
**Branch**: `031-init-workflow-integration`
**Epic**: #321

## Overview

This feature integrates the `doit init` command with the guided workflow system (Feature 030), providing step-by-step guidance through project initialization with progress tracking, state persistence, and CLI flag pre-population.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | InitWorkflow with steps for agent selection, path confirmation, optional settings | Done |
| FR-002 | WorkflowEngine orchestrates init command when running interactively | Done |
| FR-003 | Non-interactive mode (`--yes` flag) bypasses workflow engine | Done |
| FR-004 | Preserve all existing init command flags | Done |
| FR-005 | Display step progress (e.g., "Step 1/3") | Done |
| FR-006 | Allow navigation back to previous steps | Done |
| FR-007 | Save workflow state when interrupted (Ctrl+C) | Done |
| FR-008 | Prompt to resume or start fresh when interrupted state detected | Done |
| FR-009 | Clean up state files upon successful completion | Done |
| FR-010 | Step for selecting target agent(s): Claude, Copilot, Both | Done |
| FR-011 | Step for confirming project path with directory validation | Done |
| FR-012 | Optional step for custom template directory selection | Done |
| FR-014 | Comprehensive workflow system guide documentation | Done |

## User Stories Delivered

1. **US1 - Interactive Init with Workflow Engine** (P1): `doit init .` shows step-by-step workflow with progress indicators
2. **US2 - Non-Interactive Init Mode** (P1): `doit init . --yes` completes without prompts using defaults
3. **US3 - Enhanced Progress Display** (P2): Visual feedback showing file/directory creation progress
4. **US4 - Comprehensive Workflow Documentation** (P2): Architecture, extension guides, and API reference
5. **US5 - State Recovery for Init** (P3): Interrupted workflows can be resumed from saved state

## Technical Details

### Architecture

The init workflow integration extends the existing workflow system:

- **create_init_workflow()**: Factory function creating a 3-step workflow definition
- **map_workflow_responses()**: Maps workflow responses to init parameters
- **WorkflowEngine.run()**: Enhanced with `initial_responses` parameter for CLI flag pre-population
- **StateManager**: State persisted to target path (not cwd) for correct resume behavior

### Key Design Decisions

1. **CLI flag pre-population**: `--agent` flag pre-populates workflow response and skips that step
2. **Target path state storage**: State files stored in `{target_path}/.doit/state/` not `cwd/.doit/state/`
3. **Graceful cancellation**: `confirm-path=no` raises `typer.Exit(0)` for clean abort
4. **Return type optimization**: `map_workflow_responses()` returns `tuple[list[Agent], Optional[Path]]` for direct use

### Workflow Steps

| Step | ID | Options | Required | Default |
|------|----|---------|----------|---------|
| 1 | select-agent | claude, copilot, both | Yes | claude |
| 2 | confirm-path | yes, no | Yes | yes |
| 3 | custom-templates | (path input) | No | "" |

## Files Changed

### Modified Files

- `src/doit_cli/cli/init_command.py` - Integrated workflow system
- `src/doit_cli/services/workflow_engine.py` - Added `initial_responses` parameter

### New Documentation

- `docs/guides/workflow-system-guide.md` - Comprehensive workflow guide (~1,200 words)
- `docs/tutorials/creating-workflows.md` - Tutorial for custom workflows (~600 words)

### Test Files

- `tests/unit/test_init_workflow.py` - 18 tests (workflow factory and mapping)
- `tests/integration/test_init_workflow_integration.py` - 10 tests (end-to-end integration)

## Testing

- **Unit tests**: 28 tests passing
- **Integration tests**: 10 tests passing
- **Manual tests**: 8/8 passed (after bug fixes)

### Bug Fixes During Review

1. **MT-005**: State directory now uses target path instead of `cwd()` for correct resume behavior
2. **MT-007**: CLI flags (`--agent`) now pre-populate workflow responses and skip corresponding steps

## Related Issues

- Epic: #321
- Features: #322, #323, #324
- Bugs Fixed: #336 (MT-005), #337 (MT-007)

## Usage Examples

### Interactive Mode

```bash
$ doit init /path/to/project

Step 1/3: Select AI Agent
Which AI agent(s) should doit support?
  [1] Claude Code
  [2] GitHub Copilot
  [3] Both
> 1

Step 2/3: Confirm Path
Initialize doit in '/path/to/project'?
  [1] Yes
  [2] No
> 1

Step 3/3: Custom Templates (Optional)
Enter custom template directory (press Enter to skip):
>

Initializing project...
Created: .doit/
Created: .claude/commands/
Created: specs/
Done!
```

### Non-Interactive Mode

```bash
# Use defaults (Claude, no custom templates)
doit init . --yes

# Specify agent
doit init . --yes --agent copilot

# Specify multiple agents
doit init . --yes --agent claude,copilot
```

### CLI Flag Skips Workflow Step

```bash
$ doit init . --agent claude

Skipping Select AI Agent (provided via CLI)

Step 1/2: Confirm Path
Initialize doit in '.'?
```

### Resuming Interrupted Workflow

```bash
$ doit init .
Step 1/3: Select AI Agent
> ^C  # User presses Ctrl+C

$ doit init .
Found interrupted workflow from 2026-01-16 10:30:00
Resume from step 1? [y/n]:
```

## Documentation Links

- [Workflow System Guide](../guides/workflow-system-guide.md)
- [Creating Workflows Tutorial](../tutorials/creating-workflows.md)
