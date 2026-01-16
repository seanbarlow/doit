# Contract: RuleEngine

**Module**: `src/doit_cli/services/rule_engine.py`

## Overview

Evaluates validation rules against spec file content. Handles both builtin and custom rules.

## Interface

```python
class RuleEngine:
    """Evaluates validation rules against spec content."""

    def __init__(self, config: ValidationConfig | None = None) -> None:
        """Initialize rule engine.

        Args:
            config: Validation configuration. Uses defaults if None.
        """

    def get_rules(self) -> list[ValidationRule]:
        """Get all active rules (builtin + custom, minus disabled).

        Returns:
            List of ValidationRule to apply.
        """

    def evaluate(
        self,
        content: str,
        spec_path: Path
    ) -> list[ValidationIssue]:
        """Evaluate all rules against spec content.

        Args:
            content: Full text content of spec file.
            spec_path: Path to spec (for context in messages).

        Returns:
            List of ValidationIssue for all violations found.
        """

    def evaluate_rule(
        self,
        rule: ValidationRule,
        content: str,
        spec_path: Path
    ) -> list[ValidationIssue]:
        """Evaluate a single rule against content.

        Args:
            rule: The rule to evaluate.
            content: Spec file content.
            spec_path: Path for context.

        Returns:
            List of issues found (empty if rule passes).
        """
```

## Rule Evaluation Logic

### Structure Rules (missing sections)

```python
def check_section_present(content: str, section_name: str) -> bool:
    """Check if ## Section Name exists."""
    pattern = rf"^##\s+{re.escape(section_name)}"
    return bool(re.search(pattern, content, re.MULTILINE))
```

### Pattern Rules (regex matching)

```python
def check_pattern(content: str, pattern: str, must_match: bool) -> list[int]:
    """Find lines matching/not matching pattern.

    Returns line numbers where violation occurs.
    """
```

### Count Rules (occurrence limits)

```python
def check_count(content: str, pattern: str, max_count: int) -> bool:
    """Check if pattern occurs more than max_count times."""
    matches = re.findall(pattern, content, re.MULTILINE)
    return len(matches) <= max_count
```

## Builtin Rules

| ID | Check Type | Pattern/Section |
|----|------------|-----------------|
| missing-user-scenarios | section | "User Scenarios" |
| missing-requirements | section | "Requirements" |
| missing-success-criteria | section | "Success Criteria" |
| fr-naming-convention | pattern | `^- \*\*FR-\d{3}\*\*:` |
| sc-naming-convention | pattern | `^- \*\*SC-\d{3}\*\*:` |
| missing-acceptance-scenarios | custom | Check user stories have scenarios |
| unresolved-clarification | pattern | `\[NEEDS CLARIFICATION` |
| todo-in-approved-spec | pattern | `TODO\|FIXME` (only if status != Draft) |

## Dependencies

- `ValidationConfig`: For rule overrides and custom rules
- `builtin_rules`: Module with default rule definitions
