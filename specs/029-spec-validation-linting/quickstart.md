# Quickstart: Spec Validation and Linting

**Feature**: 029-spec-validation-linting

## Overview

The `doit validate` command checks spec files for structural completeness, naming conventions, and quality standards before implementation begins.

## Basic Usage

### Validate a Single Spec

```bash
# Validate a specific spec file
doit validate specs/029-spec-validation-linting/spec.md
```

**Output**:
```
Validating: specs/029-spec-validation-linting/spec.md

  WARNINGS (1)
  └─ Line 67: User Story 4 has no acceptance scenarios

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quality Score: 95/100
Status: PASS (0 errors, 1 warning)
```

### Validate All Specs

```bash
# Validate all specs in the project
doit validate --all
```

**Output**:
```
Spec Validation Summary

| Spec | Score | Status | Errors | Warnings |
|------|-------|--------|--------|----------|
| 029-spec-validation-linting | 95 | PASS | 0 | 1 |
| 028-docs-tutorial-refresh | 100 | PASS | 0 | 0 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 2 specs | Passed: 2 | Failed: 0 | Avg Score: 97
```

## CI/CD Integration

### JSON Output for Automation

```bash
# Get machine-readable output
doit validate --all --format=json
```

```json
{
  "summary": {
    "total_specs": 2,
    "passed": 2,
    "failed": 0,
    "average_score": 97
  },
  "results": [...]
}
```

### Pre-commit Hook

Add to `.doit/config/hooks.yaml`:

```yaml
hooks:
  pre-commit:
    - type: spec-validation
      enabled: true
      fail_on: error  # or "warning" for stricter enforcement
```

Now specs are validated before every commit:

```bash
$ git commit -m "Add feature spec"
Running spec validation...
  specs/new-feature/spec.md: PASS (Score: 85)
[main abc1234] Add feature spec
```

## Custom Rules

### Create Configuration

Create `.doit/validation-rules.yaml`:

```yaml
version: "1.0"

# Disable a built-in rule
disabled:
  - "check-todo-markers"

# Override severity
overrides:
  - rule: "missing-acceptance-scenarios"
    severity: error  # Upgrade from warning

# Add custom rules
custom:
  - name: "require-security-section"
    description: "Specs must include Security Considerations"
    pattern: "^## Security Considerations"
    severity: warning
    category: "organization"
```

### Verify Custom Rules

```bash
doit validate --all
# Now includes your custom "require-security-section" rule
```

## Common Scenarios

### Before Planning

Always validate before running `/doit.planit`:

```bash
doit validate specs/my-feature/spec.md && doit planit
```

### Quality Gate in CI

```yaml
# .github/workflows/spec-validation.yml
jobs:
  validate-specs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install doit-toolkit-cli
      - run: doit validate --all --format=json > validation.json
      - run: |
          if [ $(jq '.summary.failed' validation.json) -gt 0 ]; then
            exit 1
          fi
```

### Filter by Severity

```bash
# Only show errors (quieter output)
doit validate --all --quiet

# Show errors and warnings, skip info
doit validate --all --severity=warning
```

## Understanding Quality Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Excellent | Ready for planning |
| 70-89 | Good | Review warnings before proceeding |
| 50-69 | Fair | Address errors before planning |
| 0-49 | Poor | Significant rework needed |

## Next Steps

1. Run `doit validate` on your spec
2. Fix any errors reported
3. Address warnings for better quality
4. Run `/doit.planit` when score is 70+
