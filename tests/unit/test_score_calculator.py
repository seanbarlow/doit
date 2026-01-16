"""Unit tests for ScoreCalculator."""

import pytest

from doit_cli.models.validation_models import Severity, ValidationIssue
from doit_cli.services.score_calculator import ScoreCalculator


class TestScoreCalculator:
    """Tests for ScoreCalculator."""

    def test_perfect_score_no_issues(self):
        """Test that no issues results in perfect score."""
        calc = ScoreCalculator()

        score = calc.calculate([])

        assert score == 100

    def test_single_error_deduction(self):
        """Test score deduction for single error."""
        calc = ScoreCalculator()

        issues = [
            ValidationIssue(
                rule_id="missing-user-scenarios",
                severity=Severity.ERROR,
                line_number=0,
                message="Missing section",
            )
        ]

        score = calc.calculate(issues)

        # Structure category weight is 20, error multiplier is 1.0
        assert score == 80

    def test_single_warning_deduction(self):
        """Test score deduction for single warning."""
        calc = ScoreCalculator()

        issues = [
            ValidationIssue(
                rule_id="fr-naming-convention",
                severity=Severity.WARNING,
                line_number=1,
                message="Naming issue",
            )
        ]

        score = calc.calculate(issues)

        # Requirements category weight is 15, warning multiplier is 0.5
        # Deduction = 15 * 0.5 = 7.5 -> score = 92
        assert score == 92

    def test_single_info_deduction(self):
        """Test score deduction for single info issue."""
        calc = ScoreCalculator()

        issues = [
            ValidationIssue(
                rule_id="feature-branch-format",
                severity=Severity.INFO,
                line_number=0,
                message="Format issue",
            )
        ]

        score = calc.calculate(issues)

        # Naming category weight is 5, info multiplier is 0.1
        # Deduction = 5 * 0.1 = 0.5 -> score = 99
        assert score == 99

    def test_category_deduction_cap(self):
        """Test that category deductions are capped."""
        calc = ScoreCalculator()

        # Multiple errors in same category should cap at category weight
        issues = [
            ValidationIssue("missing-user-scenarios", Severity.ERROR, 0, "M1"),
            ValidationIssue("missing-requirements", Severity.ERROR, 0, "M2"),
            ValidationIssue("missing-success-criteria", Severity.ERROR, 0, "M3"),
        ]

        score = calc.calculate(issues)

        # All structure issues, capped at 20
        assert score == 80

    def test_multiple_category_deductions(self):
        """Test deductions across multiple categories."""
        calc = ScoreCalculator()

        issues = [
            ValidationIssue("missing-user-scenarios", Severity.ERROR, 0, "M1"),  # structure
            ValidationIssue("fr-naming-convention", Severity.WARNING, 1, "N1"),  # requirements
        ]

        score = calc.calculate(issues)

        # Structure: 20 * 1.0 = 20
        # Requirements: 15 * 0.5 = 7.5
        # Total deduction = 27.5 -> score = 72
        assert score == 72

    def test_minimum_score_zero(self):
        """Test that score never goes below zero."""
        calc = ScoreCalculator()

        # Create many high-severity issues across all categories
        issues = [
            ValidationIssue("missing-user-scenarios", Severity.ERROR, 0, "M1"),
            ValidationIssue("missing-requirements", Severity.ERROR, 0, "M2"),
            ValidationIssue("missing-success-criteria", Severity.ERROR, 0, "M3"),
            ValidationIssue("fr-naming-convention", Severity.ERROR, 1, "N1"),
            ValidationIssue("sc-naming-convention", Severity.ERROR, 2, "N2"),
            ValidationIssue("missing-acceptance-scenarios", Severity.ERROR, 3, "A1"),
            ValidationIssue("unresolved-clarification", Severity.ERROR, 4, "C1"),
            ValidationIssue("feature-branch-format", Severity.ERROR, 5, "F1"),
        ]

        score = calc.calculate(issues)

        assert score >= 0


class TestScoreBreakdown:
    """Tests for score breakdown functionality."""

    def test_get_breakdown_empty(self):
        """Test breakdown with no issues."""
        calc = ScoreCalculator()

        breakdown = calc.get_breakdown([])

        assert breakdown == {}

    def test_get_breakdown_single_category(self):
        """Test breakdown with single category."""
        calc = ScoreCalculator()

        issues = [
            ValidationIssue("missing-user-scenarios", Severity.ERROR, 0, "M1"),
        ]

        breakdown = calc.get_breakdown(issues)

        assert "structure" in breakdown
        assert breakdown["structure"] == 20

    def test_get_breakdown_multiple_categories(self):
        """Test breakdown with multiple categories."""
        calc = ScoreCalculator()

        issues = [
            ValidationIssue("missing-user-scenarios", Severity.ERROR, 0, "M1"),
            ValidationIssue("fr-naming-convention", Severity.WARNING, 1, "N1"),
        ]

        breakdown = calc.get_breakdown(issues)

        assert "structure" in breakdown
        assert "requirements" in breakdown
        assert breakdown["structure"] == 20
        assert breakdown["requirements"] == 7  # int(15 * 0.5)


class TestScoreInterpretation:
    """Tests for score interpretation."""

    def test_excellent_score(self):
        """Test interpretation for excellent scores."""
        calc = ScoreCalculator()

        assert "Excellent" in calc.get_score_interpretation(100)
        assert "Excellent" in calc.get_score_interpretation(95)
        assert "Excellent" in calc.get_score_interpretation(90)

    def test_good_score(self):
        """Test interpretation for good scores."""
        calc = ScoreCalculator()

        assert "Good" in calc.get_score_interpretation(89)
        assert "Good" in calc.get_score_interpretation(75)
        assert "Good" in calc.get_score_interpretation(70)

    def test_fair_score(self):
        """Test interpretation for fair scores."""
        calc = ScoreCalculator()

        assert "Fair" in calc.get_score_interpretation(69)
        assert "Fair" in calc.get_score_interpretation(55)
        assert "Fair" in calc.get_score_interpretation(50)

    def test_poor_score(self):
        """Test interpretation for poor scores."""
        calc = ScoreCalculator()

        assert "Poor" in calc.get_score_interpretation(49)
        assert "Poor" in calc.get_score_interpretation(25)
        assert "Poor" in calc.get_score_interpretation(0)


class TestStatusFromScore:
    """Tests for status determination from score."""

    def test_pass_status(self):
        """Test PASS status for high scores."""
        calc = ScoreCalculator()

        assert calc.get_status_from_score(100) == "PASS"
        assert calc.get_status_from_score(80) == "PASS"
        assert calc.get_status_from_score(70) == "PASS"

    def test_warn_status(self):
        """Test WARN status for medium scores."""
        calc = ScoreCalculator()

        assert calc.get_status_from_score(69) == "WARN"
        assert calc.get_status_from_score(60) == "WARN"
        assert calc.get_status_from_score(50) == "WARN"

    def test_fail_status(self):
        """Test FAIL status for low scores."""
        calc = ScoreCalculator()

        assert calc.get_status_from_score(49) == "FAIL"
        assert calc.get_status_from_score(25) == "FAIL"
        assert calc.get_status_from_score(0) == "FAIL"
