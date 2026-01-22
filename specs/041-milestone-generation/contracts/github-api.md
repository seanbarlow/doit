# GitHub API Contract: Milestone Operations

**Feature**: 041-milestone-generation
**Date**: 2026-01-22
**API Version**: GitHub REST API v3

## Overview

This document specifies the GitHub API endpoints used for milestone creation, assignment, and management via the `gh` CLI tool.

## Authentication

All API calls use GitHub CLI authentication:

```bash
# User must be authenticated before sync
gh auth status

# If not authenticated
gh auth login
```

**Requirements**:
- User MUST have push access to repository
- `gh` CLI MUST be version 2.0+
- Repository MUST be on GitHub (not GitLab/Bitbucket)

## Base URL Pattern

```
https://api.github.com/repos/{owner}/{repo}
```

**Example**: `https://api.github.com/repos/anthropics/doit`

## API Endpoints

### 1. List Milestones

Retrieve all milestones for a repository.

**Endpoint**: `GET /repos/{owner}/{repo}/milestones`

**CLI Command**:
```bash
gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | {number, title, state, description, open_issues, closed_issues}'
```

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `state` | string | No | Filter by state: "open", "closed", "all" (default: "open") |
| `sort` | string | No | Sort by: "due_on", "completeness" (default: "due_on") |
| `direction` | string | No | Sort direction: "asc", "desc" (default: "asc") |
| `per_page` | integer | No | Results per page (default: 30, max: 100) |

**Response** (200 OK):
```json
[
  {
    "number": 1,
    "title": "P1 - Critical",
    "description": "Auto-managed by doit. Contains all P1 - Critical roadmap items.",
    "state": "open",
    "open_issues": 5,
    "closed_issues": 12,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-22T14:20:00Z",
    "due_on": null,
    "html_url": "https://github.com/anthropics/doit/milestone/1"
  },
  {
    "number": 2,
    "title": "P2 - High Priority",
    "description": "Auto-managed by doit. Contains all P2 - High Priority roadmap items.",
    "state": "open",
    "open_issues": 3,
    "closed_issues": 8,
    "created_at": "2026-01-15T10:31:00Z",
    "updated_at": "2026-01-22T09:15:00Z",
    "due_on": null,
    "html_url": "https://github.com/anthropics/doit/milestone/2"
  }
]
```

**Error Responses**:
- `404 Not Found`: Repository does not exist or user lacks access
- `403 Forbidden`: User lacks read permission

**Usage**:
```python
def get_all_milestones(repo_slug: str) -> list[dict]:
    """Get all open milestones for repository."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo_slug}/milestones", "--jq", "."],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)
```

---

### 2. Create Milestone

Create a new milestone in the repository.

**Endpoint**: `POST /repos/{owner}/{repo}/milestones`

**CLI Command**:
```bash
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  --field title="P3 - Medium Priority" \
  --field description="Auto-managed by doit. Contains all P3 - Medium Priority roadmap items." \
  --field state="open"
```

