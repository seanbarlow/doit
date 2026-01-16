# Contract: ScoreCalculator

**Module**: `src/doit_cli/services/score_calculator.py`

## Overview

Calculates deterministic quality scores for spec files based on validation issues.

## Interface

```python
class ScoreCalculator:
    """Calculates quality scores from validation issues."""

    # Category weights (how much each category affects score)
    CATEGORY_WEIGHTS: dict[str, int] = {
        "structure": 20,      # Missing required sections
        "requirements": 15,   # Naming convention violations
        "acceptance": 10,     # Missing scenarios
        "clarity": 5,         # Unresolved markers
        "naming": 5,          # Format violations
    }

    # Severity multipliers
    SEVERITY_MULTIPLIERS: dict[str, float] = {
        "error": 1.0,         # Full weight deduction
        "warning": 0.5,       # Half weight deduction
        "info": 0.1,          # Minor deduction
    }

    def calculate(self, issues: list[ValidationIssue]) -> int:
        """Calculate quality score from issues.

        Args:
            issues: List of validation issues found.

        Returns:
            Integer score 0-100 (100 = perfect, 0 = many issues).
        """

    def get_breakdown(self, issues: list[ValidationIssue]) -> dict[str, int]:
        """Get score breakdown by category.

        Args:
            issues: List of validation issues.

        Returns:
            Dict mapping category to points deducted.
        """
```

## Scoring Algorithm

```python
def calculate(self, issues: list[ValidationIssue]) -> int:
    """
    Score = 100 - sum(deductions)

    For each issue:
        deduction = CATEGORY_WEIGHTS[category] * SEVERITY_MULTIPLIERS[severity]

    Multiple issues in same category are additive but capped at category weight.
    Example: 3 structure errors = max 20 points deducted (not 60)
    """
    score = 100
    category_deductions: dict[str, float] = {}

    for issue in issues:
        category = self._get_category(issue.rule_id)
        weight = self.CATEGORY_WEIGHTS.get(category, 5)
        multiplier = self.SEVERITY_MULTIPLIERS.get(issue.severity, 0.5)
        deduction = weight * multiplier

        # Accumulate per category
        current = category_deductions.get(category, 0)
        category_deductions[category] = min(current + deduction, weight)

    # Sum all category deductions
    total_deduction = sum(category_deductions.values())
    return max(0, int(100 - total_deduction))
```

## Score Interpretation

| Score Range | Status | Meaning |
|-------------|--------|---------|
| 90-100 | Excellent | Minor or no issues |
| 70-89 | Good | Some warnings, no errors |
| 50-69 | Fair | Has errors or many warnings |
| 0-49 | Poor | Multiple critical issues |

## Determinism Guarantee

The score calculation MUST be deterministic:
- Same issues always produce same score
- Order of issues doesn't affect result
- No randomness or time-based factors

This is verified by:
1. Unit tests with known inputs/outputs
2. Property-based testing for consistency
