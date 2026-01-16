"""Quality score calculator for spec validation."""

from ..models.validation_models import Severity, ValidationIssue


class ScoreCalculator:
    """Calculates quality scores from validation issues.

    Uses weighted category scoring where each issue deducts points
    based on its category and severity. The score is deterministic -
    the same issues always produce the same score.
    """

    # Category weights (how much each category affects score)
    CATEGORY_WEIGHTS: dict[str, int] = {
        "structure": 20,  # Missing required sections
        "requirements": 15,  # Naming convention violations
        "acceptance": 10,  # Missing scenarios
        "clarity": 5,  # Unresolved markers
        "naming": 5,  # Format violations
    }

    # Severity multipliers
    SEVERITY_MULTIPLIERS: dict[Severity, float] = {
        Severity.ERROR: 1.0,  # Full weight deduction
        Severity.WARNING: 0.5,  # Half weight deduction
        Severity.INFO: 0.1,  # Minor deduction
    }

    # Default weight for unknown categories
    DEFAULT_WEIGHT: int = 5

    def calculate(self, issues: list[ValidationIssue]) -> int:
        """Calculate quality score from issues.

        Score = 100 - sum(deductions)

        For each issue:
            deduction = CATEGORY_WEIGHTS[category] * SEVERITY_MULTIPLIERS[severity]

        Multiple issues in same category are additive but capped at category weight.

        Args:
            issues: List of validation issues found.

        Returns:
            Integer score 0-100 (100 = perfect, 0 = many issues).
        """
        if not issues:
            return 100

        category_deductions: dict[str, float] = {}

        for issue in issues:
            category = self._get_category(issue.rule_id)
            weight = self.CATEGORY_WEIGHTS.get(category, self.DEFAULT_WEIGHT)
            multiplier = self.SEVERITY_MULTIPLIERS.get(issue.severity, 0.5)
            deduction = weight * multiplier

            # Accumulate per category (capped at category weight)
            current = category_deductions.get(category, 0.0)
            category_deductions[category] = min(current + deduction, float(weight))

        # Sum all category deductions
        total_deduction = sum(category_deductions.values())

        # Return score clamped to 0-100
        return max(0, int(100 - total_deduction))

    def get_breakdown(self, issues: list[ValidationIssue]) -> dict[str, int]:
        """Get score breakdown by category.

        Args:
            issues: List of validation issues.

        Returns:
            Dict mapping category to points deducted.
        """
        breakdown: dict[str, int] = {}

        for issue in issues:
            category = self._get_category(issue.rule_id)
            weight = self.CATEGORY_WEIGHTS.get(category, self.DEFAULT_WEIGHT)
            multiplier = self.SEVERITY_MULTIPLIERS.get(issue.severity, 0.5)
            deduction = int(weight * multiplier)

            current = breakdown.get(category, 0)
            max_for_category = self.CATEGORY_WEIGHTS.get(category, self.DEFAULT_WEIGHT)
            breakdown[category] = min(current + deduction, max_for_category)

        return breakdown

    def _get_category(self, rule_id: str) -> str:
        """Determine category from rule ID.

        Args:
            rule_id: The rule identifier.

        Returns:
            Category name.
        """
        # Map rule IDs to categories based on naming patterns
        category_patterns = {
            "structure": [
                "missing-user-scenarios",
                "missing-requirements",
                "missing-success-criteria",
            ],
            "requirements": [
                "fr-naming-convention",
                "sc-naming-convention",
            ],
            "acceptance": [
                "missing-acceptance-scenarios",
                "incomplete-given-when-then",
            ],
            "clarity": [
                "unresolved-clarification",
                "todo-in-approved-spec",
            ],
            "naming": [
                "feature-branch-format",
            ],
        }

        for category, rule_ids in category_patterns.items():
            if rule_id in rule_ids:
                return category

        # Default to category based on naming heuristics
        if "missing" in rule_id.lower():
            return "structure"
        if "naming" in rule_id.lower() or "convention" in rule_id.lower():
            return "requirements"
        if "acceptance" in rule_id.lower() or "scenario" in rule_id.lower():
            return "acceptance"
        if "todo" in rule_id.lower() or "clarification" in rule_id.lower():
            return "clarity"

        return "naming"  # Default category

    def get_score_interpretation(self, score: int) -> str:
        """Get interpretation text for a score.

        Args:
            score: Quality score 0-100.

        Returns:
            Interpretation string.
        """
        if score >= 90:
            return "Excellent - minor or no issues"
        if score >= 70:
            return "Good - some warnings, no errors"
        if score >= 50:
            return "Fair - has errors or many warnings"
        return "Poor - multiple critical issues"

    def get_status_from_score(self, score: int) -> str:
        """Get status string from score.

        Args:
            score: Quality score 0-100.

        Returns:
            Status string (PASS, WARN, or FAIL).
        """
        if score >= 70:
            return "PASS"
        if score >= 50:
            return "WARN"
        return "FAIL"
