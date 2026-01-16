# Quickstart: Git Hook Integration for Workflow Enforcement

**Feature**: 025-git-hooks-workflow

## Overview

Git hooks enforce the spec-first development workflow by validating commits and pushes against specification requirements.

## Installation

### Install Hooks

```bash
# Install pre-commit and pre-push hooks
doit hooks install

# Install with automatic backup of existing hooks
doit hooks install --backup

# Force install (overwrite without prompting)
doit hooks install --force
```

### Check Installation Status

```bash
# Show current hook status and configuration
doit hooks status
```

Output:
```
Git Hooks Status
================

Installed Hooks:
  pre-commit: ✓ Installed (2026-01-15)
  pre-push:   ✓ Installed (2026-01-15)

Configuration: .doit/config/hooks.yaml
  Pre-commit validation: enabled
  Pre-push validation:   enabled
  Bypass logging:        enabled

Protected Branches: main, develop
Exempt Patterns: hotfix/*, bugfix/*
```

### Uninstall Hooks

```bash
# Remove installed hooks
doit hooks uninstall

# Restore previously backed up hooks
doit hooks restore
```

---

## Configuration

Create `.doit/config/hooks.yaml` to customize behavior:

```yaml
# Hook configuration for workflow enforcement
version: 1

pre_commit:
  enabled: true
  require_spec: true
  require_spec_status:
    - "In Progress"
    - "Complete"
    - "Approved"
  exempt_branches:
    - main
    - develop
    - "hotfix/*"
    - "bugfix/*"
  exempt_paths:
    - "docs/**"
    - "*.md"
    - ".github/**"

pre_push:
  enabled: true
  require_spec: true
  require_plan: true
  require_tasks: false
  exempt_branches:
    - main
    - develop

logging:
  enabled: true
  log_bypasses: true
  log_path: .doit/logs/hook-bypasses.log
```

---

## Usage Examples

### Normal Workflow

```bash
# 1. Create feature branch
git checkout -b 025-my-feature

# 2. Create specification (required before code commits)
doit specit "My new feature"

# 3. Now commits will work
git add .
git commit -m "Add initial spec"  # ✓ Passes - spec exists

# 4. Create plan before pushing
doit planit

# 5. Push will now work
git push -u origin 025-my-feature  # ✓ Passes - spec and plan exist
```

### Blocked Commit (Missing Spec)

```bash
git checkout -b 026-another-feature
echo "some code" > feature.py
git add feature.py
git commit -m "Add feature"

# Output:
# ✗ Pre-commit validation failed
#
# Missing specification for branch: 026-another-feature
# Expected: specs/026-another-feature/spec.md
#
# To fix: Run `doit specit "Your feature description"` first
#
# Or bypass with: git commit --no-verify (not recommended)
```

### Blocked Commit (Draft Spec)

```bash
# Spec exists but status is "Draft"
git add src/feature.py
git commit -m "Implement feature"

# Output:
# ✗ Pre-commit validation failed
#
# Specification has invalid status: Draft
# Allowed statuses: In Progress, Complete, Approved
#
# To fix: Update spec.md status to "In Progress" before committing code
```

### Blocked Push (Missing Plan)

```bash
git push origin 025-my-feature

# Output:
# ✗ Pre-push validation failed
#
# Missing required artifact: plan.md
# Expected: specs/025-my-feature/plan.md
#
# To fix: Run `/doit.planit` to create implementation plan
```

### Emergency Bypass

```bash
# Use --no-verify for emergencies (logged for audit)
git commit --no-verify -m "Emergency hotfix"

# Check bypass log
doit hooks report

# Output:
# Hook Bypass Report
# ==================
#
# Total bypasses: 1
#
# 2026-01-15 14:30:00 | branch: 025-feature | commit: abc1234 | user: dev@example.com
```

---

## Exempt Branches

These branches skip validation by default:
- `main` - Production branch
- `develop` - Integration branch
- `hotfix/*` - Emergency fixes
- `bugfix/*` - Bug fix branches

Configure additional exempt patterns in `hooks.yaml`.

---

## Exempt Paths

Files matching these patterns don't require specs:
- `docs/**` - Documentation changes
- `*.md` - Markdown files
- `.github/**` - GitHub configuration

When ALL staged files match exempt patterns, validation is skipped.

---

## Troubleshooting

### "Hook validation failed but I have a spec"

Check that:
1. Branch name matches spec directory (e.g., `025-feature` → `specs/025-feature/`)
2. Spec status is not "Draft" when committing code
3. You're not in detached HEAD state

### "Hooks not running"

Verify installation:
```bash
ls -la .git/hooks/pre-commit
doit hooks status
```

### "Want to disable temporarily"

Use `--no-verify` (logged) or disable in config:
```yaml
pre_commit:
  enabled: false
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `doit hooks install` | Install pre-commit and pre-push hooks |
| `doit hooks uninstall` | Remove installed hooks |
| `doit hooks status` | Show installation and configuration status |
| `doit hooks restore` | Restore backed up hooks |
| `doit hooks report` | Show bypass audit log |
| `doit hooks validate <type>` | Run validation (called by hooks) |
