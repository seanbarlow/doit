"""Rule engine for evaluating validation rules against spec content."""

import re
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from ..models.validation_models import (
    Severity,
    ValidationConfig,
    ValidationIssue,
    ValidationRule,
)
from ..rules.builtin_rules import get_builtin_rules

if TYPE_CHECKING:
    from .crossref_service import CrossReferenceService


class RuleEngine:
    """Evaluates validation rules against spec content."""

    def __init__(self, config: Optional[ValidationConfig] = None) -> None:
        """Initialize rule engine.

        Args:
            config: Validation configuration. Uses defaults if None.
        """
        self.config = config or ValidationConfig.default()
        self._rules: list[ValidationRule] = []
        self._load_rules()

    def _load_rules(self) -> None:
        """Load and configure all rules."""
        # Start with builtin rules
        self._rules = get_builtin_rules()

        # Apply disabled rules
        for rule in self._rules:
            if rule.id in self.config.disabled_rules:
                rule.enabled = False

        # Apply severity overrides
        for override in self.config.overrides:
            for rule in self._rules:
                if rule.id == override.rule:
                    rule.severity = Severity(override.severity)
                    break

        # Add custom rules
        for custom in self.config.custom_rules:
            custom_rule = ValidationRule(
                id=custom.name,
                name=custom.name.replace("-", " ").title(),
                description=custom.description,
                severity=Severity(custom.severity),
                category=custom.category,
                pattern=custom.pattern,
                enabled=True,
                builtin=False,
            )
            self._rules.append(custom_rule)

    def get_rules(self) -> list[ValidationRule]:
        """Get all active rules (builtin + custom, minus disabled).

        Returns:
            List of ValidationRule to apply.
        """
        return [rule for rule in self._rules if rule.enabled]

    def evaluate(
        self,
        content: str,
        spec_path: Path,
    ) -> list[ValidationIssue]:
        """Evaluate all rules against spec content.

        Args:
            content: Full text content of spec file.
            spec_path: Path to spec (for context in messages).

        Returns:
            List of ValidationIssue for all violations found.
        """
        issues: list[ValidationIssue] = []

        for rule in self.get_rules():
            rule_issues = self.evaluate_rule(rule, content, spec_path)
            issues.extend(rule_issues)

        return issues

    def evaluate_rule(
        self,
        rule: ValidationRule,
        content: str,
        spec_path: Path,
    ) -> list[ValidationIssue]:
        """Evaluate a single rule against content.

        Args:
            rule: The rule to evaluate.
            content: Spec file content.
            spec_path: Path for context.

        Returns:
            List of issues found (empty if rule passes).
        """
        issues: list[ValidationIssue] = []

        # Traceability rules have no pattern and require cross-file analysis
        if rule.category == "traceability":
            issues = self._check_traceability(rule, spec_path)
            return issues

        if not rule.pattern:
            return issues

        # Determine rule type based on category and pattern
        if rule.category == "structure":
            # Structure rules check for presence of sections
            issues = self._check_section_present(rule, content)
        elif rule.category in ("requirements", "naming"):
            # These rules check that patterns ARE followed where applicable
            issues = self._check_pattern_compliance(rule, content)
        elif rule.category == "acceptance":
            # Check user stories have acceptance scenarios
            issues = self._check_acceptance_scenarios(rule, content)
        elif rule.category == "clarity":
            # Clarity rules check for absence of problematic patterns
            issues = self._check_pattern_absent(rule, content)

        return issues

    def _check_section_present(
        self,
        rule: ValidationRule,
        content: str,
    ) -> list[ValidationIssue]:
        """Check if a required section is present.

        Args:
            rule: The structure rule to check.
            content: Spec content.

        Returns:
            List with one issue if section missing, empty otherwise.
        """
        if not rule.pattern:
            return []

        if not re.search(rule.pattern, content, re.MULTILINE | re.IGNORECASE):
            return [
                ValidationIssue(
                    rule_id=rule.id,
                    severity=rule.severity,
                    line_number=0,
                    message=f"{rule.name}: {rule.description}",
                    suggestion=f"Add a '## {rule.name.replace('Missing ', '')}' section to your spec",
                )
            ]
        return []

    def _check_pattern_compliance(
        self,
        rule: ValidationRule,
        content: str,
    ) -> list[ValidationIssue]:
        """Check that patterns are followed where applicable.

        For FR/SC naming, we check if there ARE requirements/criteria
        that don't follow the naming convention.

        Args:
            rule: The pattern rule to check.
            content: Spec content.

        Returns:
            List of issues for non-compliant patterns.
        """
        issues: list[ValidationIssue] = []

        if not rule.pattern:
            return issues

        # Find the relevant section
        lines = content.split("\n")

        # For FR naming, look in Requirements section
        if rule.id == "fr-naming-convention":
            in_section = False
            for i, line in enumerate(lines):
                if re.match(r"^##\s+Requirements", line, re.IGNORECASE):
                    in_section = True
                    continue
                if in_section and line.startswith("##"):
                    in_section = False
                if in_section and line.strip().startswith("- **FR-"):
                    # Check if it follows the pattern
                    if not re.match(rule.pattern, line):
                        issues.append(
                            ValidationIssue(
                                rule_id=rule.id,
                                severity=rule.severity,
                                line_number=i + 1,
                                message=f"Line {i + 1}: {rule.description}",
                                suggestion="Use format: - **FR-XXX**: Description",
                            )
                        )

        # For SC naming, look in Success Criteria section
        elif rule.id == "sc-naming-convention":
            in_section = False
            for i, line in enumerate(lines):
                if re.match(r"^##\s+Success\s+Criteria", line, re.IGNORECASE):
                    in_section = True
                    continue
                if in_section and line.startswith("##"):
                    in_section = False
                if in_section and line.strip().startswith("- **SC-"):
                    if not re.match(rule.pattern, line):
                        issues.append(
                            ValidationIssue(
                                rule_id=rule.id,
                                severity=rule.severity,
                                line_number=i + 1,
                                message=f"Line {i + 1}: {rule.description}",
                                suggestion="Use format: - **SC-XXX**: Description",
                            )
                        )

        # For feature branch format
        elif rule.id == "feature-branch-format":
            if not re.search(rule.pattern, content, re.MULTILINE):
                # Check if there's a feature branch line at all
                if re.search(r"\*\*Feature\s+Branch\*\*:", content):
                    issues.append(
                        ValidationIssue(
                            rule_id=rule.id,
                            severity=rule.severity,
                            line_number=0,
                            message=rule.description,
                            suggestion="Use format: `NNN-feature-name` (e.g., `029-spec-validation`)",
                        )
                    )

        return issues

    def _check_acceptance_scenarios(
        self,
        rule: ValidationRule,
        content: str,
    ) -> list[ValidationIssue]:
        """Check that user stories have acceptance scenarios.

        Args:
            rule: The acceptance rule to check.
            content: Spec content.

        Returns:
            List of issues for user stories without scenarios.
        """
        issues: list[ValidationIssue] = []

        if rule.id != "missing-acceptance-scenarios":
            return issues

        # Find user story sections
        lines = content.split("\n")
        current_story = None
        story_line = 0
        has_scenarios = False

        for i, line in enumerate(lines):
            # Detect user story headers
            if re.match(r"^###\s+User\s+Story\s+\d+", line, re.IGNORECASE):
                # Check previous story
                if current_story and not has_scenarios:
                    issues.append(
                        ValidationIssue(
                            rule_id=rule.id,
                            severity=rule.severity,
                            line_number=story_line,
                            message=f"{current_story} has no acceptance scenarios",
                            suggestion="Add **Given/When/Then** scenarios under the user story",
                        )
                    )
                current_story = line.strip().lstrip("#").strip()
                story_line = i + 1
                has_scenarios = False

            # Detect acceptance scenarios
            if current_story and re.search(
                r"\*\*Given\*\*.*\*\*When\*\*.*\*\*Then\*\*", line
            ):
                has_scenarios = True

            # Detect next section (non-user story)
            if current_story and re.match(r"^##[^#]", line):
                if not has_scenarios:
                    issues.append(
                        ValidationIssue(
                            rule_id=rule.id,
                            severity=rule.severity,
                            line_number=story_line,
                            message=f"{current_story} has no acceptance scenarios",
                            suggestion="Add **Given/When/Then** scenarios under the user story",
                        )
                    )
                current_story = None
                has_scenarios = False

        # Check last story
        if current_story and not has_scenarios:
            issues.append(
                ValidationIssue(
                    rule_id=rule.id,
                    severity=rule.severity,
                    line_number=story_line,
                    message=f"{current_story} has no acceptance scenarios",
                    suggestion="Add **Given/When/Then** scenarios under the user story",
                )
            )

        return issues

    def _check_pattern_absent(
        self,
        rule: ValidationRule,
        content: str,
    ) -> list[ValidationIssue]:
        """Check that problematic patterns are absent.

        Args:
            rule: The clarity rule to check.
            content: Spec content.

        Returns:
            List of issues where pattern is found.
        """
        issues: list[ValidationIssue] = []

        if not rule.pattern:
            return issues

        # Special handling for TODO/FIXME in approved specs
        if rule.id == "todo-in-approved-spec":
            # Check if spec is in draft status
            if re.search(r"\*\*Status\*\*:\s*Draft", content, re.IGNORECASE):
                return []  # Don't flag TODOs in draft specs

        lines = content.split("\n")
        for i, line in enumerate(lines):
            matches = re.findall(rule.pattern, line, re.IGNORECASE)
            if matches:
                issues.append(
                    ValidationIssue(
                        rule_id=rule.id,
                        severity=rule.severity,
                        line_number=i + 1,
                        message=f"Line {i + 1}: {rule.description}",
                        suggestion=self._get_clarity_suggestion(rule.id),
                    )
                )

        return issues

    def _get_clarity_suggestion(self, rule_id: str) -> str:
        """Get suggestion text for clarity rules.

        Args:
            rule_id: The rule ID.

        Returns:
            Suggestion text.
        """
        suggestions = {
            "unresolved-clarification": "Resolve the ambiguity and remove the [NEEDS CLARIFICATION] marker",
            "todo-in-approved-spec": "Complete the TODO item or change spec status to Draft",
        }
        return suggestions.get(rule_id, "Review and address this issue")

    def _check_traceability(
        self,
        rule: ValidationRule,
        spec_path: Path,
    ) -> list[ValidationIssue]:
        """Check cross-reference traceability between spec.md and tasks.md.

        Args:
            rule: The traceability rule to check.
            spec_path: Path to the spec file.

        Returns:
            List of issues found.
        """
        issues: list[ValidationIssue] = []

        # Determine the feature directory from spec path
        feature_dir = spec_path.parent
        tasks_path = feature_dir / "tasks.md"

        # Skip traceability checks if tasks.md doesn't exist
        if not tasks_path.exists():
            return issues

        # Import here to avoid circular imports
        from .crossref_service import CrossReferenceService

        try:
            service = CrossReferenceService()
            uncovered, orphaned = service.validate_references(spec_path=spec_path)

            if rule.id == "orphaned-task-reference":
                for task, ref_id in orphaned:
                    issues.append(
                        ValidationIssue(
                            rule_id=rule.id,
                            severity=rule.severity,
                            line_number=task.line_number,
                            message=f"Task references non-existent requirement {ref_id}",
                            suggestion=f"Verify {ref_id} exists in spec.md or remove the reference",
                        )
                    )

            elif rule.id == "uncovered-requirement":
                for req_id in uncovered:
                    issues.append(
                        ValidationIssue(
                            rule_id=rule.id,
                            severity=rule.severity,
                            line_number=0,
                            message=f"Requirement {req_id} has no linked tasks",
                            suggestion=f"Add [task description] [{req_id}] to tasks.md",
                        )
                    )

        except Exception:
            # If cross-reference validation fails, skip silently
            # (e.g., spec not found, parsing errors)
            pass

        return issues
