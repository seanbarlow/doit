# Requirements Checklist: Git Hook Integration for Workflow Enforcement

**Feature Branch**: `025-git-hooks-workflow`
**Generated**: 2026-01-15

## Functional Requirements

| ID | Requirement | Status | Notes |
|----|-------------|--------|-------|
| FR-001 | System MUST provide a `doit hooks install` command that installs pre-commit and pre-push Git hooks | [ ] | |
| FR-002 | System MUST provide a `doit hooks uninstall` command that removes installed hooks | [ ] | |
| FR-003 | Pre-commit hook MUST validate that feature branches have a corresponding spec file at `specs/{branch-name}/spec.md` | [ ] | |
| FR-004 | Pre-commit hook MUST check that spec files are not in "Draft" status when committing implementation code | [ ] | |
| FR-005 | Pre-push hook MUST validate that feature branches have required workflow artifacts (configurable: spec.md, plan.md, tasks.md) | [ ] | |
| FR-006 | System MUST skip validation for protected branches (`main`, `develop`) and merge commits | [ ] | |
| FR-007 | System MUST support a configuration file (`.doit/config/hooks.yaml`) for customizing enforcement rules | [ ] | |
| FR-008 | System MUST backup existing hooks before overwriting and offer restoration via `doit hooks restore` | [ ] | |
| FR-009 | System MUST log all hook bypass events (`--no-verify`) to `.doit/logs/hook-bypasses.log` | [ ] | |
| FR-010 | System MUST provide a `doit hooks status` command showing current hook configuration and installation state | [ ] | |
| FR-011 | System MUST provide clear, actionable error messages when commits/pushes are blocked | [ ] | |
| FR-012 | System MUST support `exempt_branches` configuration for branches that bypass validation (e.g., `hotfix/*`) | [ ] | |
| FR-013 | System MUST support `exempt_paths` configuration for file patterns that don't require specs (e.g., `docs/**`) | [ ] | |

## Success Criteria

| ID | Criterion | Status | Notes |
|----|-----------|--------|-------|
| SC-001 | `doit hooks install` successfully installs hooks in under 2 seconds | [ ] | |
| SC-002 | Pre-commit validation completes in under 500ms for typical repositories | [ ] | |
| SC-003 | 100% of feature branch commits are validated against spec requirements (unless bypassed) | [ ] | |
| SC-004 | Zero false positives - valid commits on properly documented branches always succeed | [ ] | |
| SC-005 | Bypass events are logged with 100% reliability for audit purposes | [ ] | |
| SC-006 | Existing hooks are never lost - backup/restore functionality works correctly | [ ] | |

## User Story Coverage

| Story | Title | Priority | Scenarios Covered | Status |
|-------|-------|----------|-------------------|--------|
| US-1 | Hook Installation | P1 | 3 | [ ] |
| US-2 | Pre-Commit Validation | P1 | 4 | [ ] |
| US-3 | Pre-Push Validation | P2 | 3 | [ ] |
| US-4 | Hook Configuration | P2 | 3 | [ ] |
| US-5 | Hook Bypass for Emergencies | P3 | 3 | [ ] |

## Edge Cases

| Case | Description | Status | Notes |
|------|-------------|--------|-------|
| EC-001 | Branch name doesn't follow `###-feature-name` pattern | [ ] | |
| EC-002 | spec.md exists but is malformed | [ ] | |
| EC-003 | Commits with only documentation or test changes | [ ] | |
| EC-004 | Detached HEAD state | [ ] | |

---

**Legend**:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked
