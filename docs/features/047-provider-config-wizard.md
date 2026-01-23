# Git Provider Configuration Wizard

**Completed**: 2026-01-22
**Branch**: 047-provider-config-wizard
**Priority**: P3 - Medium Priority
**Epic**: [#607](https://github.com/seanbarlow/doit/issues/607)

## Overview

Interactive step-by-step wizard for configuring git provider authentication. Guides users through setting up GitHub (via gh CLI), Azure DevOps (via PAT), or GitLab (via token) with credential validation, connectivity testing, and configuration backup/restore capabilities.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | `doit provider wizard` command launches interactive wizard | Done |
| FR-002 | Auto-detect provider from git remote URL | Done |
| FR-003 | Step-by-step configuration with progress indicators | Done |
| FR-004 | Validate credentials before saving | Done |
| FR-005 | Test connectivity to provider API | Done |
| FR-006 | Progress indicators during validation | Done |
| FR-007 | Back navigation between steps | Partial (forward-only in v1) |
| FR-008 | Save configuration only on completion | Done |
| FR-009 | Preserve existing config as backup before changes | Done |
| FR-010 | Handle cancellation gracefully with config restoration | Done |
| FR-011 | Clear error messages with actionable suggestions | Done |
| FR-012 | Provider-specific authentication instructions | Done |
| FR-020-023 | GitHub: gh CLI detection, auth status, GHE support | Done |
| FR-030-035 | Azure DevOps: org/project prompts, PAT validation, scope detection | Done |
| FR-040-042 | GitLab: host/token prompts, limited support warning | Done |

## User Stories

### US1: First-Time GitHub Setup (P1 - MVP)
When a developer runs `doit provider wizard` with a GitHub remote, the wizard detects GitHub, validates gh CLI authentication, and saves the configuration.

**Test Command**: `doit provider wizard` in a GitHub repo

### US2: Azure DevOps Configuration (P1)
Developers can configure Azure DevOps with organization, project, and PAT. The wizard validates PAT scopes and tests project access.

**Test Command**: `doit provider wizard` in an Azure DevOps repo

### US3: Provider Switching (P2)
When reconfiguring from one provider to another, the wizard creates a backup of the existing configuration that can be restored.

**Test Command**: Run wizard on project with existing config, switch provider

### US4: GitLab Configuration (P3)
Developers can configure GitLab with host and token, with clear messaging about current limited support status.

**Test Command**: `doit provider wizard` in a GitLab repo

## Technical Details

### Architecture

**Service Layer**:
- `ProviderValidationService` - Validates credentials and connectivity for each provider
- `ConfigBackupService` - Manages configuration backups with create/list/restore/prune
- `WizardService` - Orchestrates the wizard flow with Rich UI components

**Models** (`wizard_models.py`):
- `WizardStep` - Enum for wizard steps (DETECT, SELECT, CONFIGURE, VALIDATE, SUMMARY)
- `WizardState` - Dataclass tracking current wizard state
- `ValidationResult` - Result of validation with success/error/suggestion
- `WizardResult` - Final wizard outcome with config or cancellation
- `ConfigBackup` - Backup entry with backup_id, timestamp, reason, config_data

**Exceptions**:
- `WizardCancelledError` - User cancelled the wizard
- `WizardStepError` - A wizard step failed with suggestion
- `BackupNotFoundError` - Requested backup doesn't exist

### Key Decisions

1. **gh CLI for GitHub**: Uses `gh auth status` instead of direct API to leverage existing auth
2. **Backup ID Format**: `YYYYMMDD_HHMMSS_ffffff` with microseconds for uniqueness
3. **Max Backups**: Keeps 5 most recent backups, prunes older ones automatically
4. **Forward-Only Flow**: Back navigation deferred to future iteration
5. **Rich UI**: Uses Panel for steps, Status for spinners, Table for summary
6. **PAT Environment Variable**: Azure DevOps supports `AZURE_DEVOPS_PAT` env var

### Provider Detection

```python
# From git remote URL
github.com or ghe. -> GitHub
dev.azure.com or visualstudio.com -> Azure DevOps
gitlab -> GitLab
```

### Validation Flow

**GitHub**:
1. Check gh CLI installed (`which gh`)
2. Check gh authenticated (`gh auth status`)
3. Test repo access (`gh api user`)

**Azure DevOps**:
1. Test organization access (`GET /_apis/projects`)
2. Test project access (`GET /{project}/_apis/project`)
3. Detect PAT scopes from endpoint responses

**GitLab**:
1. Test user endpoint (`GET /api/v4/user`)
2. Return limited support warning

## Files Changed

### Created (9 files)
- `src/doit_cli/models/wizard_models.py` - WizardStep, WizardState, ValidationResult, ConfigBackup, exceptions
- `src/doit_cli/services/provider_validation_service.py` - ProviderValidationService (~250 lines)
- `src/doit_cli/services/config_backup_service.py` - ConfigBackupService (~150 lines)
- `src/doit_cli/services/wizard_service.py` - WizardService (~400 lines)
- `tests/unit/services/test_provider_validation_service.py` - 20 unit tests
- `tests/unit/services/test_wizard_service.py` - 17 unit tests
- `tests/unit/services/test_config_backup_service.py` - 18 unit tests
- `tests/integration/test_provider_wizard.py` - Integration tests

### Modified (2 files)
- `src/doit_cli/services/provider_config.py` - Extended with validated_at, configured_by, wizard_version fields
- `src/doit_cli/cli/provider_command.py` - Added wizard subcommand with --force flag

## Testing

### Automated Tests
- **Feature Tests**: 55 tests passed
- **Full Suite**: 1,432 tests passed
- **No regressions detected** - All existing functionality intact

### Manual Tests (11/11 Passed)

| Test ID | Description | Result |
|---------|-------------|--------|
| MT-001 | Wizard command exists and help displays | PASS |
| MT-002 | Provider auto-detection from git remote | PASS |
| MT-003 | gh CLI detection and authentication check | PASS |
| MT-004 | Full GitHub validation flow | PASS |
| MT-005 | Backup service (create, list, restore, latest) | PASS |
| MT-006 | Wizard service initialization and methods | PASS |
| MT-007 | Azure DevOps validation error handling | PASS |
| MT-008 | GitLab validation with error messages | PASS |
| MT-009 | Wizard models (WizardStep, ValidationResult, WizardState) | PASS |
| MT-010 | ProviderConfig extended fields persistence | PASS |
| MT-011 | Exception classes (WizardCancelledError, etc.) | PASS |

### Contract Compliance

| Contract | Implementation | Status |
|----------|---------------|--------|
| ValidationService | ProviderValidationService | COMPLIANT |
| ConfigBackupService | ConfigBackupService | COMPLIANT |
| WizardService | WizardService | COMPLIANT |

## Usage

### CLI Commands

```bash
# Run the configuration wizard
doit provider wizard

# Force reconfiguration (skip confirmation)
doit provider wizard --force
```

### Wizard Flow

```
╭─ Provider Configuration Wizard ─╮
│ Step 1 of 4: Detecting Provider │
╰─────────────────────────────────╯

Detected: GitHub (from git remote)

╭─ Provider Configuration Wizard ─╮
│ Step 2 of 4: GitHub Setup       │
╰─────────────────────────────────╯

✓ GitHub CLI (gh) is installed
✓ Authenticated as: octocat
? Are you using GitHub Enterprise? [y/N]: n

⠋ Validating configuration...

╭─ Configuration Complete ─────────────────╮
│ Provider: GitHub                         │
│ Auth Method: gh CLI                      │
│ Authenticated: octocat                   │
│ Repository Access: ✓ Verified            │
╰──────────────────────────────────────────╯
```

## Error Messages

| Scenario | Error | Suggestion |
|----------|-------|------------|
| gh not found | "GitHub CLI (gh) is not installed" | "Install from https://cli.github.com" |
| gh not authed | "GitHub CLI is not authenticated" | "Run 'gh auth login' to authenticate" |
| ADO PAT invalid | "Invalid Personal Access Token" | "Create a new PAT at https://dev.azure.com/{org}/_usersSettings/tokens" |
| ADO project 404 | "Project not found in organization" | "Verify the project name or check permissions" |
| GitLab token invalid | "Invalid GitLab token" | "Create a new token at https://{host}/-/profile/personal_access_tokens" |

## Success Criteria

| Criteria | Status | Verification |
|----------|--------|--------------|
| SC-001: Wizard detects provider from remote | Verified | Auto-detection works |
| SC-002: GitHub auth via gh CLI works | Verified | Auth status checked |
| SC-003: ADO PAT validation works | Verified | Scopes detected |
| SC-004: Backup created on reconfigure | Verified | Backup file created |
| SC-005: Cancellation restores config | Verified | Ctrl+C handled |
| SC-006: All tests pass | Verified | 1,432 tests pass |

## Related Issues

- **Epic**: [#607](https://github.com/seanbarlow/doit/issues/607) - Git Provider Configuration Wizard
- **Tasks**: [#608](https://github.com/seanbarlow/doit/issues/608) - [#635](https://github.com/seanbarlow/doit/issues/635) (28 tasks)

## Impact

- **Improved DX**: Guided setup replaces manual configuration
- **Credential Validation**: Catches auth issues before workflow execution
- **Safe Reconfiguration**: Backups prevent data loss during provider switches
- **Provider Support**: Foundation for multi-provider workflows

## Next Steps

1. **Future Enhancement**: Implement back navigation (FR-007)
2. **GitLab Full Support**: Expand GitLab implementation when API features added
3. **Integration**: Use wizard validation in other commands

---

**Feature Documentation Generated**: 2026-01-22
**Generated by**: `/doit.checkin`
