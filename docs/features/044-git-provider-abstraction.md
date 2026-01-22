# Feature: Git Provider Abstraction Layer

**Spec**: [044-git-provider-abstraction](../../specs/044-git-provider-abstraction/spec.md)
**Status**: Implemented
**Completed**: 2026-01-22
**Branch**: `044-git-provider-abstraction`
**Version**: 0.2.0

## Overview

The Git Provider Abstraction Layer enables doit to work with multiple git hosting providers (GitHub, Azure DevOps, GitLab) through a unified interface. This allows CLI commands to remain provider-agnostic while supporting provider-specific behaviors through configuration.

## Supported Providers

| Provider | Status | Authentication |
|----------|--------|----------------|
| **GitHub** | ✅ Full | gh CLI (`gh auth login`) |
| **Azure DevOps** | ✅ Full | Personal Access Token |
| **GitLab** | ⚠️ Stub | Not yet implemented |

## Quick Start

### Configure Your Provider

```bash
# Auto-detect from git remote URL
doit provider configure --auto-detect

# Or explicitly select a provider
doit provider configure --provider github
doit provider configure --provider azure_devops -o myorg --project myproject
```

### Check Provider Status

```bash
doit provider status
```

### Provider Detection

The abstraction layer automatically detects your provider from the git remote URL:

| Remote URL Pattern | Detected Provider |
|--------------------|-------------------|
| `github.com/*` | GitHub |
| `ghe.*/*` | GitHub Enterprise |
| `dev.azure.com/*` | Azure DevOps |
| `*.visualstudio.com/*` | Azure DevOps |
| `gitlab.com/*` | GitLab |
| `gitlab.*/*` | GitLab (self-hosted) |

## Configuration

Provider configuration is stored in `.doit/config/provider.yaml`:

```yaml
# GitHub (default for github.com remotes)
provider: github
auto_detected: true
detection_source: git_remote
github:
  auth_method: gh_cli

# Azure DevOps
provider: azure_devops
auto_detected: false
azure_devops:
  organization: myorg
  project: myproject
  auth_method: pat
  api_version: "7.0"
```

## Authentication

### GitHub

GitHub authentication uses the `gh` CLI tool:

```bash
# Install gh CLI: https://cli.github.com
gh auth login
```

### Azure DevOps

Azure DevOps uses a Personal Access Token (PAT):

1. Go to Azure DevOps → User Settings → Personal Access Tokens
2. Create a token with Work Items and Code permissions
3. Set the environment variable:

```bash
export AZURE_DEVOPS_PAT="your-token-here"
```

### GitLab (Future)

GitLab will use an access token:

```bash
export GITLAB_TOKEN="your-token-here"
```

## Usage in Code

### Basic Usage

```python
from doit_cli.services.provider_factory import ProviderFactory
from doit_cli.models.provider_models import IssueCreateRequest

# Create provider (auto-detected or from config)
provider = ProviderFactory.create()

# Create an issue
issue = provider.create_issue(
    IssueCreateRequest(
        title="Bug: Login fails",
        body="Steps to reproduce...",
        labels=["bug", "priority:high"]
    )
)

print(f"Created issue: {issue.url}")
```

### Offline-Safe Usage

```python
from doit_cli.services.provider_factory import ProviderFactory

# Returns None if provider is unavailable
provider = ProviderFactory.create_safe()

if provider:
    issues = provider.list_issues()
else:
    print("Running in offline mode")
```

### Backward Compatibility

Existing code using `GitHubService` continues to work:

```python
from doit_cli.services.github_service import GitHubService

# Existing code works unchanged
service = GitHubService()
epics = service.fetch_epics()

# Or get the new provider for new operations
provider = service.get_provider()
```

## Provider Interface

All providers implement the `GitProvider` interface:

### Issue Operations

| Method | Description |
|--------|-------------|
| `create_issue(request)` | Create a new issue |
| `get_issue(id)` | Get issue by ID |
| `list_issues(filters)` | List issues with filters |
| `update_issue(id, updates)` | Update an issue |

### Pull Request Operations

| Method | Description |
|--------|-------------|
| `create_pull_request(request)` | Create a new PR/MR |
| `get_pull_request(id)` | Get PR by ID |
| `list_pull_requests(filters)` | List PRs with filters |

### Milestone Operations

| Method | Description |
|--------|-------------|
| `create_milestone(request)` | Create a new milestone |
| `get_milestone(id)` | Get milestone by ID |
| `list_milestones(state)` | List milestones |

## Data Models

### Issue

```python
@dataclass
class Issue:
    id: str              # Unified ID: github:issue:123
    provider_id: str     # Provider-specific: 123
    title: str
    body: str | None
    state: IssueState    # OPEN, CLOSED
    type: IssueType      # BUG, TASK, USER_STORY, FEATURE, EPIC
    labels: list[Label]
    url: str
    created_at: datetime
    updated_at: datetime
```

### PullRequest

```python
@dataclass
class PullRequest:
    id: str
    provider_id: str
    title: str
    body: str | None
    source_branch: str
    target_branch: str
    state: PRState       # OPEN, MERGED, CLOSED
    labels: list[Label]
    url: str
    created_at: datetime
    merged_at: datetime | None
```

### Milestone

```python
@dataclass
class Milestone:
    id: str
    provider_id: str
    title: str
    description: str | None
    state: MilestoneState  # OPEN, CLOSED
    due_date: datetime | None
    issue_count: int
    closed_issue_count: int
```

## Label Translation

Labels are translated between providers automatically:

| Unified Type | GitHub | Azure DevOps |
|--------------|--------|--------------|
| BUG | `bug` | Work Item Type: Bug |
| TASK | `task` | Work Item Type: Task |
| USER_STORY | `enhancement` | Work Item Type: User Story |
| FEATURE | `feature` | Work Item Type: Feature |
| EPIC | `epic` | Work Item Type: Epic |

## Error Handling

The abstraction layer provides consistent error handling:

```python
from doit_cli.services.providers.exceptions import (
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)

try:
    issue = provider.create_issue(request)
except AuthenticationError:
    print("Please authenticate with your provider")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ResourceNotFoundError as e:
    print(f"{e.resource_type} not found: {e.resource_id}")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
```

## Rate Limiting

For operations that may encounter rate limits, use the retry decorator:

```python
from doit_cli.services.providers.base import with_retry

@with_retry(max_retries=3, base_delay=1.0)
def fetch_all_issues():
    return provider.list_issues()
```

## Related Commands

- `doit provider configure` - Configure git provider
- `doit provider status` - Show provider status
- `doit provider detect` - Auto-detect provider
- `doit roadmapit add` - Create epics (uses provider)
- `doit roadmapit sync-milestones` - Sync milestones (uses provider)

## Troubleshooting

### "No git provider configured"

Run `doit provider configure` to set up your provider.

### "GitHub CLI not authenticated"

Run `gh auth login` to authenticate with GitHub.

### "AZURE_DEVOPS_PAT environment variable not set"

Set your Azure DevOps Personal Access Token:

```bash
export AZURE_DEVOPS_PAT="your-token-here"
```

### "GitLab provider does not support X yet"

GitLab support is planned for a future release. Use GitHub or Azure DevOps in the meantime.

## See Also

- [Specification](../../specs/044-git-provider-abstraction/spec.md)
- [Implementation Plan](../../specs/044-git-provider-abstraction/plan.md)
- [Data Model](../../specs/044-git-provider-abstraction/data-model.md)
