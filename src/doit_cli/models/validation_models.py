"""Models for spec validation and linting."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    """Severity level for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationStatus(str, Enum):
    """Status of a validation result."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class ValidationRule:
    """Represents a single validation check for spec files.

    Attributes:
        id: Unique identifier (e.g., "missing-requirements")
        name: Human-readable name
        description: What this rule checks
        severity: error, warning, or info
        category: Group (structure, requirements, acceptance, clarity, naming)
        pattern: Regex pattern for matching (if applicable)
        enabled: Whether rule is active
        builtin: True for default rules, false for custom
    """

    id: str
    name: str
    description: str
    severity: Severity
    category: str
    pattern: Optional[str] = None
    enabled: bool = True
    builtin: bool = True


@dataclass
class ValidationIssue:
    """Individual problem found during validation.

    Attributes:
        rule_id: FK to ValidationRule that triggered
        severity: Severity level (error, warning, info)
        line_number: Line in spec where issue found (0 if N/A)
        message: Human-readable description of problem
        suggestion: How to fix the issue (optional)
    """

    rule_id: str
    severity: Severity
    line_number: int
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Aggregate result of validating a single spec file.

    Attributes:
        spec_path: Path to validated spec file
        issues: List of validation issues found
        quality_score: 0-100 score based on weighted issues
        validated_at: Timestamp of validation
    """

    spec_path: str
    issues: list[ValidationIssue] = field(default_factory=list)
    quality_score: int = 100
    validated_at: datetime = field(default_factory=datetime.now)

    @property
    def status(self) -> ValidationStatus:
        """Derive status from issue counts."""
        if self.error_count > 0:
            return ValidationStatus.FAIL
        if self.warning_count > 0:
            return ValidationStatus.WARN
        return ValidationStatus.PASS

    @property
    def error_count(self) -> int:
        """Count error-severity issues."""
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count warning-severity issues."""
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        """Count info-severity issues."""
        return sum(1 for i in self.issues if i.severity == Severity.INFO)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add an issue to the result."""
        self.issues.append(issue)


@dataclass
class RuleOverride:
    """Override for built-in rule behavior.

    Attributes:
        rule: Rule ID to override
        severity: New severity level
    """

    rule: str
    severity: str


@dataclass
class CustomRule:
    """User-defined validation rule.

    Attributes:
        name: Unique name (becomes ID)
        description: What this checks
        pattern: Regex to match (required or absent sections)
        severity: error, warning, or info
        category: Logical grouping
        check: "present" (must match), "absent" (must not match), or "count"
        max: For check="count", maximum occurrences
    """

    name: str
    description: str
    pattern: str
    severity: str
    category: str
    check: str = "present"
    max: Optional[int] = None


@dataclass
class ValidationConfig:
    """Project-level validation configuration.

    Loaded from .doit/validation-rules.yaml.

    Attributes:
        path: Path to configuration file
        version: Schema version (e.g., "1.0")
        enabled: Whether validation is enabled
        disabled_rules: Rule IDs to skip
        overrides: Severity overrides for built-in rules
        custom_rules: User-defined validation rules
    """

    path: str = ""
    version: str = "1.0"
    enabled: bool = True
    disabled_rules: list[str] = field(default_factory=list)
    overrides: list[RuleOverride] = field(default_factory=list)
    custom_rules: list[CustomRule] = field(default_factory=list)

    @classmethod
    def default(cls) -> "ValidationConfig":
        """Return default configuration with no customizations."""
        return cls()
