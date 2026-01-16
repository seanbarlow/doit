# Contract: ValidationService

**Module**: `src/doit_cli/services/validation_service.py`

## Overview

Core orchestration service for spec validation. Coordinates rule loading, spec parsing, and result aggregation.

## Interface

```python
class ValidationService:
    """Orchestrates spec file validation."""

    def __init__(
        self,
        project_root: Path | None = None,
        config_path: Path | None = None
    ) -> None:
        """Initialize validation service.

        Args:
            project_root: Root directory for spec discovery. Defaults to cwd.
            config_path: Path to validation config. Defaults to .doit/validation-rules.yaml.
        """

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

    def validate_directory(self, specs_dir: Path) -> list[ValidationResult]:
        """Validate all spec files in a directory.

        Args:
            specs_dir: Directory containing spec files.

        Returns:
            List of ValidationResult, one per spec file found.
        """

    def validate_all(self) -> list[ValidationResult]:
        """Validate all specs in project's specs/ directory.

        Returns:
            List of ValidationResult for all specs found.
        """

    def get_summary(self, results: list[ValidationResult]) -> dict:
        """Generate summary statistics for multiple results.

        Args:
            results: List of validation results.

        Returns:
            Dict with total_specs, passed, warned, failed, avg_score.
        """
```

## Dependencies

- `RuleEngine`: For rule evaluation
- `ScoreCalculator`: For quality score computation
- `ValidationConfig`: Loaded at initialization

## Behavior

1. On init, load config from `.doit/validation-rules.yaml` if exists
2. On validate, parse spec file into sections
3. Apply all enabled rules via RuleEngine
4. Compute quality score via ScoreCalculator
5. Return ValidationResult with all issues

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Spec file not found | Raise FileNotFoundError |
| Empty spec file | Return result with "empty-file" error |
| Invalid markdown | Return result with "parse-error" error |
| Config file invalid | Log warning, use defaults |
