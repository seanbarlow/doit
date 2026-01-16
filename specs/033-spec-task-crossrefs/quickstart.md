# Quickstart: Cross-Reference Support

**Feature**: 033-spec-task-crossrefs
**Date**: 2026-01-16

## Overview

This feature enables bidirectional linking between specification requirements (FR-XXX) and implementation tasks, providing full traceability from requirements through implementation.

## Quick Usage

### 1. Add References to Tasks

When creating or editing tasks in `tasks.md`, add requirement references at the end of each task:

```markdown
## Tasks

- [ ] Implement RequirementParser class [FR-001]
- [ ] Add validation rules for orphaned references [FR-005]
- [ ] Create coverage report command [FR-003, FR-004]
```

### 2. Check Coverage

```bash
# View coverage report for current feature
doit xref coverage

# View as JSON for CI/CD
doit xref coverage --format json
```

### 3. Find Requirement Definition

```bash
# Locate FR-001 in spec.md
doit xref locate FR-001

# Get just the file:line for IDE integration
doit xref locate FR-001 --format line
```

### 4. Find Implementing Tasks

```bash
# List all tasks that implement FR-001
doit xref tasks FR-001
```

### 5. Validate Cross-References

```bash
# Check for orphaned references or uncovered requirements
doit xref validate

# Strict mode (treat uncovered as errors)
doit xref validate --strict
```

## Reference Syntax

| Syntax | Example | Meaning |
|--------|---------|---------|
| Single | `[FR-001]` | Task implements FR-001 |
| Multiple | `[FR-001, FR-003]` | Task implements both |
| Multi-spec | `[sub/spec.md#FR-001]` | Reference to nested spec |

## Validation Rules

| Rule | Severity | Description |
|------|----------|-------------|
| orphaned-task-reference | Error | Task references non-existent FR-XXX |
| uncovered-requirement | Warning | FR-XXX has no linked tasks |

## Integration Points

- **Pre-commit hook**: Validates cross-references before commit
- **`doit validate`**: Includes cross-reference checks
- **`doit status`**: Shows coverage percentage per spec

## Example Workflow

```bash
# 1. Create spec with requirements
doit specit "new feature"

# 2. Create implementation plan
doit planit

# 3. Generate tasks (now with FR reference placeholders)
doit taskit

# 4. Add specific FR references to tasks
# Edit tasks.md manually

# 5. Check coverage before implementing
doit xref coverage

# 6. Implement with full traceability
doit implementit
```

## Troubleshooting

### "Orphaned reference: FR-099"

The task references a requirement that doesn't exist in spec.md.

**Fix**: Either add FR-099 to the spec, or correct the reference to an existing FR-XXX.

### "Uncovered requirement: FR-003"

A requirement in spec.md has no linked tasks.

**Fix**: Add a task that implements FR-003, or mark it as "deferred" in the spec.

### Coverage not showing

Tasks.md must exist in the same directory as spec.md for coverage to be calculated.

**Fix**: Run `doit taskit` to generate tasks.md, then add FR references.
