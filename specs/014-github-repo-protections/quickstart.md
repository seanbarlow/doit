# Quickstart: GitHub Repository Protections

**Feature**: 014-github-repo-protections
**Estimated Time**: 30-45 minutes

## Prerequisites

- [ ] `gh` CLI installed and authenticated (`gh auth status`)
- [ ] Admin access to seanbarlow/doit repository
- [ ] Review repo history for any accidentally committed secrets

## Implementation Steps

### Step 1: Review Existing Documentation Files

Verify the following files exist and contain substantive content:

```bash
# Check files exist
ls -la SECURITY.md CONTRIBUTING.md CODE_OF_CONDUCT.md LICENSE
```

Review each file for:
- [ ] SECURITY.md - Has vulnerability reporting instructions
- [ ] CONTRIBUTING.md - Has setup instructions, PR process, code standards
- [ ] CODE_OF_CONDUCT.md - Has community standards (e.g., Contributor Covenant)
- [ ] LICENSE - Contains MIT license text

### Step 2: Create Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.yml`:

```yaml
name: Bug Report
description: Report a bug or unexpected behavior
title: "[Bug]: "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  - type: input
    id: version
    attributes:
      label: DoIt Version
      description: What version of doit-toolkit-cli are you running?
      placeholder: "0.0.23"
    validations:
      required: true
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear description of what the bug is
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Run `doit init ...`
        2. See error...
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What you expected to happen
    validations:
      required: true
  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: OS, Python version, etc.
      placeholder: |
        - OS: macOS 14.0
        - Python: 3.11.5
    validations:
      required: true
```

Create `.github/ISSUE_TEMPLATE/feature_request.yml`:

```yaml
name: Feature Request
description: Suggest a new feature or enhancement
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a feature! Please fill out the details below.
  - type: textarea
    id: problem
    attributes:
      label: Problem Statement
      description: What problem does this feature solve?
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: How would you like this to work?
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Any alternative solutions you've considered?
  - type: checkboxes
    id: contribution
    attributes:
      label: Contribution
      options:
        - label: I would be willing to help implement this feature
```

### Step 3: Create PR Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Summary

<!-- Brief description of changes -->

## Related Issues

<!-- Link to related issues: Fixes #123, Part of #456 -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Testing

<!-- Describe the tests you ran -->

- [ ] Tests pass locally (`pytest`)
- [ ] Linting passes (`ruff check .`)

## Checklist

- [ ] My code follows the project's code style
- [ ] I have updated documentation as needed
- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass
```

### Step 4: Create Dependabot Configuration

Create `.github/dependabot.yml`:

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
    open-pull-requests-limit: 3
```

### Step 5: Update Repository Metadata

```bash
gh repo edit seanbarlow/doit \
  --description "DoIt CLI - Spec-Driven Development Framework for AI-powered software development" \
  --add-topic cli \
  --add-topic python \
  --add-topic spec-driven-development \
  --add-topic ai \
  --add-topic development-workflow \
  --add-topic scaffolding
```

### Step 6: Make Repository Public

```bash
gh repo edit seanbarlow/doit --visibility public
```

**Warning**: This cannot be easily undone. Ensure all sensitive data has been removed.

### Step 7: Configure Branch Protection

After making the repository public:

```bash
gh api repos/seanbarlow/doit/branches/main/protection \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  --field required_status_checks='{"strict":true,"contexts":[]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  --field restrictions=null \
  --field required_linear_history=false \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

### Step 8: Verify Security Features

After making public, verify in GitHub Settings:
- [ ] Secret scanning is enabled (Settings → Security → Code security and analysis)
- [ ] Dependabot alerts are enabled
- [ ] Dependabot security updates are enabled

## Verification Checklist

### Branch Protection
- [ ] Direct push to main is rejected
- [ ] PR requires 1 approval
- [ ] Stale reviews are dismissed on new commits

### Security
- [ ] Secret scanning enabled
- [ ] Dependabot alerts enabled
- [ ] SECURITY.md visible in Security tab

### Documentation
- [ ] CONTRIBUTING.md visible in Insights → Community
- [ ] CODE_OF_CONDUCT.md visible
- [ ] LICENSE badge shows MIT

### Templates
- [ ] Creating new issue shows Bug Report and Feature Request options
- [ ] Creating PR shows template

### Metadata
- [ ] Description visible on repo page
- [ ] Topics visible below description
