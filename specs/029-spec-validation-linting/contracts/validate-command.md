# Contract: validate Command

**Module**: `src/doit_cli/cli/validate_command.py`

## Overview

CLI command for validating spec files. Provides human-readable and JSON output.

## Command Signature

```bash
doit validate [PATH] [OPTIONS]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| PATH | path | No | Spec file or directory to validate |

## Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| --all | -a | flag | false | Validate all specs in project |
| --format | -f | choice | human | Output format: human, json |
| --severity | -s | choice | all | Filter by minimum severity: error, warning, info, all |
| --quiet | -q | flag | false | Only show errors (implies --severity=error) |
| --path | -p | path | . | Project root directory |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All validations passed (may have warnings/info) |
| 1 | One or more validations failed (has errors) |
| 2 | Invalid arguments or file not found |

## Output Formats

### Human (default)

```text
Validating: specs/029-spec-validation-linting/spec.md

  ERRORS (1)
  ├─ Line 45: Missing acceptance scenarios for User Story 3
  │  Suggestion: Add **Given/When/Then** scenarios under the user story

  WARNINGS (2)
  ├─ Line 12: [NEEDS CLARIFICATION] marker found
  ├─ Line 78: FR-003 doesn't follow naming convention

  INFO (1)
  └─ Feature branch format could be improved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quality Score: 72/100
Status: FAIL (1 error, 2 warnings, 1 info)
```

### JSON

```json
{
  "spec_path": "specs/029-spec-validation-linting/spec.md",
  "status": "fail",
  "quality_score": 72,
  "error_count": 1,
  "warning_count": 2,
  "info_count": 1,
  "issues": [
    {
      "rule_id": "missing-acceptance-scenarios",
      "severity": "error",
      "line_number": 45,
      "message": "Missing acceptance scenarios for User Story 3",
      "suggestion": "Add **Given/When/Then** scenarios under the user story"
    }
  ],
  "validated_at": "2026-01-15T10:30:00Z"
}
```

## Batch Output (--all)

### Human

```text
Spec Validation Summary

| Spec | Score | Status | Errors | Warnings |
|------|-------|--------|--------|----------|
| 029-spec-validation-linting | 72 | FAIL | 1 | 2 |
| 028-docs-tutorial-refresh | 95 | PASS | 0 | 1 |
| 027-template-context | 100 | PASS | 0 | 0 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 3 specs | Passed: 2 | Failed: 1 | Avg Score: 89
```

### JSON

```json
{
  "summary": {
    "total_specs": 3,
    "passed": 2,
    "failed": 1,
    "average_score": 89
  },
  "results": [
    { /* ValidationResult */ },
    { /* ValidationResult */ }
  ]
}
```

## Usage Examples

```bash
# Validate single spec
doit validate specs/029-spec-validation-linting/spec.md

# Validate all specs
doit validate --all

# JSON output for CI
doit validate --all --format=json

# Only show errors
doit validate --all --quiet

# Validate from different directory
doit validate --path=/path/to/project --all
```
