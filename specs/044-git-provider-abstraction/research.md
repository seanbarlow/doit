# Research: Git Provider Abstraction Layer

**Feature**: 044-git-provider-abstraction
**Date**: 2026-01-22
**Status**: Complete

## Design Decisions

### DD-001: Strategy Pattern for Provider Abstraction

**Decision**: Use the Strategy pattern where each git provider implements a common `GitProvider` interface.

**Rationale**:
- Enables runtime provider selection based on configuration
- Each provider can have custom implementation details while exposing a uniform API
- New providers can be added without modifying existing code
- Aligns with Python's Protocol/ABC patterns

**Alternatives Considered**:
1. **Adapter Pattern**: Wrap each provider's API in an adapter. Rejected because we need a clean abstraction, not compatibility with existing interfaces.
2. **Plugin Architecture**: Dynamic loading of provider modules. Rejected as over-engineering for 3 known providers.

### DD-002: Provider Detection via Git Remote URL

**Decision**: Auto-detect the git provider by parsing the remote URL pattern.

**Detection Patterns**:
| Provider | URL Patterns |
|----------|-------------|
| GitHub | `github.com`, `ghe.*/` (enterprise) |
| Azure DevOps | `dev.azure.com`, `*.visualstudio.com` |
| GitLab | `gitlab.com`, `gitlab.*/` (self-hosted) |

**Rationale**:
- Zero-configuration for most users
- Git remote is already configured in projects
- Fallback to explicit configuration when detection fails

### DD-003: Configuration Storage in YAML

**Decision**: Store provider configuration in `.doit/config/provider.yaml`.

**Structure**:
```yaml
provider: github  # or azure_devops, gitlab
auto_detected: true
detection_source: git_remote

github:
  auth_method: gh_cli  # or token

azure_devops:
  organization: myorg
  project: myproject
  auth_method: pat  # personal access token

gitlab:
  host: gitlab.com  # or self-hosted URL
  auth_method: token
```

**Rationale**:
- YAML is human-readable and editable
- Consistent with other doit configuration files
- Supports provider-specific settings without schema changes

### DD-004: GitHub Provider via gh CLI

**Decision**: Use the `gh` CLI for GitHub operations rather than direct REST API calls.

**Rationale**:
- `gh` handles authentication automatically
- Existing `github_service.py` already uses this approach
- Reduces authentication complexity for users
- Enterprise GitHub support comes for free

**Trade-offs**:
- Requires `gh` CLI to be installed
- Less control over API calls
- Error messages may be less precise

### DD-005: Azure DevOps Provider via REST API

**Decision**: Use Azure DevOps REST API directly with httpx.

**Rationale**:
- Azure CLI (`az`) is heavyweight and complex
- REST API is well-documented and stable
- PAT authentication is straightforward
- Enables fine-grained control over requests

**API Endpoints**:
```text
Work Items:  https://dev.azure.com/{org}/{project}/_apis/wit/workitems
Pull Requests: https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullrequests
Iterations: https://dev.azure.com/{org}/{project}/_apis/work/teamsettings/iterations
```

### DD-006: Unified Data Models

**Decision**: Create provider-agnostic data models that abstract provider-specific concepts.

**Mappings**:
| Unified Model | GitHub | Azure DevOps | GitLab |
|--------------|--------|--------------|--------|
| Issue | Issue | Work Item (Bug/Task/User Story) | Issue |
| PullRequest | Pull Request | Pull Request | Merge Request |
| Milestone | Milestone | Iteration/Sprint | Milestone |
| Label | Label | Tag | Label |

**Rationale**:
- CLI commands work identically regardless of provider
- Provider-specific details are encapsulated in provider implementations
- Users don't need to learn provider-specific terminology

### DD-007: Label/Tag Translation

**Decision**: Implement a translation layer for labels between providers.

**Approach**:
```python
class LabelMapper:
    def to_provider(self, label: str, provider: str) -> str:
        """Convert unified label to provider-specific format."""

    def from_provider(self, tag: str, provider: str) -> str:
        """Convert provider-specific tag to unified label."""
```

**Examples**:
- GitHub label `bug` → Azure DevOps work item type `Bug`
- Azure DevOps tag `P1` → unified priority label `priority:high`

### DD-008: Backward Compatibility Strategy

**Decision**: Maintain `GitHubService` as a facade that delegates to `GitHubProvider`.

**Implementation**:
```python
# github_service.py (existing interface)
class GitHubService:
    def __init__(self):
        self._provider = GitHubProvider()

    def create_issue(self, title, body, labels):
        return self._provider.create_issue(
            IssueCreateRequest(title=title, body=body, labels=labels)
        )
```

**Rationale**:
- Existing code continues to work without modification
- Gradual migration path for internal callers
- All existing tests remain valid

### DD-009: Error Handling Strategy

**Decision**: Define provider-agnostic exceptions that wrap provider-specific errors.

**Exception Hierarchy**:
```text
ProviderError (base)
├── AuthenticationError
├── RateLimitError
├── ResourceNotFoundError
├── ValidationError
└── NetworkError
```

**Rationale**:
- Callers handle errors uniformly
- Provider-specific details available via `.cause` attribute
- Enables consistent error messages across providers

### DD-010: GitLab as Stub Implementation

**Decision**: Implement GitLab provider as a stub that raises `NotImplementedError` with guidance.

**Implementation**:
```python
class GitLabProvider(GitProvider):
    def create_issue(self, request: IssueCreateRequest) -> Issue:
        raise NotImplementedError(
            "GitLab support is not yet implemented. "
            "See https://github.com/seanbarlow/doit/issues/XXX for status."
        )
```

**Rationale**:
- Establishes the interface for future implementation
- Clear feedback when GitLab is detected but not supported
- Allows testing of provider detection and configuration

## Open Questions (Resolved)

### OQ-001: Should we support multiple providers simultaneously?

**Resolution**: No. A project uses one provider at a time. The configuration stores a single active provider.

**Reasoning**: Multi-provider support adds complexity with little benefit. Users typically have one source control system per project.

### OQ-002: How to handle Azure DevOps work item types?

**Resolution**: Map to unified Issue model with a `type` field.

```python
@dataclass
class Issue:
    id: str
    title: str
    body: str
    type: IssueType  # BUG, TASK, USER_STORY, FEATURE
    labels: list[str]
```

### OQ-003: Authentication token storage?

**Resolution**: Defer to existing mechanisms:
- GitHub: `gh auth` manages credentials
- Azure DevOps: PAT stored in environment variable `AZURE_DEVOPS_PAT`
- GitLab: Token in environment variable `GITLAB_TOKEN`

No custom credential storage to avoid security concerns.

## References

- [Azure DevOps REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
- [GitHub CLI](https://cli.github.com/manual/)
- [GitLab API](https://docs.gitlab.com/ee/api/)
- [Python Protocol (PEP 544)](https://peps.python.org/pep-0544/)