**Request Body**:
```json
{
  "title": "P3 - Medium Priority",
  "description": "Auto-managed by doit. Contains all P3 - Medium Priority roadmap items.",
  "state": "open",
  "due_on": null
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Milestone title (unique within repo) |
| `description` | string | No | Milestone description |
| `state` | string | No | "open" or "closed" (default: "open") |
| `due_on` | string | No | ISO 8601 timestamp for due date |

**Response** (201 Created):
```json
{
  "number": 7,
  "title": "P3 - Medium Priority",
  "description": "Auto-managed by doit. Contains all P3 - Medium Priority roadmap items.",
  "state": "open",
  "open_issues": 0,
  "closed_issues": 0,
  "created_at": "2026-01-22T14:30:00Z",
  "updated_at": "2026-01-22T14:30:00Z",
  "due_on": null,
  "html_url": "https://github.com/anthropics/doit/milestone/7"
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Milestone with same title already exists
- `403 Forbidden`: User lacks write permission
- `404 Not Found`: Repository does not exist

**Usage**:
```python
def create_milestone(repo_slug: str, title: str, description: str) -> int:
    """Create milestone and return its number."""
    result = subprocess.run(
        [
            "gh", "api", f"repos/{repo_slug}/milestones",
            "--method", "POST",
            "--field", f"title={title}",
            "--field", f"description={description}",
            "--field", "state=open",
            "--jq", ".number"
        ],
        capture_output=True,
        text=True,
        check=True
    )
    return int(result.stdout.strip())
```

---

### 3. Update Milestone

Update an existing milestone's state or description.

**Endpoint**: `PATCH /repos/{owner}/{repo}/milestones/{milestone_number}`

**CLI Command**:
```bash
gh api repos/{owner}/{repo}/milestones/7 \
  --method PATCH \
  --field state="closed"
```

**Request Body**:
```json
{
  "state": "closed"
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | Update milestone title |
| `description` | string | No | Update milestone description |
| `state` | string | No | Update state: "open" or "closed" |
| `due_on` | string | No | Update due date (ISO 8601) |

**Response** (200 OK):
```json
{
  "number": 7,
  "title": "P3 - Medium Priority",
  "description": "Auto-managed by doit. Contains all P3 - Medium Priority roadmap items.",
  "state": "closed",
  "open_issues": 0,
  "closed_issues": 15,
  "created_at": "2026-01-22T14:30:00Z",
  "updated_at": "2026-01-22T16:45:00Z",
  "closed_at": "2026-01-22T16:45:00Z",
  "due_on": null,
  "html_url": "https://github.com/anthropics/doit/milestone/7"
}
```

**Error Responses**:
- `404 Not Found`: Milestone does not exist
- `403 Forbidden`: User lacks write permission

**Usage**:
```python
def close_milestone(repo_slug: str, milestone_number: int) -> None:
    """Close a milestone."""
    subprocess.run(
        [
            "gh", "api", f"repos/{repo_slug}/milestones/{milestone_number}",
            "--method", "PATCH",
            "--field", "state=closed"
        ],
        check=True
    )
```

---

### 4. Get Issue Details

Retrieve issue details including current milestone assignment.

**Endpoint**: `GET /repos/{owner}/{repo}/issues/{issue_number}`

**CLI Command**:
```bash
gh issue view {issue_number} --json milestone,title,state
```

**Response** (200 OK):
```json
{
  "number": 587,
  "title": "GitHub Issue Auto-linking in Spec Creation",
  "state": "closed",
  "milestone": {
    "number": 2,
    "title": "P2 - High Priority",
    "description": "Auto-managed by doit. Contains all P2 - High Priority roadmap items.",
    "state": "open"
  }
}
```

**Response** (when no milestone assigned):
```json
{
  "number": 595,
  "title": "New Feature Request",
  "state": "open",
  "milestone": null
}
```

**Error Responses**:
- `404 Not Found`: Issue does not exist
- `403 Forbidden`: User lacks read permission

**Usage**:
```python
def get_issue_milestone(issue_number: int) -> Optional[str]:
    """Get current milestone title for issue."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number), "--json", "milestone"],
        capture_output=True,
        text=True,
        check=True
    )
    data = json.loads(result.stdout)
    return data["milestone"]["title"] if data["milestone"] else None
```

---

### 5. Assign Issue to Milestone

Assign or reassign an issue to a milestone.

**Endpoint**: `PATCH /repos/{owner}/{repo}/issues/{issue_number}`

**CLI Command**:
```bash
gh issue edit {issue_number} --milestone "P1 - Critical"
```

**Simplified Interface**:
The `gh issue edit` command wraps the API call and handles:
- Finding milestone by title
- Updating issue with milestone number
- Error handling for non-existent milestones

**Equivalent API Call**:
```bash
# First, get milestone number by title
MILESTONE_NUM=$(gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | select(.title == "P1 - Critical") | .number')

# Then, assign issue to milestone
gh api repos/{owner}/{repo}/issues/{issue_number} \
  --method PATCH \
  --field milestone=${MILESTONE_NUM}
```

**Response** (200 OK):
```json
{
  "number": 587,
  "title": "GitHub Issue Auto-linking in Spec Creation",
  "state": "closed",
  "milestone": {
    "number": 1,
    "title": "P1 - Critical"
  }
}
```

**Error Responses**:
- `404 Not Found`: Issue or milestone does not exist
- `403 Forbidden`: User lacks write permission
- `422 Unprocessable Entity`: Milestone title not found

**Usage**:
```python
def assign_issue_to_milestone(issue_number: int, milestone_title: str) -> None:
    """Assign issue to milestone by title."""
    subprocess.run(
        [
            "gh", "issue", "edit", str(issue_number),
            "--milestone", milestone_title
        ],
        check=True
    )
```

---

## Rate Limiting

**Primary Rate Limit**: 5,000 requests/hour (authenticated)

**Rate Limit Headers** (returned in all responses):
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4850
X-RateLimit-Reset: 1642867200
```

**Handling Rate Limits**:

```python
def handle_rate_limit(func):
    """Decorator to handle rate limit errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            if "rate limit" in e.stderr.lower():
                # Get reset time from error message
                reset_time = parse_rate_limit_reset(e.stderr)
                wait_seconds = reset_time - time.time()
                logger.warning(f"Rate limited. Waiting {wait_seconds}s...")
                time.sleep(wait_seconds)
                return func(*args, **kwargs)
            raise
    return wrapper
```

**Optimization Strategy**:
- Batch milestone list query (1 call per sync)
- Only assign epics that changed (skip if already assigned)
- Use conditional requests with `If-None-Match` headers

---

## Error Handling

### Common Error Codes

| Code | Meaning | Handling Strategy |
|------|---------|-------------------|
| `200` | OK | Success, parse response |
| `201` | Created | Success, extract created resource |
| `304` | Not Modified | Use cached data |
| `401` | Unauthorized | Prompt user to run `gh auth login` |
| `403` | Forbidden | Check user permissions, exit with error |
| `404` | Not Found | Resource doesn't exist, skip or create |
| `422` | Unprocessable | Validation error (duplicate title), skip |
| `500` | Server Error | Retry with exponential backoff |
| `502`/`503` | Service Unavailable | Retry with exponential backoff |

### Example Error Response

```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "resource": "Milestone",
      "code": "already_exists",
      "field": "title"
    }
  ],
  "documentation_url": "https://docs.github.com/rest/issues/milestones#create-a-milestone"
}
```

### Retry Strategy

```python
def retry_on_server_error(max_retries=3):
    """Retry decorator for server errors (500, 502, 503)."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except subprocess.CalledProcessError as e:
                    if attempt == max_retries - 1:
                        raise
                    if "500" in e.stderr or "502" in e.stderr or "503" in e.stderr:
                        wait = 2 ** attempt  # Exponential backoff
                        time.sleep(wait)
                        continue
                    raise
        return wrapper
    return decorator
```

---

## Testing

### Unit Test Mocking

Use `unittest.mock` to mock `subprocess.run` calls:

```python
@patch('subprocess.run')
def test_create_milestone(mock_run):
    """Test milestone creation."""
    mock_run.return_value = Mock(
        stdout='{"number": 7, "title": "P3 - Medium Priority"}',
        returncode=0
    )

    milestone_num = create_milestone("owner/repo", "P3 - Medium Priority", "Description")

    assert milestone_num == 7
    mock_run.assert_called_once_with(
        ["gh", "api", "repos/owner/repo/milestones", "--method", "POST", ...],
        capture_output=True,
        text=True,
        check=True
    )
```

### Integration Test Strategy

Use VCR.py or similar to record/replay real GitHub API responses:

```python
import vcr

@vcr.use_cassette('fixtures/list_milestones.yaml')
def test_list_milestones_real_api():
    """Test against recorded real API response."""
    milestones = get_all_milestones("test/repo")
    assert len(milestones) > 0
    assert milestones[0]["title"] == "P1 - Critical"
```

---

## API Reference

**Official Documentation**:
- [GitHub Milestones API](https://docs.github.com/en/rest/issues/milestones)
- [GitHub Issues API](https://docs.github.com/en/rest/issues/issues)
- [GitHub CLI Manual](https://cli.github.com/manual/)

**CLI Command Reference**:
```bash
gh api --help          # API command help
gh issue edit --help   # Issue edit help
gh auth status         # Check authentication
```

---

## Security Considerations

1. **Authentication**: Never commit GitHub tokens. Use `gh auth` for authentication.
2. **Permissions**: User must have `write` access to repository for milestone creation.
3. **Rate Limiting**: Implement backoff to avoid hitting limits during bulk operations.
4. **Input Validation**: Sanitize user input before passing to API (prevent injection).
5. **Error Messages**: Don't expose internal details in error messages shown to users.

---

## Performance Benchmarks

**Expected API Call Latency** (authenticated, good network):
- List milestones: 200-500ms
- Create milestone: 300-600ms
- Assign issue: 200-400ms

**Total Sync Time Estimate** (50 items, 4 priorities):
- List milestones: 1 × 500ms = 0.5s
- Create missing milestones: 2 × 600ms = 1.2s
- Assign epics: 25 × 400ms = 10s
- **Total**: ~12 seconds

**Optimization**: Use concurrent requests (asyncio) to reduce latency (future enhancement).
