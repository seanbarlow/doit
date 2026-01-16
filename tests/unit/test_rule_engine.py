"""Unit tests for RuleEngine."""

import pytest
from pathlib import Path

from doit_cli.models.validation_models import Severity, ValidationConfig
from doit_cli.services.rule_engine import RuleEngine


class TestRuleEngine:
    """Tests for RuleEngine."""

    def test_init_with_default_config(self):
        """Test initialization with default config."""
        engine = RuleEngine()

        rules = engine.get_rules()
        assert len(rules) > 0

    def test_init_with_custom_config(self):
        """Test initialization with custom config."""
        config = ValidationConfig(
            disabled_rules=["missing-user-scenarios"],
            overrides=[],
            custom_rules=[],
        )
        engine = RuleEngine(config=config)

        rules = engine.get_rules()
        rule_ids = [r.id for r in rules]
        assert "missing-user-scenarios" not in rule_ids

    def test_get_rules_returns_enabled_only(self):
        """Test that get_rules only returns enabled rules."""
        engine = RuleEngine()

        rules = engine.get_rules()
        assert all(r.enabled for r in rules)

    def test_evaluate_empty_content(self):
        """Test evaluating empty content."""
        engine = RuleEngine()

        issues = engine.evaluate("", Path("/test/spec.md"))

        # Empty content should trigger structure issues
        assert len(issues) > 0

    def test_evaluate_valid_content(self):
        """Test evaluating valid spec content."""
        engine = RuleEngine()

        content = """# Feature: Test

## User Scenarios

### User Story 1: Test Story

As a user, I want to test.

**Given** I have setup
**When** I perform action
**Then** I see result

## Requirements

- **FR-001**: First requirement
- **FR-002**: Second requirement

## Success Criteria

- **SC-001**: First criterion
- **SC-002**: Second criterion
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # Valid content should have minimal issues
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_evaluate_missing_sections(self):
        """Test evaluating content missing required sections."""
        engine = RuleEngine()

        content = """# Feature: Test

## Overview

Just an overview, missing required sections.
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # Should have errors for missing sections
        errors = [i for i in issues if i.severity == Severity.ERROR]
        # At minimum, should detect missing Requirements and Success Criteria
        assert len(errors) >= 2
        # Verify specific expected issues
        issue_ids = [i.rule_id for i in errors]
        assert "missing-requirements" in issue_ids
        assert "missing-success-criteria" in issue_ids


class TestRuleEnginePatternMatching:
    """Tests for pattern matching in RuleEngine."""

    def test_check_section_present_found(self):
        """Test section detection when section is present."""
        engine = RuleEngine()

        content = """# Feature

## User Scenarios

Some content here.
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # Should not have issue for missing user scenarios
        issue_ids = [i.rule_id for i in issues]
        assert "missing-user-scenarios" not in issue_ids

    def test_check_section_present_missing(self):
        """Test section detection when section is missing."""
        engine = RuleEngine()

        content = """# Feature

## Overview

No required sections here.
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # Should have issues for missing required sections
        issue_ids = [i.rule_id for i in issues]
        # Check that at least Requirements and Success Criteria are detected as missing
        assert "missing-requirements" in issue_ids
        assert "missing-success-criteria" in issue_ids

    def test_check_clarity_todo_in_draft(self):
        """Test that TODO in draft spec is not flagged."""
        engine = RuleEngine()

        content = """# Feature

**Status**: Draft

## User Scenarios

TODO: Add scenarios

## Requirements

TODO: Add requirements

## Success Criteria

TODO: Add criteria
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # TODO should not be flagged in draft specs
        todo_issues = [i for i in issues if i.rule_id == "todo-in-approved-spec"]
        assert len(todo_issues) == 0

    def test_check_clarity_todo_in_approved(self):
        """Test that TODO in approved spec is flagged."""
        engine = RuleEngine()

        content = """# Feature

**Status**: Approved

## User Scenarios

TODO: Finish this

## Requirements

- **FR-001**: Test

## Success Criteria

- **SC-001**: Test
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # TODO should be flagged in approved specs
        todo_issues = [i for i in issues if i.rule_id == "todo-in-approved-spec"]
        assert len(todo_issues) > 0

    def test_check_unresolved_clarification(self):
        """Test detection of unresolved clarification markers."""
        engine = RuleEngine()

        content = """# Feature

## User Scenarios

[NEEDS CLARIFICATION] What about edge cases?

## Requirements

- **FR-001**: Test

## Success Criteria

- **SC-001**: Test
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # Should flag unresolved clarification
        clarification_issues = [i for i in issues if i.rule_id == "unresolved-clarification"]
        assert len(clarification_issues) > 0
