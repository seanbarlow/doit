# Research: Git Provider Configuration Wizard

**Branch**: `047-provider-config-wizard` | **Date**: 2026-01-22 | **Spec**: [spec.md](spec.md)

## Phase 0: Codebase Analysis

### Existing Provider Architecture

#### Provider Abstraction Layer

The doit CLI uses a well-structured provider abstraction layer:

1. **ProviderFactory** (`src/doit_cli/services/provider_factory.py`)
   - Factory pattern for instantiating providers
   - Auto-detection from git remote URL
   - `detect_provider()` analyzes remote for `github.com`, `dev.azure.com`, `gitlab` patterns
   - `is_provider_available()` checks authentication status
   - `is_offline()` performs network connectivity check

2. **Base Interface** (`src/doit_cli/services/providers/base.py`)
   - `GitProvider` abstract class with standardized methods
   - `is_available` property for authentication/connection status
   - `_ensure_authenticated()` pattern for pre-operation validation
   - `with_retry()` decorator for transient failure handling

3. **Provider Implementations**
   - **GitHub** (`providers/github.py`): Uses `gh` CLI tool, checks `gh auth status`
   - **Azure DevOps** (`providers/azure_devops.py`): Direct REST API with httpx, PAT authentication
   - **GitLab** (`providers/gitlab.py`): Stub implementation, raises `ProviderNotImplementedError`

#### Configuration Storage

Current configuration stored in `.doit/config/provider.yaml`:

```yaml
provider: github
auto_detected: true
detection_source: git_remote
github:
  auth_method: gh_cli
  enterprise_host: null  # for GHE
```

Configuration classes (`src/doit_cli/services/provider_config.py`):
- `ProviderConfig` - main config with `load()` and `save()` methods
- `GitHubConfig` - auth_method, enterprise_host
- `AzureDevOpsConfig` - organization, project, auth_method, api_version
- `GitLabConfig` - host, auth_method

#### Existing CLI Commands

The `doit provider` command group (`src/doit_cli/cli/provider_command.py`):

1. **configure** - Basic configuration with auto-detect or manual selection
   - Uses `typer.prompt()` for interactive input
   - No validation of credentials before saving
   - No progress indicators or wizard flow

2. **status** - Shows current configuration and availability
3. **detect** - Reports detected provider without saving

### Gap Analysis: Current vs. Required

| Requirement | Current State | Gap |
|-------------|--------------|-----|
| Step-by-step wizard | Basic prompts | Need wizard state machine |
| Credential validation | None before save | Need validation before save |
| Connection testing | Only in `status` command | Need inline during wizard |
| Progress indicators | None | Need Rich progress UI |
| Back navigation | Not supported | Need step navigation |
| Graceful cancellation | Not supported | Need state preservation |
| Configuration backup | Not supported | Need backup on reconfigure |
| GitHub Enterprise | Config exists, no prompt | Need host configuration step |
| Azure DevOps scopes | Not validated | Need PAT scope validation |

### Libraries for Interactive Wizard

**Currently Available:**
- `Rich` - Already used for terminal formatting (Panel, Table, Console)
- `readchar` - Already in dependencies for keyboard input
- `Typer` - CLI framework with `typer.prompt()` and `typer.confirm()`

**Rich Features to Leverage:**
- `Prompt` - Enhanced input prompts with validation
- `Progress` - Progress indicators for connection testing
- `Panel` - Step containers and summaries
- `Status` - Spinner for async operations
- `Text` - Styled text for instructions

**No Additional Dependencies Required.**

### Authentication Testing Methods

#### GitHub
```python
# Current: gh auth status
result = subprocess.run(["gh", "auth", "status"], capture_output=True)
is_authenticated = result.returncode == 0
```
Extension needed:
- Check gh CLI installation (`which gh`)
- Parse auth status for username/scope info
- Test repository access with `gh api user`

#### Azure DevOps
```python
# Current: Test project endpoint
response = client.get(f"https://dev.azure.com/{org}/{project}/_apis/project")
is_authenticated = response.status_code == 200
```
Extension needed:
- Validate PAT has required scopes (Code, Work Items)
- Test with `/_apis/projects` for organization access
- Provide specific error for 401 (invalid PAT) vs 403 (missing scopes)

#### GitLab
```python
# Not implemented, but pattern would be:
headers = {"PRIVATE-TOKEN": token}
response = client.get(f"https://{host}/api/v4/user", headers=headers)
is_authenticated = response.status_code == 200
```

### Wizard State Machine Design

Recommended pattern using a state-driven wizard:

```python
class WizardState(Enum):
    DETECT_PROVIDER = "detect"
    SELECT_PROVIDER = "select"
    GITHUB_AUTH = "github_auth"
    GITHUB_ENTERPRISE = "github_enterprise"
    ADO_ORGANIZATION = "ado_organization"
    ADO_PROJECT = "ado_project"
    ADO_PAT = "ado_pat"
    GITLAB_HOST = "gitlab_host"
    GITLAB_TOKEN = "gitlab_token"
    VALIDATE = "validate"
    CONFIRM = "confirm"
    COMPLETE = "complete"
```

Each step:
1. Displays current state and instructions
2. Collects input with validation
3. Allows back navigation or cancellation
4. Transitions to next state on success

### Integration Points

1. **Entry Point**: Add `wizard` subcommand to `provider_command.py`
2. **Configuration**: Extend `ProviderConfig` with backup mechanism
3. **Validation**: Create dedicated validation service
4. **UI Components**: Leverage existing Rich console patterns

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| gh CLI not installed | Medium | High | Provide clear install instructions with links |
| PAT scope insufficient | High | Medium | Test specific endpoints, suggest required scopes |
| Network timeout during validation | Medium | Low | Allow save without validation with warning |
| User cancels mid-wizard | High | Low | No partial saves, restore previous config |
| GHE/self-hosted auth differs | Low | Medium | Test enterprise endpoint patterns |

### Recommendations

1. **Create `WizardService`** in `src/doit_cli/services/wizard_service.py`
   - State machine for wizard flow
   - Provider-specific step sequences
   - Validation orchestration

2. **Create `ValidationService`** in `src/doit_cli/services/validation_service.py`
   - Authentication testing methods per provider
   - Scope validation for Azure DevOps PAT
   - Connection testing with timeout

3. **Extend `ProviderConfig`** with:
   - `create_backup()` method for reconfiguration
   - `validated_at` timestamp field
   - History tracking in separate file

4. **Use Rich components** for UI:
   - `Panel` for each wizard step
   - `Prompt.ask()` for validated input
   - `Status()` spinner for validation
   - `Table` for configuration summary

## References

- [provider_factory.py:78-116](../../src/doit_cli/services/provider_factory.py#L78-L116) - Detection logic
- [github.py:99-110](../../src/doit_cli/services/providers/github.py#L99-L110) - GitHub availability check
- [azure_devops.py:571-587](../../src/doit_cli/services/providers/azure_devops.py#L571-L587) - ADO authentication
- [provider_config.py:128-172](../../src/doit_cli/services/provider_config.py#L128-L172) - Configuration save
