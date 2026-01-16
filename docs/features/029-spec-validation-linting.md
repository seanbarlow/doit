# Spec Validation and Linting

**Completed**: 2026-01-15
**Branch**: 029-spec-validation-linting
**PR**: #277

## Overview

Add a `doit validate` command that validates spec files against quality standards before planning and implementation. Catches specification errors early, enforces naming conventions, and provides a quality score for each spec.

## Quick Start

```bash
# Validate a single spec file
doit validate specs/029-spec-validation-linting/spec.md

# Validate a spec directory
doit validate specs/029-spec-validation-linting/

# Validate all specs
doit validate --all

# Output as JSON (for CI integration)
doit validate --all --json
```

## Validation Rules

### Built-in Rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `missing-user-scenarios` | Error | Spec must include a User Scenarios section |
| `missing-requirements` | Error | Spec must include a Requirements section |
| `missing-success-criteria` | Error | Spec must include a Success Criteria section |
| `fr-naming-convention` | Warning | Functional requirements should follow FR-XXX pattern |
| `sc-naming-convention` | Warning | Success criteria should follow SC-XXX pattern |
| `missing-acceptance-scenarios` | Warning | User stories should have Given/When/Then scenarios |
| `unresolved-clarification` | Warning | Spec should not have [NEEDS CLARIFICATION] markers |
| `todo-in-approved-spec` | Warning | Approved specs should not have TODO markers |
| `feature-branch-format` | Info | Feature branch should follow NNN-feature-name format |

### Quality Score

Quality score (0-100) is calculated based on weighted issues:
- Errors: -20 points each
- Warnings: -10 points each
- Info: -5 points each

## Custom Rules Configuration

Create `.doit/validation-rules.yaml` to customize validation:

```yaml
version: "1.0"
enabled: true

# Disable specific rules
disabled_rules:
  - feature-branch-format

# Override rule severity
overrides:
  - rule: todo-in-approved-spec
    severity: info

# Add custom pattern rules
custom_rules:
  - name: require-overview
    description: Spec must have an Overview section
    pattern: "^## Overview"
    severity: warning
    category: structure
    check: present

  - name: no-placeholder
    description: No placeholder text allowed
    pattern: '\[PLACEHOLDER\]'
    severity: error
    category: clarity
    check: absent
```

## Pre-Commit Hook Integration

The validation is integrated with git pre-commit hooks. Configure in `.doit/config/hooks.yaml`:

```yaml
version: 1
pre_commit:
  enabled: true
  require_spec: true
  validate_spec: true
  validate_spec_threshold: 70  # Minimum quality score
```

## Technical Details

### Architecture

- **RuleEngine** (`src/doit_cli/services/rule_engine.py`): Evaluates validation rules
- **ValidationService** (`src/doit_cli/services/validation_service.py`): Orchestrates validation
- **ScoreCalculator** (`src/doit_cli/services/score_calculator.py`): Calculates quality scores
- **ConfigLoader** (`src/doit_cli/services/config_loader.py`): Loads custom rules configuration
- **ReportGenerator** (`src/doit_cli/services/report_generator.py`): Formats output

### Files

- `src/doit_cli/cli/validate_command.py` - CLI command
- `src/doit_cli/models/validation_models.py` - Data models
- `src/doit_cli/rules/builtin_rules.py` - Built-in validation rules
- `templates/config/validation-rules.yaml` - Configuration template

## Related Issues

- Epic: #272
- Features: #273, #274, #275, #276
