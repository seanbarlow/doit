"""Built-in validation rules for spec files."""

from dataclasses import replace

from ..models.validation_models import Severity, ValidationRule

# Default validation rules
BUILTIN_RULES: list[ValidationRule] = [
    # Structure rules (error severity)
    ValidationRule(
        id="missing-user-scenarios",
        name="Missing User Scenarios",
        description="Spec must include a User Scenarios section",
        severity=Severity.ERROR,
        category="structure",
        pattern=r"^##\s+User\s+Scenarios",
    ),
    ValidationRule(
        id="missing-requirements",
        name="Missing Requirements",
        description="Spec must include a Requirements section",
        severity=Severity.ERROR,
        category="structure",
        pattern=r"^##\s+Requirements",
    ),
    ValidationRule(
        id="missing-success-criteria",
        name="Missing Success Criteria",
        description="Spec must include a Success Criteria section",
        severity=Severity.ERROR,
        category="structure",
        pattern=r"^##\s+Success\s+Criteria",
    ),
    # Requirements rules (warning severity)
    ValidationRule(
        id="fr-naming-convention",
        name="FR Naming Convention",
        description="Functional requirements should follow FR-XXX pattern",
        severity=Severity.WARNING,
        category="requirements",
        pattern=r"^\s*-\s+\*\*FR-\d{3}\*\*:",
    ),
    ValidationRule(
        id="sc-naming-convention",
        name="SC Naming Convention",
        description="Success criteria should follow SC-XXX pattern",
        severity=Severity.WARNING,
        category="requirements",
        pattern=r"^\s*-\s+\*\*SC-\d{3}\*\*:",
    ),
    # Acceptance rules (warning severity)
    ValidationRule(
        id="missing-acceptance-scenarios",
        name="Missing Acceptance Scenarios",
        description="User stories should have acceptance scenarios with Given/When/Then",
        severity=Severity.WARNING,
        category="acceptance",
        pattern=r"\*\*Given\*\*.*\*\*When\*\*.*\*\*Then\*\*",
    ),
    ValidationRule(
        id="incomplete-given-when-then",
        name="Incomplete Given/When/Then",
        description="Acceptance scenarios should have complete Given/When/Then format",
        severity=Severity.INFO,
        category="acceptance",
        pattern=r"Given.*When.*Then",
    ),
    # Clarity rules (warning severity)
    ValidationRule(
        id="unresolved-clarification",
        name="Unresolved Clarification",
        description="Spec should not have [NEEDS CLARIFICATION] markers",
        severity=Severity.WARNING,
        category="clarity",
        pattern=r"\[NEEDS\s+CLARIFICATION",
    ),
    ValidationRule(
        id="todo-in-approved-spec",
        name="TODO in Approved Spec",
        description="Approved specs should not have TODO or FIXME markers",
        severity=Severity.WARNING,
        category="clarity",
        pattern=r"\b(TODO|FIXME)\b",
    ),
    # Naming rules (info severity)
    ValidationRule(
        id="feature-branch-format",
        name="Feature Branch Format",
        description="Feature branch should follow NNN-feature-name format",
        severity=Severity.INFO,
        category="naming",
        pattern=r"\*\*Feature\s+Branch\*\*:\s+`\d{3}-[\w-]+`",
    ),
    # Traceability rules (cross-reference validation)
    ValidationRule(
        id="orphaned-task-reference",
        name="Orphaned Task Reference",
        description="Task references a requirement that does not exist in spec.md",
        severity=Severity.ERROR,
        category="traceability",
        pattern=None,  # Requires cross-file analysis
    ),
    ValidationRule(
        id="uncovered-requirement",
        name="Uncovered Requirement",
        description="Requirement has no linked tasks in tasks.md",
        severity=Severity.WARNING,
        category="traceability",
        pattern=None,  # Requires cross-file analysis
    ),
]


def get_builtin_rules() -> list[ValidationRule]:
    """Get all built-in validation rules.

    Returns:
        List of ValidationRule objects with default configuration.
        Each call returns fresh copies to prevent mutation issues.
    """
    return [replace(rule) for rule in BUILTIN_RULES]


def get_rule_by_id(rule_id: str) -> ValidationRule | None:
    """Get a specific built-in rule by ID.

    Args:
        rule_id: The unique identifier of the rule.

    Returns:
        The ValidationRule if found, None otherwise.
    """
    for rule in BUILTIN_RULES:
        if rule.id == rule_id:
            return rule
    return None


def get_rules_by_category(category: str) -> list[ValidationRule]:
    """Get all built-in rules in a category.

    Args:
        category: Category name (structure, requirements, acceptance, clarity, naming).

    Returns:
        List of ValidationRule objects in the category.
    """
    return [rule for rule in BUILTIN_RULES if rule.category == category]


def get_rules_by_severity(severity: Severity) -> list[ValidationRule]:
    """Get all built-in rules with a specific severity.

    Args:
        severity: Severity level to filter by.

    Returns:
        List of ValidationRule objects with that severity.
    """
    return [rule for rule in BUILTIN_RULES if rule.severity == severity]
