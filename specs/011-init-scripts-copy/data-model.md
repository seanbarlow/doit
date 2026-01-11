# Data Model: Init Scripts Copy

**Feature**: 011-init-scripts-copy
**Date**: 2026-01-10

## Overview

This feature introduces no new data models or database schemas. It extends existing patterns with a constant and method for copying bash scripts.

## Constants

### WORKFLOW_SCRIPTS

```python
WORKFLOW_SCRIPTS = [
    "common.sh",
    "check-prerequisites.sh",
    "create-new-feature.sh",
    "setup-plan.sh",
    "update-agent-context.sh",
]
```

**Location**: `src/doit_cli/services/template_manager.py`
**Purpose**: Defines the list of bash scripts to copy during initialization

## Method Signatures

### TemplateManager.copy_scripts()

```python
def copy_scripts(
    self,
    target_dir: Path,
    overwrite: bool = False,
) -> dict[str, list[Path]]:
    """Copy workflow scripts to target directory.

    Args:
        target_dir: Destination directory (typically .doit/scripts/bash/)
        overwrite: Whether to overwrite existing files

    Returns:
        Dict with 'created', 'updated', 'skipped' lists of paths
    """
```

## Return Value Structure

```python
{
    "created": [Path],   # Scripts that were newly created
    "updated": [Path],   # Scripts that were overwritten (when overwrite=True)
    "skipped": [Path],   # Scripts that existed and were not overwritten
}
```

## File System Structure

### Source (bundled in package)

```
templates/
└── scripts/
    └── bash/
        ├── common.sh
        ├── check-prerequisites.sh
        ├── create-new-feature.sh
        ├── setup-plan.sh
        └── update-agent-context.sh
```

### Target (created during init)

```
.doit/
└── scripts/
    └── bash/
        ├── common.sh              (mode 755)
        ├── check-prerequisites.sh (mode 755)
        ├── create-new-feature.sh  (mode 755)
        ├── setup-plan.sh          (mode 755)
        └── update-agent-context.sh (mode 755)
```

## Integration Points

### InitResult Model (existing)

The existing `InitResult` model tracks script copy results:

```python
@dataclass
class InitResult:
    success: bool
    project: Project
    created_directories: list[Path] = field(default_factory=list)
    created_files: list[Path] = field(default_factory=list)  # Scripts added here
    updated_files: list[Path] = field(default_factory=list)  # Scripts added here
    skipped_files: list[Path] = field(default_factory=list)  # Scripts added here
    error_message: str = ""
```

No changes to `InitResult` are required - scripts will be tracked in existing file lists.
