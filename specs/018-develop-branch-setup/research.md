# Research: Develop Branch Setup

**Feature**: 018-develop-branch-setup
**Date**: 2026-01-13

## Current State Analysis

### Existing Branch Structure

The repository currently uses a single-branch workflow:

- **main**: The only long-lived branch, serves as both development and production
- Feature branches merge directly to `main`

### Existing Branch Protection on `main`

Retrieved via `gh api repos/{owner}/{repo}/branches/main/protection`:

```json
{
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false,
    "required_approving_review_count": 1
  },
  "required_status_checks": {
    "strict": true,
    "contexts": [],
    "checks": []
  },
  "enforce_admins": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_signatures": false,
  "required_linear_history": false,
  "required_conversation_resolution": false,
  "lock_branch": false
}
```

**Key settings to replicate on `develop`:**

| Setting | Value | Purpose |
| ------- | ----- | ------- |
| Required PR reviews | 1 | Code review before merge |
| Dismiss stale reviews | true | Re-review after changes |
| Force pushes | disabled | Protect history |
| Deletions | disabled | Prevent accidental deletion |

### Current Documentation References

**CONTRIBUTING.md** references that need updating:

- Line 267: "Create Branch - From latest `main`" → needs to change to `develop`
- Line 39-40: Branch naming convention section
- PR process describes merging to `main`

### Open PRs and Branches

As of research date:

- No open PRs targeting `main`
- No blocking issues for branch switch

## Industry Best Practices Research

### Gitflow Model (Reference)

The classic Gitflow model uses:

- `main` (or `master`): Production-ready code only
- `develop`: Integration branch for features
- `feature/*`: Short-lived feature branches
- `release/*`: Release preparation (optional)
- `hotfix/*`: Emergency production fixes

### GitHub Flow (Alternative)

Simpler model with:

- `main`: Always deployable
- Feature branches merge directly to main
- Continuous deployment

### Recommended Approach for DoIt

A **simplified Gitflow** is appropriate:

- `main`: Production releases (PyPI publishes)
- `develop`: Default branch, feature integration
- `###-feature-name`: Feature branches (existing convention)

This provides:

1. Clear separation of stable vs. in-progress code
2. Buffer before production releases
3. Maintains existing numbered branch convention
4. No need for release branches (small team)

## GitHub CLI Commands Research

### Setting Default Branch

```bash
gh repo edit --default-branch develop
```

### Branch Protection API

The GitHub REST API endpoint for branch protection:

```
PUT /repos/{owner}/{repo}/branches/{branch}/protection
```

Required permissions: `repo` scope or repository admin

### Protection Rule JSON Structure

```bash
gh api repos/{owner}/{repo}/branches/develop/protection \
  -X PUT \
  -H "Accept: application/vnd.github+json" \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"required_approving_review_count":1}' \
  -f enforce_admins=false \
  -f required_status_checks=null \
  -f restrictions=null \
  -F allow_force_pushes=false \
  -F allow_deletions=false
```

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Contributors branch from main | Medium | Low | Update docs, main still exists |
| CI/CD breakage | Low | Medium | No CI currently; verify before switch |
| Confusion during transition | Medium | Low | Clear communication in docs |

## Conclusions

1. **Approach**: Simplified Gitflow with `main` + `develop`
2. **Protection**: Mirror existing `main` rules on `develop`
3. **Documentation**: Update CONTRIBUTING.md branch instructions
4. **Migration**: No open PRs, clean transition possible
