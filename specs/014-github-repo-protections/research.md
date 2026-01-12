# Research: GitHub Repository Protections and Best Practices

**Feature**: 014-github-repo-protections
**Date**: 2026-01-12

## Current State Analysis

### Documentation Files (FR-009 to FR-013)

| File | Status | Notes |
|------|--------|-------|
| SECURITY.md | Exists | Needs review for completeness |
| CONTRIBUTING.md | Exists | Needs review for completeness |
| CODE_OF_CONDUCT.md | Exists | Needs review for completeness |
| LICENSE | Exists | MIT license confirmed |

**Decision**: Review existing files for completeness rather than creating new ones.

### Issue Templates (FR-017, FR-018)

| Template | Status | Notes |
|----------|--------|-------|
| epic.yml | Exists | DoIt workflow template |
| feature.yml | Exists | DoIt workflow template |
| task.yml | Exists | DoIt workflow template |
| bug_report.yml | Missing | Needs creation |
| feature_request.yml | Missing | Needs creation (public-facing, distinct from DoIt feature.yml) |

**Decision**: Create bug_report.yml and feature_request.yml for public contributors. Keep existing DoIt workflow templates.

### PR Template (FR-019)

| Template | Status | Notes |
|----------|--------|-------|
| PULL_REQUEST_TEMPLATE.md | Missing | Needs creation |

**Decision**: Create PR template in `.github/` directory.

### Repository Settings

| Setting | Current Value | Target Value |
|---------|---------------|--------------|
| Visibility | private | public (after configuration) |
| Description | null | "DoIt CLI - Spec-Driven Development Framework for AI-powered software development" |
| Topics | [] | ["cli", "python", "spec-driven-development", "ai", "development-workflow", "scaffolding"] |
| Default branch | main | main (no change) |

## gh CLI Commands Research

### Branch Protection (FR-001 to FR-005)

```bash
# Create branch protection rule
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":[]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  --field restrictions=null \
  --field required_linear_history=false \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

**Note**: Branch protection requires the repo to be public OR on a paid GitHub plan for private repos.

### Security Settings (FR-006 to FR-008)

```bash
# Enable secret scanning (requires repo to be public or GitHub Advanced Security)
gh api repos/{owner}/{repo} --method PATCH \
  --field security_and_analysis='{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"}}'

# Dependabot alerts are enabled automatically for public repos
# For configuration, create .github/dependabot.yml
```

### Repository Metadata (FR-014, FR-015)

```bash
# Update description and topics
gh repo edit seanbarlow/doit \
  --description "DoIt CLI - Spec-Driven Development Framework for AI-powered software development" \
  --add-topic cli \
  --add-topic python \
  --add-topic spec-driven-development \
  --add-topic ai \
  --add-topic development-workflow \
  --add-topic scaffolding
```

## Dependabot Configuration

For FR-007 and FR-008, create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Implementation Order

Based on dependencies and risk:

1. **Create documentation files/templates first** (no risk, can be done on branch)
2. **Configure Dependabot** (via file creation, safe)
3. **Update repository metadata** (description, topics - low risk)
4. **Make repository public** (requires security checks complete)
5. **Enable branch protection** (must be done AFTER making public for free tier)
6. **Enable security features** (auto-enabled for public repos)

## Alternatives Considered

### Branch Protection Timing

- **Option A**: Configure before going public (requires GitHub Pro/Team)
- **Option B**: Make public first, then configure (free tier compatible)

**Decision**: Option B - Make public first, as this is a personal/open-source project.

### Issue Template Format

- **Option A**: YAML forms (modern, structured)
- **Option B**: Markdown templates (traditional, flexible)

**Decision**: Option A - YAML forms provide better UX with form fields.

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Branch protection not working on private repo | Make public before configuring |
| Secrets in repo history | Review history before making public |
| Incomplete security setup | Follow checklist before public visibility |
