# Developer Quickstart: GitHub Epic Integration

**Feature**: GitHub Epic and Issue Integration for Roadmap Command
**Target Audience**: Developers implementing or testing this feature
**Last Updated**: 2026-01-21

## Overview

This guide helps you set up, develop, test, and debug the GitHub epic integration for the roadmapit command.

## Prerequisites

### Required

- Python 3.11+
- Git repository with GitHub remote
- GitHub CLI (`gh`) installed and authenticated

### Optional

- Mock GitHub server for testing (we'll use pytest fixtures)

## Setup

### 1. Install GitHub CLI

**macOS**:
```bash
brew install gh
```

**Linux**:
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora/RHEL
sudo dnf install gh
```

**Windows**:
```bash
scoop install gh
# or
winget install GitHub.cli
```

Verify installation:
```bash
gh --version
# Output: gh version 2.40.0 (or higher)
```

### 2. Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate. Verify:
```bash
gh auth status
# Output: ✓ Logged in to github.com as <username>
```

### 3. Set Up Development Environment

Clone the doit repo:
```bash
git clone https://github.com/seanbarlow/doit.git
cd doit
```

Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:
```bash
pip install -e ".[dev]"
```

### 4. Verify GitHub Remote

Ensure your repo has a GitHub remote:
```bash
git remote get-url origin
# Output: https://github.com/owner/repo.git
```

## Development Workflow

### Running the Enhanced Roadmapit Command

After implementation, you'll be able to:

**Basic usage (with GitHub sync)**:
```bash
doit roadmapit
```

**Skip GitHub sync (offline mode)**:
```bash
doit roadmapit --skip-github
```

**Force refresh (bypass cache)**:
```bash
doit roadmapit --refresh
```

**Add item (creates GitHub epic)**:
```bash
doit roadmapit add "New feature X"
```

### Directory Structure

```
src/doit_toolkit_cli/
├── commands/
│   └── roadmapit.py          # Command entry point
├── services/
│   ├── github_service.py     # GitHub API interactions
│   ├── github_cache_service.py  # Cache management
│   └── roadmap_merge_service.py # Merge logic
├── models/
│   ├── github_epic.py        # Data models
│   └── sync_metadata.py
└── utils/
    ├── github_auth.py        # Auth detection
    └── priority_mapper.py    # Priority mapping

tests/
├── unit/
│   ├── test_github_service.py
│   ├── test_cache_service.py
│   └── test_merge_service.py
├── integration/
│   └── test_roadmapit_github.py
└── fixtures/
    └── github_responses.json  # Mock API responses
```

## Testing

### Unit Tests

Test individual services in isolation with mocked dependencies.

**Run all unit tests**:
```bash
pytest tests/unit/
```

**Run specific service tests**:
```bash
pytest tests/unit/test_github_service.py -v
```

**Example test structure**:
```python
# tests/unit/test_github_service.py
from unittest.mock import patch, MagicMock
import pytest
from doit_toolkit_cli.services.github_service import GitHubService

def test_fetch_epics_success():
    """Test fetching epics from GitHub successfully."""
    with patch('subprocess.run') as mock_run:
        # Mock gh CLI response
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 577, "title": "[Epic]: Test"}]'
        )

        service = GitHubService()
        epics = service.fetch_epics()

        assert len(epics) == 1
        assert epics[0].number == 577
        mock_run.assert_called_once()
```

### Integration Tests

Test the full workflow with mocked GitHub API.

**Run integration tests**:
```bash
pytest tests/integration/test_roadmapit_github.py -v
```

**Example integration test**:
```python
# tests/integration/test_roadmapit_github.py
from typer.testing import CliRunner
from doit_toolkit_cli.cli import app

runner = CliRunner()

def test_roadmapit_with_github_sync(mock_github_api, tmp_path):
    """Test roadmapit command with GitHub sync enabled."""
    # Setup: Create mock roadmap file
    roadmap_path = tmp_path / ".doit/memory/roadmap.md"
    roadmap_path.parent.mkdir(parents=True)
    roadmap_path.write_text("# Roadmap\n\n## P1\n- Local item")

    # Execute
    result = runner.invoke(app, ["roadmapit"])

    # Verify
    assert result.exit_code == 0
    assert "Local item" in result.stdout
    assert "577" in result.stdout  # GitHub epic number from mock
```

### Manual Testing

#### Test Scenario 1: Fetch and Display Epics

**Setup**:
1. Create test GitHub repo with sample issues
2. Label some issues as "epic" with priority labels

**Execute**:
```bash
doit roadmapit
```

**Verify**:
- All open epics appear in roadmap
- Priorities are correctly mapped
- Local items are preserved

#### Test Scenario 2: Offline Mode with Cache

**Setup**:
1. Run `doit roadmapit` to populate cache
2. Disconnect from internet

**Execute**:
```bash
doit roadmapit
```

**Verify**:
- Command succeeds using cached data
- Warning message indicates using cache
- All epics from cache are displayed

#### Test Scenario 3: Create GitHub Epic

**Setup**:
1. Ensure GitHub authentication is working

**Execute**:
```bash
doit roadmapit add "New dashboard feature"
# When prompted, select priority P2
```

**Verify**:
1. Check `.doit/memory/roadmap.md` - item added
2. Check GitHub issues - epic created with correct labels
3. Run `doit roadmapit` - see the synced item

## Debugging

### Enable Debug Logging

```python
# In your code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

