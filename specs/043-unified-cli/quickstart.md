# Quickstart: Unified CLI Package Migration

**Feature**: `043-unified-cli`
**Purpose**: Step-by-step guide to execute the package unification

## Prerequisites

- On branch `043-unified-cli`
- All tests passing before starting
- Clean git working directory

## Migration Steps

### Step 1: Verify Starting State

```bash
# Confirm branch
git branch --show-current
# Expected: 043-unified-cli

# Run tests to establish baseline
pytest

# Check current package structure
ls -la src/
# Should show: doit_cli/ and doit_toolkit_cli/
```

### Step 2: Create Utils Directory

```bash
mkdir -p src/doit_cli/utils
touch src/doit_cli/utils/__init__.py
```

### Step 3: Move Model Files

```bash
# Move 7 model files from toolkit to main package
mv src/doit_toolkit_cli/models/github_epic.py src/doit_cli/models/
mv src/doit_toolkit_cli/models/github_feature.py src/doit_cli/models/
mv src/doit_toolkit_cli/models/milestone.py src/doit_cli/models/
mv src/doit_toolkit_cli/models/priority.py src/doit_cli/models/
mv src/doit_toolkit_cli/models/roadmap.py src/doit_cli/models/
mv src/doit_toolkit_cli/models/sync_metadata.py src/doit_cli/models/
mv src/doit_toolkit_cli/models/sync_operation.py src/doit_cli/models/
```

### Step 4: Move Utility Files

```bash
# Move 4 utility files
mv src/doit_toolkit_cli/utils/fuzzy_match.py src/doit_cli/utils/
mv src/doit_toolkit_cli/utils/github_auth.py src/doit_cli/utils/
mv src/doit_toolkit_cli/utils/priority_mapper.py src/doit_cli/utils/
mv src/doit_toolkit_cli/utils/spec_parser.py src/doit_cli/utils/
```

### Step 5: Move Service Files

```bash
# Move 5 service files (excluding github_service.py which needs merge)
mv src/doit_toolkit_cli/services/github_cache_service.py src/doit_cli/services/
mv src/doit_toolkit_cli/services/github_linker.py src/doit_cli/services/
mv src/doit_toolkit_cli/services/milestone_service.py src/doit_cli/services/
mv src/doit_toolkit_cli/services/roadmap_matcher.py src/doit_cli/services/
mv src/doit_toolkit_cli/services/roadmap_merge_service.py src/doit_cli/services/
```

### Step 6: Merge github_service.py

This requires manual merging of the two files:

1. **Keep the existing** `src/doit_cli/services/github_service.py` as base
2. **Add from toolkit version**:
   - `GitHubAuthError` class
   - `GitHubAPIError` class
   - Epic/milestone methods: `fetch_epics`, `fetch_features_for_epic`, `create_epic`, `get_all_milestones`, `create_milestone`, `close_milestone`
   - `_get_repo_slug` helper method
   - `_ensure_authenticated` method

### Step 7: Move Command File

```bash
# Move and rename roadmapit command implementation
mv src/doit_toolkit_cli/commands/roadmapit.py src/doit_cli/cli/roadmapit_impl.py
```

### Step 8: Update Imports

Update all files that import from `doit_toolkit_cli`:

```bash
# Find all files with old imports
grep -r "from doit_toolkit_cli" src/ --include="*.py" -l
grep -r "from doit_toolkit_cli" tests/ --include="*.py" -l

# Replace imports in each file:
# from doit_toolkit_cli.models.X -> from doit_cli.models.X
# from doit_toolkit_cli.services.X -> from doit_cli.services.X
# from doit_toolkit_cli.utils.X -> from doit_cli.utils.X
# from doit_toolkit_cli.commands.roadmapit -> from doit_cli.cli.roadmapit_impl
```

### Step 9: Update roadmapit_command.py Wrapper

Edit `src/doit_cli/cli/roadmapit_command.py`:

```python
# Change from:
from doit_toolkit_cli.commands.roadmapit import app as roadmapit_app

# To:
from doit_cli.cli.roadmapit_impl import app as roadmapit_app
```

### Step 10: Update pyproject.toml

Edit `pyproject.toml`:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/doit_cli"]  # Remove doit_toolkit_cli
```

### Step 11: Delete Toolkit Package

```bash
# Remove the now-empty toolkit package
rm -rf src/doit_toolkit_cli/
```

### Step 12: Verify Migration

```bash
# Check no toolkit imports remain
grep -r "doit_toolkit_cli" src/ tests/
# Should return nothing

# Check package structure
ls src/
# Should only show: doit_cli

# Run tests
pytest

# Build package
hatch build

# Test CLI
pip install -e .
doit --help
```

## Rollback

If issues occur, rollback with:

```bash
git checkout -- .
git clean -fd
```

## Verification Checklist

- [ ] `src/` contains only `doit_cli/` directory
- [ ] No files reference `doit_toolkit_cli`
- [ ] All tests pass
- [ ] `hatch build` succeeds
- [ ] `doit --help` shows all commands
- [ ] `doit roadmapit show` works correctly
