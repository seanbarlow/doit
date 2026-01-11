# Research: Init Scripts Copy

**Feature**: 011-init-scripts-copy
**Date**: 2026-01-10
**Status**: Complete

## Executive Summary

This feature adds automatic copying of workflow bash scripts during `doit init`. The implementation follows the existing pattern used for workflow templates and GitHub issue templates, extending `TemplateManager` with a new `copy_scripts()` method.

## Current Implementation Analysis

### Init Command Flow ([init_command.py](../../src/doit_cli/cli/init_command.py))

The `run_init()` function currently:
1. Creates project model and validates paths
2. Creates `.doit/` directory structure via `Scaffolder`
3. Copies workflow templates to `.doit/templates/` (lines 329-336)
4. Copies GitHub issue templates to `.github/ISSUE_TEMPLATE/` (lines 338-345)
5. Copies agent command templates (lines 347-359)
6. Creates copilot instructions if applicable (lines 361-375)

**Gap**: No script copying currently happens. The `.doit/scripts/` directory is created by `Scaffolder` but remains empty.

### Template Manager ([template_manager.py](../../src/doit_cli/services/template_manager.py))

Already implements two copy methods that serve as patterns:
- `copy_workflow_templates()` (lines 355-401)
- `copy_github_issue_templates()` (lines 403-458)

Both use the same pattern:
1. Define list of files to copy (module-level constants)
2. Get source path from bundled templates
3. Ensure target directory exists
4. Copy files with overwrite logic
5. Return dict with `created`, `updated`, `skipped` lists

### Scaffolder ([scaffolder.py](../../src/doit_cli/services/scaffolder.py))

Creates `.doit/scripts/` directory (line 15: `DOIT_SUBDIRS = ["memory", "templates", "scripts"]`) but does not populate it.

## Existing Scripts Analysis

Five bash scripts located in `.doit/scripts/bash/`:

| Script | Lines | Purpose | Dependencies |
|--------|-------|---------|--------------|
| `common.sh` | 157 | Shared utility functions | None (sourced by others) |
| `check-prerequisites.sh` | 167 | Validate feature branch and docs | `common.sh` |
| `create-new-feature.sh` | 298 | Create feature branch and spec dir | git, optional gh CLI |
| `setup-plan.sh` | 62 | Copy plan template to feature dir | `common.sh` |
| `update-agent-context.sh` | 800 | Update agent context files | `common.sh` |

### Script Compatibility Assessment

All scripts are already designed to work with the current doit workflow:

1. **common.sh**: Uses `.doit/templates/` path for templates (line 40)
2. **create-new-feature.sh**: References `$REPO_ROOT/.doit/templates/spec-template.md` (line 283)
3. **setup-plan.sh**: References `$REPO_ROOT/.doit/templates/plan-template.md` (line 40)
4. **check-prerequisites.sh**: Uses standard feature paths from `common.sh`
5. **update-agent-context.sh**: References `$REPO_ROOT/.doit/templates/agent-file-template.md` (line 80)

**Finding**: Scripts reference templates in `.doit/templates/` which is now populated during init. Scripts are compatible with current workflow.

## Implementation Approach

### Option 1: Follow Existing Pattern (Recommended)

Add `copy_scripts()` method to `TemplateManager` following `copy_workflow_templates()` pattern:

```python
WORKFLOW_SCRIPTS = [
    "common.sh",
    "check-prerequisites.sh",
    "create-new-feature.sh",
    "setup-plan.sh",
    "update-agent-context.sh",
]

def copy_scripts(self, target_dir: Path, overwrite: bool = False) -> dict:
    # Same pattern as copy_workflow_templates
    # Use shutil.copy2 to preserve permissions
```

**Pros**:
- Consistent with existing code
- Simple, minimal changes
- `shutil.copy2` preserves execute permissions

**Cons**:
- None identified

### Option 2: Separate ScriptManager Class

Create new `script_manager.py` service.

**Pros**:
- Separation of concerns

**Cons**:
- Over-engineering for 5 files
- Inconsistent with how templates are handled
- More files to maintain

**Decision**: Option 1 - follow existing pattern.

## Bundling Strategy

Scripts must be bundled with the doit-cli package for distribution:

### Current Bundling (pyproject.toml)

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/doit_cli"]

[tool.hatch.build.targets.wheel.force-include]
"templates" = "doit_cli/templates"
```

### Required Addition

Scripts need to be included alongside templates:

```toml
[tool.hatch.build.targets.wheel.force-include]
"templates" = "doit_cli/templates"
".doit/scripts" = "doit_cli/scripts"
```

Or maintain scripts in `templates/scripts/bash/` for consistency with template bundling.

## Source Path Resolution

The `get_base_template_path()` method in `TemplateManager` handles two cases:
1. **Installed package**: Uses `importlib.resources` to find bundled files
2. **Development mode**: Falls back to repo root `templates/` directory

Scripts should follow the same pattern:
- Bundled: `doit_cli/scripts/bash/`
- Development: `.doit/scripts/bash/` or `templates/scripts/bash/`

## File Permission Handling

Scripts require execute permissions (mode 755). Using `shutil.copy2` preserves the original file's permissions:

```python
shutil.copy2(source_path, target_path)  # Preserves mode, timestamps
```

Alternatively, explicitly set permissions after copy:

```python
import os
shutil.copy(source_path, target_path)
os.chmod(target_path, 0o755)  # Ensure executable
```

**Recommendation**: Use `shutil.copy2` since source scripts already have correct permissions.

## Edge Cases

1. **Missing source scripts**: Return gracefully with empty result (matches template behavior)
2. **Permission errors on copy**: Let exception propagate (matches template behavior)
3. **Windows compatibility**: Scripts are still copied; users need bash/WSL to execute
4. **Update mode**: `--update` flag should update scripts same as templates

## Testing Strategy

1. **Unit tests**: Test `copy_scripts()` method directly
2. **Integration tests**: Test `doit init` copies scripts
3. **Permission tests**: Verify scripts are executable after copy
4. **Overwrite tests**: Test `--force` and `--update` behavior

## Dependencies

- No new dependencies required
- Uses existing: `shutil`, `pathlib`
- Test dependencies: `pytest`, `tempfile`

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Scripts not bundled correctly | Medium | High | Test wheel distribution |
| Permission issues on copy | Low | Medium | Use shutil.copy2 |
| Path resolution fails | Low | High | Follow existing template pattern |

## Conclusion

Implementation is straightforward following the established pattern for template copying. The main work involves:
1. Adding `WORKFLOW_SCRIPTS` constant and `copy_scripts()` method to `TemplateManager`
2. Calling `copy_scripts()` in `run_init()`
3. Updating `pyproject.toml` to bundle scripts
4. Adding tests

Estimated complexity: Low - follows existing patterns exactly.