#### Issue: `gh: command not found`

**Solution**: Install GitHub CLI (see Prerequisites)

#### Issue: `Not authenticated with GitHub`

**Solution**:
```bash
gh auth login
```

#### Issue: `Rate limit exceeded`

**Solution**:
- Wait for rate limit reset (check with `gh api rate_limit`)
- Use `--skip-github` to work offline
- Use cached data (default behavior)

#### Issue: Cache not updating

**Solution**:
```bash
# Force refresh
doit roadmapit --refresh

# Or delete cache manually
rm .doit/cache/github_epics.json
```

#### Issue: Epics not appearing

**Debug steps**:
1. Check if epics have "epic" label:
   ```bash
   gh issue list --label epic
   ```

2. Check if gh CLI works:
   ```bash
   gh issue list --json number,title
   ```

3. Check cache file:
   ```bash
   cat .doit/cache/github_epics.json | jq .
   ```

### Inspecting Cache

View cached epics:
```bash
cat .doit/cache/github_epics.json | jq '.epics[] | {number, title, labels}'
```

Check cache age:
```bash
cat .doit/cache/github_epics.json | jq '.metadata.last_sync'
```

## Development Tips

### Mock GitHub CLI in Tests

Use `pytest` fixtures to mock subprocess calls:

```python
@pytest.fixture
def mock_gh_cli(monkeypatch):
    """Mock gh CLI subprocess calls."""
    def mock_run(cmd, **kwargs):
        if "issue list" in " ".join(cmd):
            return MagicMock(
                returncode=0,
                stdout='[{"number": 577, "title": "Test Epic"}]'
            )
        return MagicMock(returncode=0, stdout='')

    monkeypatch.setattr('subprocess.run', mock_run)
```

### Test with Different GitHub States

Create fixture files for various scenarios:

```python
# tests/fixtures/github_responses.json
{
  "epics_with_features": [...],
  "epics_no_priority": [...],
  "empty_repo": [],
  "rate_limit_error": {"error": "rate limit exceeded"}
}
```

### Performance Profiling

Profile cache vs API performance:

```bash
# With cache
time doit roadmapit

# Without cache (fresh API call)
rm .doit/cache/github_epics.json
time doit roadmapit --refresh
```

Target: <5 seconds for 50 epics with fresh API call

## Example Workflows

### Workflow 1: Daily Development

```bash
# Morning: Check roadmap with latest GitHub data
doit roadmapit --refresh

# Add new feature idea
doit roadmapit add "Feature X"

# Work on code...

# Evening: Review updated roadmap
doit roadmapit
```

### Workflow 2: Offline Development

```bash
# Before going offline: sync
doit roadmapit --refresh

# While offline: use cache
doit roadmapit

# Add local item (won't create GitHub epic until online)
doit roadmapit add "Feature Y"
```

### Workflow 3: Team Sync

```bash
# Pull latest from team
git pull

# Sync roadmap with GitHub
doit roadmapit --refresh

# Review team's epics
doit roadmapit

# Add your feature
doit roadmapit add "My feature"
```

## API Reference

### GitHub Service

```python
from doit_toolkit_cli.services.github_service import GitHubService

service = GitHubService()

# Fetch all open epics
epics = service.fetch_epics()

# Fetch features for an epic
features = service.fetch_features_for_epic(epic_number=577)

# Create new epic
epic = service.create_epic(
    title="New Feature",
    priority="P2",
    body="Description..."
)
```

### Cache Service

```python
from doit_toolkit_cli.services.github_cache_service import GitHubCacheService

cache = GitHubCacheService()

# Check if cache is valid
if cache.is_valid():
    epics = cache.load_epics()
else:
    epics = fetch_from_github()
    cache.save_epics(epics)
```

### Priority Mapper

```python
from doit_toolkit_cli.utils.priority_mapper import map_labels_to_priority

labels = ["epic", "priority:P2", "enhancement"]
priority = map_labels_to_priority(labels)
# Returns: "P2"

labels = ["epic"]  # No priority label
priority = map_labels_to_priority(labels)
# Returns: "P3" (default)
```

## Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub REST API Docs](https://docs.github.com/en/rest)
- [pytest Documentation](https://docs.pytest.org/)
- [Feature Spec](spec.md)
- [Implementation Plan](plan.md)
- [Data Model](data-model.md)

## Next Steps

After completing development:

1. Run full test suite: `pytest tests/`
2. Check code coverage: `pytest --cov=doit_toolkit_cli tests/`
3. Run linter: `ruff check .`
4. Update documentation if API changed
5. Run `/doit.reviewit` for code review
6. Run `/doit.testit` for automated testing
7. Run `/doit.checkin` to complete the feature
