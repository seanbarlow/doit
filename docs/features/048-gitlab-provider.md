# GitLab Git Provider Support

**Completed**: 2026-01-22
**Branch**: `048-gitlab-provider`
**PR**: Pending
**Epic**: [#637](https://github.com/seanbarlow/doit/issues/637)

## Overview

Full GitLab support in the doit CLI by implementing the GitLabProvider class. This enables teams using GitLab for source control to use all doit workflow features (issue creation, merge request management, milestone synchronization) with their GitLab repositories, whether using gitlab.com or self-hosted GitLab instances.

## Requirements Implemented

### Authentication & Configuration

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | PAT authentication support | Done |
| FR-002 | Token validation via `/api/v4/user` | Done |
| FR-003 | Self-hosted GitLab support | Done |
| FR-004 | Store host URL in config | Done |
| FR-005 | Token via env var or param | Done |

### Issue Management

| ID | Description | Status |
|----|-------------|--------|
| FR-010 | Create issues via POST | Done |
| FR-011 | Labels for type categorization | Done |
| FR-012 | Priority labels P1-P4 | Done |
| FR-013 | Query issues with filtering | Done |
| FR-014 | Update issues via PUT | Done |
| FR-015 | Close issues via state_event | Done |
| FR-016 | Issue relationships via links API | Done |

### Merge Request Management

| ID | Description | Status |
|----|-------------|--------|
| FR-020 | Create MRs via POST | Done |
| FR-021 | Specify branches and description | Done |
| FR-022 | Return MR web_url | Done |
| FR-023 | Query MRs via GET | Done |

### Milestone Management

| ID | Description | Status |
|----|-------------|--------|
| FR-030 | Create milestones via POST | Done |
| FR-031 | Update milestones via PUT | Done |
| FR-032 | Query milestones via GET | Done |
| FR-033 | Milestone state filtering | Done |
| FR-034 | Optional due_date support | Done |

### Error Handling

| ID | Description | Status |
|----|-------------|--------|
| FR-040 | Handle 401 with auth message | Done |
| FR-041 | Handle 403 with permissions message | Done |
| FR-042 | Handle 404 with not found message | Done |
| FR-043 | Handle 429 with retry-after | Done |
| FR-044 | Handle network timeouts | Done |

### Label Mapping

| ID | Description | Status |
|----|-------------|--------|
| FR-050 | Map EPIC to "Epic" label | Done |
| FR-051 | Map FEATURE to "Feature" label | Done |
| FR-052 | Map BUG to "Bug" label | Done |
| FR-053 | Map TASK to "Task" label | Done |
| FR-054 | Auto-create missing labels | Done |

## Technical Details

### Architecture

The implementation consists of three main classes:

1. **GitLabLabelMapper**: Maps between unified IssueType/priority and GitLab labels
   - Uses scoped labels for priorities (`priority::1`, `priority::2`, etc.)
   - Automatically creates labels with default colors

2. **GitLabAPIClient**: HTTP client wrapper for GitLab REST API v4
   - Handles authentication via `PRIVATE-TOKEN` header
   - Maps HTTP errors to domain exceptions
   - Supports both gitlab.com and self-hosted instances

3. **GitLabProvider**: Full implementation of GitProvider interface
   - All interface methods implemented
   - Retry decorator for transient failures
   - URL-encoded project paths for API calls

### Key Decisions

- **REST API v4**: Chose REST over GraphQL for broader compatibility
- **Scoped Labels**: Used `priority::N` syntax for mutual exclusion
- **Label-based Epics**: Uses "Epic" label instead of GitLab Premium Epics feature for free tier compatibility
- **PAT Only**: Personal Access Tokens only (no OAuth2) for simplicity

### Files Changed

| File | Description |
|------|-------------|
| `src/doit_cli/services/providers/gitlab.py` | Full GitLabProvider implementation (1035 lines) |
| `tests/unit/services/providers/test_gitlab.py` | Unit tests (45 tests) |
| `tests/integration/providers/test_gitlab_integration.py` | Integration test scaffolding |
| `tests/integration/providers/__init__.py` | Package init |

## Testing

### Automated Tests

| Suite | Tests | Status |
|-------|-------|--------|
| TestGitLabLabelMapper | 10 | Pass |
| TestGitLabAPIClient | 12 | Pass |
| TestGitLabProvider | 23 | Pass |
| **Total** | **45** | **100% Pass** |

### Requirement Coverage

- 29/30 requirements directly tested (97%)
- FR-016 (issue links) has implementation but no direct test

### Integration Tests

Integration tests require environment variables:
- `GITLAB_TOKEN`: Valid GitLab Personal Access Token
- `GITLAB_TEST_PROJECT`: Project path (e.g., `owner/repo`)

## Related Issues

- Epic: [#637](https://github.com/seanbarlow/doit/issues/637) - GitLab Git Provider Support
- Feature: [#638](https://github.com/seanbarlow/doit/issues/638) - Configure GitLab Provider
- Feature: [#639](https://github.com/seanbarlow/doit/issues/639) - Create GitLab Issues and Epics
- Feature: [#640](https://github.com/seanbarlow/doit/issues/640) - Query GitLab Issues
- Feature: [#641](https://github.com/seanbarlow/doit/issues/641) - Create GitLab Merge Requests

## Usage

### Configuration

```bash
# Set environment variable
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"

# Or use provider wizard
doit provider wizard
```

### Example Code

```python
from doit_cli.services.providers.gitlab import GitLabProvider
from doit_cli.models.provider_models import IssueCreateRequest, IssueType

# Initialize provider
provider = GitLabProvider(project_path="owner/repo")

# Check availability
if provider.is_available:
    # Create an issue
    issue = provider.create_issue(
        IssueCreateRequest(
            title="New feature request",
            body="Description here",
            type=IssueType.FEATURE,
            labels=["enhancement"]
        )
    )
    print(f"Created: {issue.url}")
```

---
Generated by `/doit.checkin` on 2026-01-22
