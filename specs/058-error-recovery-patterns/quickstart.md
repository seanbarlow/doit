# Quickstart: Error Recovery Patterns in All Commands

**Feature**: 058-error-recovery-patterns
**Branch**: `058-error-recovery-patterns`

## Overview

This feature adds structured `## Error Recovery` sections to all 13 command templates. It is a **documentation-only** change — no Python code, no tests, no new dependencies.

## Prerequisites

- Familiarity with the existing command templates in `.doit/templates/commands/`
- Understanding of the reference pattern in `doit.fixit.md` (lines 258-300)

## Getting Started

### 1. Review the reference pattern

```bash
# Read the fixit error recovery section (the pattern to follow)
cat .doit/templates/commands/doit.fixit.md | sed -n '/^## Error Recovery/,/^## /p' | head -50
```

### 2. Check current state of each template

```bash
# See which templates already have error handling
for f in .doit/templates/commands/doit.*.md; do
  echo "=== $(basename $f) ==="
  grep -n "Error\|On Error" "$f" | head -5
  echo
done
```

### 3. Implementation order

Follow this order (highest impact first):

**Tier 1 — Core workflow** (expand existing On Error):
1. `doit.implementit.md` — highest risk of lost progress
2. `doit.specit.md` — most frequently used
3. `doit.planit.md` — dependency chain start
4. `doit.testit.md` — common failure point
5. `doit.reviewit.md` — pre-merge gate

**Tier 2 — Peripheral** (mix of expand and new):
6. `doit.checkin.md` — expand existing
7. `doit.taskit.md` — expand existing
8. `doit.researchit.md` — write from scratch
9. `doit.scaffoldit.md` — write from scratch
10. `doit.roadmapit.md` — write from scratch
11. `doit.constitution.md` — expand existing
12. `doit.documentit.md` — add recovery steps to existing severity table

**Tier 3 — Reference alignment**:
13. `doit.fixit.md` — minor format alignment only

### 4. Sync after all edits

```bash
# Propagate template changes to Claude Code and Copilot
doit sync-prompts
```

### 5. Verify

```bash
# Confirm all 13 templates have Error Recovery sections
for f in .doit/templates/commands/doit.*.md; do
  if grep -q "^## Error Recovery" "$f"; then
    echo "✓ $(basename $f)"
  else
    echo "✗ $(basename $f) — MISSING"
  fi
done
```

## Error Recovery Section Template

Copy this template for each new error scenario:

```markdown
### {Error Scenario Name}

{Plain-language summary in ≤25 words.}

**{ERROR|WARNING|FATAL}** | If {specific condition}:

1. {Recovery step with specific CLI command}
2. {Next step}
3. Verify: {command to confirm recovery}

> Prevention: {one-liner tip}

If the above steps don't resolve the issue: {escalation guidance}
```

## Key Files

| File | Purpose |
|------|---------|
| [spec.md](spec.md) | Feature specification |
| [plan.md](plan.md) | Implementation plan with all error scenarios |
| [research.md](research.md) | Background research and codebase analysis |
| `.doit/templates/commands/doit.fixit.md` | Reference pattern |
