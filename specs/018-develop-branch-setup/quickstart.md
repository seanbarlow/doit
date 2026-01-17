# Quickstart: New Branching Workflow

**Feature**: 018-develop-branch-setup

This guide explains the new branching workflow after implementing the develop branch.

## Branch Structure

```
main      ← Production releases only (PyPI publishes)
  │
develop   ← Default branch, feature integration (DEFAULT)
  │
  ├── 018-feature-a
  ├── 019-feature-b
  └── 020-feature-c
```

## Daily Development Workflow

### Starting New Work

```bash
# Make sure you're on develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b ###-feature-name
```

### Completing a Feature

```bash
# Push your feature branch
git push -u origin ###-feature-name

# Create PR (targets develop automatically)
gh pr create --title "feat: description" --body "..."
```

### After PR Merge

```bash
# Clean up local branch
git checkout develop
git pull origin develop
git branch -d ###-feature-name
```

## Release Workflow (Maintainers)

When ready to release to production:

```bash
# Create PR from develop to main
gh pr create --base main --head develop --title "Release vX.Y.Z"

# After merge, tag the release
git checkout main
git pull origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

## Key Changes from Previous Workflow

| Before | After |
| ------ | ----- |
| Branch from `main` | Branch from `develop` |
| PRs target `main` | PRs target `develop` |
| Clone lands on `main` | Clone lands on `develop` |
| `main` = development | `main` = production only |

## Quick Reference

| Task | Command |
| ---- | ------- |
| Start feature | `git checkout -b ###-name develop` |
| Create PR | `gh pr create` (targets develop) |
| Release | PR from develop → main |
| Hotfix | Branch from main, PR to main AND develop |

## Common Scenarios

### I accidentally branched from main

```bash
# Rebase onto develop
git rebase --onto develop main ###-feature-name
```

### I need to update my feature branch

```bash
git checkout ###-feature-name
git fetch origin
git rebase origin/develop
```

### Emergency hotfix needed

```bash
# Branch from main for hotfixes
git checkout main
git pull origin main
git checkout -b hotfix-description

# After fix, PR to BOTH main and develop
```
