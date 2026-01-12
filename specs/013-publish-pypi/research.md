# Research: Publish CLI to PyPI

**Feature**: 013-publish-pypi
**Date**: 2026-01-11
**Purpose**: Document technical decisions and best practices for PyPI publishing

## Research Summary

This feature involves publishing the doit-cli package to PyPI using GitHub Actions for automation. The package already has a working build configuration with hatchling.

---

## 1. PyPI Publishing Method

### Decision: Use Trusted Publishing (OIDC)

**Rationale**: PyPI's Trusted Publishing eliminates the need to manage API tokens manually. GitHub Actions can authenticate directly with PyPI using OpenID Connect, which is more secure and requires no secret management.

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Trusted Publishing (OIDC) | No secrets needed, automatic rotation, audit trail | Requires initial PyPI project setup | **Selected** |
| API Token in Secrets | Simple to understand | Tokens can leak, require rotation | Rejected |
| Username/Password | Familiar pattern | Deprecated by PyPI, insecure | Rejected |

---

## 2. Package Metadata Requirements

### Decision: Add Complete pyproject.toml Metadata

**Required Fields for PyPI**:
- `authors` - Name and email of maintainers
- `license` - SPDX license identifier (MIT recommended)
- `readme` - Path to README file for PyPI page display
- `keywords` - Searchable terms
- `classifiers` - PyPI trove classifiers for categorization
- `urls` - Homepage, Documentation, Repository, Issues links

**Current State**: pyproject.toml has basic fields but missing authors, license, readme, classifiers, and urls.

---

## 3. GitHub Actions Workflow

### Decision: Use pypa/gh-action-pypi-publish

**Rationale**: This is the official PyPA (Python Packaging Authority) action, maintained by the same organization that maintains PyPI and pip. It supports trusted publishing natively.

**Workflow Trigger**: On push of tags matching `v*.*.*`

**Workflow Steps**:
1. Checkout code
2. Setup Python 3.11
3. Install build dependencies (hatchling)
4. Build package (`python -m build`)
5. Publish to PyPI (pypa/gh-action-pypi-publish)

---

## 4. Version Management

### Decision: Manual Version Bumping in pyproject.toml

**Rationale**: For a small project, manual version bumping before tagging provides explicit control. Automated version management (like bump2version or python-semantic-release) adds complexity not needed at this stage.

**Release Process**:
1. Update version in `pyproject.toml`
2. Commit: `git commit -m "chore: bump version to X.Y.Z"`
3. Tag: `git tag vX.Y.Z`
4. Push: `git push && git push --tags`
5. CI automatically publishes to PyPI

---

## 5. Package Name Availability

### Decision: Use `doit-cli` Name

**Research Finding**: The name `doit` is taken on PyPI by an unrelated project (a task automation tool). The name `doit-cli` is available and clearly distinguishes this package.

**Verification**: Checked `pip index versions doit-cli` - returns "No matching distribution found" confirming availability.

---

## 6. Template Bundling

### Decision: Use hatch force-include for Templates

**Current Configuration** (pyproject.toml):
```toml
[tool.hatch.build.targets.wheel.force-include]
"templates" = "doit_cli/templates"
```

**Verification Needed**: Ensure this correctly bundles all subdirectories:
- `templates/commands/` (command templates)
- `templates/memory/` (memory templates)
- `templates/scripts/` (workflow scripts)
- `templates/github-issue-templates/` (GitHub issue templates)

---

## 7. README for PyPI

### Decision: Use Root README.md

**Approach**: Add `readme = "README.md"` to pyproject.toml. The root README.md will be displayed on the PyPI package page.

**Note**: Current README.md content should be reviewed to ensure it provides good PyPI landing page content (installation instructions, quick start, etc.).

---

## 8. Testing Strategy

### Decision: Test Locally Before Publishing

**Pre-publish Verification**:
1. Build locally: `python -m build`
2. Install from wheel: `pip install dist/doit_cli-*.whl`
3. Verify command: `doit --version`
4. Verify templates: Check `.doit/templates/` after `doit init`

**Optional**: Use TestPyPI for first release validation before publishing to production PyPI.

---

## Key Findings Summary

| Area | Decision | Implementation |
|------|----------|----------------|
| Auth Method | Trusted Publishing (OIDC) | Configure PyPI project + GitHub workflow |
| Metadata | Complete pyproject.toml | Add authors, license, readme, classifiers, urls |
| CI/CD | GitHub Actions | `.github/workflows/publish.yml` |
| Version | Manual bump | Update pyproject.toml before tagging |
| Package Name | `doit-cli` | Already configured |
| Templates | hatch force-include | Verify all subdirectories included |
| README | Root README.md | Add readme field to pyproject.toml |

---

## Open Questions (Resolved)

1. ~~Should we use TestPyPI first?~~ → Yes, for initial validation
2. ~~What license to use?~~ → MIT (standard for tools like this)
3. ~~Who are the maintainers?~~ → Use project owner info from git config

---

## 9. Manual Setup Instructions

### Step 1: Create PyPI Account (if needed)

1. Go to https://pypi.org/account/register/
2. Create account with email verification
3. Enable 2FA for security (recommended)

### Step 2: Create GitHub Environment

1. Go to repository Settings → Environments
2. Click "New environment"
3. Name: `pypi`
4. (Optional) Add protection rules:
   - Required reviewers for manual approval
   - Deployment branch restrictions (only `main` or tags)

### Step 3: Configure PyPI Trusted Publishing

**Before first publish**, configure PyPI to trust GitHub Actions:

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the form:
   - **PyPI Project Name**: `doit-cli`
   - **Owner**: `vanbarlow09`
   - **Repository name**: `doit`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

This creates a "pending publisher" that will be claimed when the first publish occurs.

### Step 4: First Release

```bash
# Update version in pyproject.toml (e.g., 0.1.0)
# Commit the change
git add pyproject.toml
git commit -m "chore: release v0.1.0"

# Create and push tag
git tag v0.1.0
git push origin main
git push origin v0.1.0

# Monitor GitHub Actions
# Once complete, verify: pip index versions doit-cli
```

### Step 5: Verify Installation

```bash
# Test installation
uv tool install doit-cli
# or: pip install doit-cli

# Verify
doit --version

# Test init creates templates
mkdir /tmp/test-doit && cd /tmp/test-doit
doit init .
ls -la .doit/memory/
ls -la .doit/commands/
```

---

## 10. Implementation Status

| Task | Status | Notes |
|------|--------|-------|
| Package name verified | ✅ | `doit-cli` available |
| Authors/license added | ✅ | pyproject.toml updated |
| Keywords/classifiers added | ✅ | pyproject.toml updated |
| Project URLs added | ✅ | pyproject.toml updated |
| Publish workflow created | ✅ | `.github/workflows/publish.yml` |
| Template bundling verified | ✅ | All templates in wheel |
| README reviewed | ✅ | Good PyPI landing page content |
| GitHub environment | ⏳ | Manual: Create `pypi` environment |
| PyPI trusted publishing | ⏳ | Manual: Configure pending publisher |
| First release | ⏳ | Manual: Tag and push |
