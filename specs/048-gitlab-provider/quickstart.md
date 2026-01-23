# Quickstart: GitLab Git Provider Support

**Feature**: 048-gitlab-provider
**Date**: 2026-01-22
**Status**: Implemented

## Overview

This guide helps developers use and extend the GitLabProvider for the doit CLI.

## Prerequisites

1. **Python 3.11+** installed
2. **doit CLI** development environment set up
3. **GitLab account** with a personal access token
4. **Git repository** with GitLab remote

## Setup

### 1. Create GitLab Personal Access Token

1. Go to GitLab → Settings → Access Tokens
2. Create a token with `api` scope
3. Export the token:

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
```

### 2. Configure doit for GitLab

```bash
doit provider wizard
# Select: GitLab
# Enter: Token (or use GITLAB_TOKEN env var)
# Confirm: Project path auto-detected from git remote
```

## Key Files

### Implementation

| File | Purpose |
| ---- | ------- |
| [gitlab.py](../../src/doit_cli/services/providers/gitlab.py) | Main GitLabProvider implementation |
| [base.py](../../src/doit_cli/services/providers/base.py) | GitProvider abstract interface |
| [exceptions.py](../../src/doit_cli/services/providers/exceptions.py) | Provider exceptions |
| [provider_models.py](../../src/doit_cli/models/provider_models.py) | Unified data models |

### Tests

| File | Purpose |
| ---- | ------- |
| [test_gitlab.py](../../tests/unit/services/providers/test_gitlab.py) | Unit tests with mocked API |
| [test_gitlab_integration.py](../../tests/integration/providers/test_gitlab_integration.py) | Integration tests |

## Usage Examples

### Initialize Provider

```python
from doit_cli.services.providers.gitlab import GitLabProvider

# Using environment variable for token
provider = GitLabProvider(project_path="owner/repo")

# With explicit token and self-hosted instance
provider = GitLabProvider(
    project_path="org/project",
    host="gitlab.mycompany.com",
    token="glpat-xxxxxxxxxxxx",
)

# Check availability
if provider.is_available:
    print("GitLab provider is configured and ready")
```

### Create Issues

```python
from doit_cli.models.provider_models import IssueCreateRequest, IssueType

# Create a feature issue
request = IssueCreateRequest(
    title="Add user authentication",
    body="Implement OAuth2 login flow",
    type=IssueType.FEATURE,
    labels=["backend", "security"],
)
issue = provider.create_issue(request)
print(f"Created issue: {issue.url}")

# Create an epic
epic_request = IssueCreateRequest(
    title="Q1 2026 Roadmap",
    body="High-level goals for Q1",
    type=IssueType.EPIC,
)
epic = provider.create_issue(epic_request)
```

### Query Issues

```python
from doit_cli.models.provider_models import IssueFilters, IssueState

# List open issues
filters = IssueFilters(state=IssueState.OPEN, limit=10)
issues = provider.list_issues(filters)
for issue in issues:
    print(f"#{issue.provider_id}: {issue.title}")

# Get specific issue
issue = provider.get_issue("42")
print(f"Issue state: {issue.state}")
```

### Create Merge Requests

```python
from doit_cli.models.provider_models import PRCreateRequest

request = PRCreateRequest(
    title="feat: add user authentication",
    body="Implements OAuth2 login flow\n\nCloses #42",
    source_branch="feature/auth",
    target_branch="main",
)
mr = provider.create_pull_request(request)
print(f"Created MR: {mr.url}")
```

### Manage Milestones

```python
from datetime import datetime, timedelta
from doit_cli.models.provider_models import MilestoneCreateRequest, MilestoneState

# Create milestone
request = MilestoneCreateRequest(
    title="v1.0.0",
    description="First stable release",
    due_date=datetime.now() + timedelta(days=30),
)
milestone = provider.create_milestone(request)

# List active milestones
milestones = provider.list_milestones(state=MilestoneState.OPEN)

# Close a milestone
provider.update_milestone(milestone.provider_id, state=MilestoneState.CLOSED)
```

## Architecture

### Class Structure

```
GitLabProvider
├── GitLabAPIClient      # HTTP client wrapper
│   ├── get()            # GET requests
│   ├── post()           # POST requests
│   ├── put()            # PUT requests
│   └── _handle_response() # Error handling
├── GitLabLabelMapper    # Label conversion
│   ├── to_gitlab_labels()
│   └── from_gitlab_labels()
└── Provider Methods
    ├── create_issue()
    ├── get_issue()
    ├── list_issues()
    ├── update_issue()
    ├── create_pull_request()
    ├── get_pull_request()
    ├── list_pull_requests()
    ├── create_milestone()
    ├── get_milestone()
    ├── list_milestones()
    └── update_milestone()
```

### Label Mapping

| Unified Type | GitLab Label |
| ------------ | ------------ |
| EPIC | `Epic` |
| FEATURE | `Feature` |
| BUG | `Bug` |
| TASK | `Task` |
| USER_STORY | `User Story` |

| Priority | GitLab Label |
| -------- | ------------ |
| P1 | `priority::1` |
| P2 | `priority::2` |
| P3 | `priority::3` |
| P4 | `priority::4` |

## Testing

### Run Unit Tests

```bash
pytest tests/unit/services/providers/test_gitlab.py -v
```

### Run with Live GitLab (Integration)

```bash
export GITLAB_TOKEN="your-token"
export GITLAB_TEST_PROJECT="owner/test-repo"
pytest tests/integration/providers/test_gitlab_integration.py -v
```

## Verification Checklist

- [x] `doit provider wizard` detects GitLab from remote URL
- [x] Token validation shows user info
- [x] `doit roadmapit add` creates epic in GitLab
- [x] `/doit.specit` creates feature issue with labels
- [x] `/doit.checkin` creates merge request
- [x] `doit roadmapit sync-milestones` creates milestones
- [x] Error messages are clear for auth failures
- [x] Self-hosted GitLab instances work with custom host

## Common Issues

### Token Scope Error

```
Error: Insufficient permissions for create_issue
```

**Fix**: Ensure token has `api` scope (not just `read_api`).

### Project Not Found

```
Error: Project owner/repo not found
```

**Fix**: Check project path matches GitLab exactly (case-sensitive).

### SSL Certificate Error (Self-Hosted)

```
Error: SSL certificate verify failed
```

**Fix**: Check SSL configuration or use truststore for custom CA.

## Resources

- [GitLab REST API Documentation](https://docs.gitlab.com/ee/api/rest/)
- [GitLab Issues API](https://docs.gitlab.com/ee/api/issues.html)
- [GitLab Merge Requests API](https://docs.gitlab.com/ee/api/merge_requests.html)
- [GitLab Milestones API](https://docs.gitlab.com/ee/api/milestones.html)
