"""Validation service for spec file validation."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.validation_models import ValidationConfig, ValidationResult
from .config_loader import load_validation_config
from .rule_engine import RuleEngine
from .score_calculator import ScoreCalculator


class ValidationService:
    """Orchestrates spec file validation.

    Coordinates rule loading, spec parsing, and result aggregation.
    """

    # Default specs directory name
    SPECS_DIR = "specs"

    def __init__(
        self,
        project_root: Optional[Path] = None,
        config: Optional[ValidationConfig] = None,
    ) -> None:
        """Initialize validation service.

        Args:
            project_root: Root directory for spec discovery. Defaults to cwd.
            config: Validation configuration. Uses defaults if None.
                    If None, attempts to load from .doit/validation-rules.yaml.
        """
        self.project_root = project_root or Path.cwd()
        self.config = config or load_validation_config(self.project_root)
        self.rule_engine = RuleEngine(config=self.config)
        self.score_calculator = ScoreCalculator()

    def validate_file(self, spec_path: Path) -> ValidationResult:
        """Validate a single spec file.

        Args:
            spec_path: Path to the spec file to validate.

        Returns:
            ValidationResult with all issues found.

        Raises:
            FileNotFoundError: If spec_path doesn't exist.
            ValueError: If file is not a valid markdown file.
        """
        # Ensure path is absolute
        if not spec_path.is_absolute():
            spec_path = self.project_root / spec_path

        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        if not spec_path.suffix.lower() == ".md":
            raise ValueError(f"Not a markdown file: {spec_path}")

        # Read file content
        try:
            content = spec_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise ValueError(f"Could not read file: {e}") from e

        # Handle empty files
        if not content.strip():
            result = ValidationResult(
                spec_path=str(spec_path),
                validated_at=datetime.now(),
            )
            from ..models.validation_models import Severity, ValidationIssue

            result.add_issue(
                ValidationIssue(
                    rule_id="empty-file",
                    severity=Severity.ERROR,
                    line_number=0,
                    message="Spec file is empty",
                    suggestion="Add content following the spec template structure",
                )
            )
            result.quality_score = 0
            return result

        # Evaluate rules
        issues = self.rule_engine.evaluate(content, spec_path)

        # Calculate score
        score = self.score_calculator.calculate(issues)

        # Create result
        result = ValidationResult(
            spec_path=str(spec_path),
            issues=issues,
            quality_score=score,
            validated_at=datetime.now(),
        )

        return result

    def validate_directory(self, specs_dir: Path) -> list[ValidationResult]:
        """Validate all spec files in a directory.

        Args:
            specs_dir: Directory containing spec files.

        Returns:
            List of ValidationResult, one per spec file found.
        """
        if not specs_dir.is_absolute():
            specs_dir = self.project_root / specs_dir

        if not specs_dir.exists():
            return []

        results: list[ValidationResult] = []

        # Find all spec.md files in subdirectories
        for spec_file in sorted(specs_dir.rglob("spec.md")):
            try:
                result = self.validate_file(spec_file)
                results.append(result)
            except (FileNotFoundError, ValueError) as e:
                # Create error result for unreadable files
                from ..models.validation_models import Severity, ValidationIssue

                result = ValidationResult(
                    spec_path=str(spec_file),
                    validated_at=datetime.now(),
                )
                result.add_issue(
                    ValidationIssue(
                        rule_id="file-error",
                        severity=Severity.ERROR,
                        line_number=0,
                        message=str(e),
                        suggestion="Check file permissions and encoding",
                    )
                )
                result.quality_score = 0
                results.append(result)

        return results

    def validate_all(self) -> list[ValidationResult]:
        """Validate all specs in project's specs/ directory.

        Returns:
            List of ValidationResult for all specs found.
        """
        specs_dir = self.project_root / self.SPECS_DIR
        return self.validate_directory(specs_dir)

    def get_summary(self, results: list[ValidationResult]) -> dict:
        """Generate summary statistics for multiple results.

        Args:
            results: List of validation results.

        Returns:
            Dict with total_specs, passed, warned, failed, avg_score.
        """
        if not results:
            return {
                "total_specs": 0,
                "passed": 0,
                "warned": 0,
                "failed": 0,
                "average_score": 0,
            }

        from ..models.validation_models import ValidationStatus

        passed = sum(1 for r in results if r.status == ValidationStatus.PASS)
        warned = sum(1 for r in results if r.status == ValidationStatus.WARN)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAIL)
        avg_score = sum(r.quality_score for r in results) // len(results)

        return {
            "total_specs": len(results),
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "average_score": avg_score,
        }
