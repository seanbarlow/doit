# Quickstart: Doit CLI and Command Rename

## Overview

This feature renames the CLI tool from "Specify CLI" to "Doit CLI" and transforms slash commands to shorter, action-oriented names while preserving the `doit.` namespace.

## Command Reference

### Renamed Commands

| Old Command | New Command | Purpose |
|-------------|-------------|---------|
| `/doit.specify` | `/doit.specit` | Create feature specification |
| `/doit.plan` | `/doit.planit` | Generate implementation plan |
| `/doit.tasks` | `/doit.taskit` | Generate task breakdown |
| `/doit.implement` | `/doit.implementit` | Execute implementation |
| `/doit.test` | `/doit.testit` | Run automated tests |
| `/doit.review` | `/doit.reviewit` | Code review and manual testing |
| `/doit.scaffold` | `/doit.scaffoldit` | Generate project structure |

### Unchanged Commands

| Command | Purpose |
|---------|---------|
| `/doit.constitution` | Create/update project constitution |
| `/doit.checkin` | Finalize feature and create PR |

## Workflow Example

```bash
# Start a new feature (create spec)
/doit.specit Add user authentication with OAuth2

# Generate implementation plan
/doit.planit

# Generate task breakdown
/doit.taskit

# Implement the feature
/doit.implementit

# Run tests
/doit.testit

# Code review and manual testing
/doit.reviewit

# Finalize and create PR
/doit.checkin
```

## CLI Tool Usage

The CLI tool is now consistently branded as "Doit CLI":

```bash
# Initialize a new project
doit init my-project

# Initialize in current directory
doit init --here

# Get help
doit --help

# Show version info
doit info
```

## Migration Notes

- Old command names (`/doit.specify`, `/doit.plan`, etc.) will no longer work
- Existing projects using old command references in their local files will need manual updates
- The `doit.` namespace prefix is preserved to avoid conflicts with other tools

## Package Structure

After this feature, the Python package structure changes:

```text
src/
└── doit_cli/           # Renamed from specify_cli/
    └── __init__.py     # All "Specify CLI" refs → "Doit CLI"
```

## Testing the Changes

```bash
# Verify CLI branding
doit --help              # Should show "Doit CLI"
doit info                # Should show "Doit CLI Information"

# Verify package installation
pip install -e .
doit init --help         # Should work correctly
```
