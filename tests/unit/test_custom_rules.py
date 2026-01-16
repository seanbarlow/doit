"""Unit tests for custom validation rules."""

import pytest
from pathlib import Path

from doit_cli.models.validation_models import (
    CustomRule,
    RuleOverride,
    Severity,
    ValidationConfig,
)
from doit_cli.services.config_loader import ConfigLoader, load_validation_config
from doit_cli.services.rule_engine import RuleEngine
from doit_cli.services.validation_service import ValidationService


class TestConfigLoader:
    """Tests for ConfigLoader."""

    def test_load_default_when_no_file(self, temp_dir):
        """Test that default config is returned when file doesn't exist."""
        loader = ConfigLoader(project_root=temp_dir)
        config = loader.load()

        assert config.enabled is True
        assert config.disabled_rules == []
        assert config.overrides == []
        assert config.custom_rules == []

    def test_load_from_yaml_file(self, temp_dir):
        """Test loading config from YAML file."""
        config_dir = temp_dir / ".doit"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "validation-rules.yaml"
        config_file.write_text("""
version: "1.0"
enabled: true
disabled_rules:
  - feature-branch-format
overrides:
  - rule: todo-in-approved-spec
    severity: info
custom_rules:
  - name: require-overview
    description: Must have overview section
    pattern: "^## Overview"
    severity: warning
    category: structure
    check: present
""")

        loader = ConfigLoader(project_root=temp_dir)
        config = loader.load()

        assert config.version == "1.0"
        assert config.enabled is True
        assert "feature-branch-format" in config.disabled_rules
        assert len(config.overrides) == 1
        assert config.overrides[0].rule == "todo-in-approved-spec"
        assert config.overrides[0].severity == "info"
        assert len(config.custom_rules) == 1
        assert config.custom_rules[0].name == "require-overview"

    def test_load_invalid_yaml_returns_default(self, temp_dir):
        """Test that invalid YAML returns default config."""
        config_dir = temp_dir / ".doit"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "validation-rules.yaml"
        config_file.write_text("invalid: yaml: content: :")

        loader = ConfigLoader(project_root=temp_dir)
        config = loader.load()

        # Should return default config
        assert config.enabled is True
        assert config.disabled_rules == []


class TestRuleEngineWithCustomConfig:
    """Tests for RuleEngine with custom configuration."""

    def test_disabled_rules_not_evaluated(self):
        """Test that disabled rules are not included."""
        config = ValidationConfig(
            disabled_rules=["missing-user-scenarios", "missing-requirements"],
        )
        engine = RuleEngine(config=config)

        rules = engine.get_rules()
        rule_ids = [r.id for r in rules]

        assert "missing-user-scenarios" not in rule_ids
        assert "missing-requirements" not in rule_ids
        assert "missing-success-criteria" in rule_ids  # Not disabled

    def test_severity_override(self):
        """Test that severity overrides are applied."""
        config = ValidationConfig(
            overrides=[
                RuleOverride(rule="todo-in-approved-spec", severity="info"),
            ],
        )
        engine = RuleEngine(config=config)

        rules = engine.get_rules()
        todo_rule = next((r for r in rules if r.id == "todo-in-approved-spec"), None)

        assert todo_rule is not None
        assert todo_rule.severity == Severity.INFO

    def test_custom_rule_added(self):
        """Test that custom rules are added to the rule set."""
        config = ValidationConfig(
            custom_rules=[
                CustomRule(
                    name="require-overview",
                    description="Must have overview",
                    pattern=r"^## Overview",
                    severity="warning",
                    category="structure",
                    check="present",
                ),
            ],
        )
        engine = RuleEngine(config=config)

        rules = engine.get_rules()
        custom_rule = next((r for r in rules if r.id == "require-overview"), None)

        assert custom_rule is not None
        assert custom_rule.name == "Require Overview"
        assert custom_rule.builtin is False
        assert custom_rule.severity == Severity.WARNING

    def test_custom_rule_evaluated(self):
        """Test that custom rules are evaluated."""
        config = ValidationConfig(
            custom_rules=[
                CustomRule(
                    name="require-overview",
                    description="Must have overview section",
                    pattern=r"^## Overview",
                    severity="warning",
                    category="structure",
                    check="present",
                ),
            ],
        )
        engine = RuleEngine(config=config)

        # Content without Overview section
        content = """# Feature: Test

## User Scenarios

### User Story 1

As a user, I want to test.

- **Given** setup **When** action **Then** result

## Requirements

- **FR-001**: Test

## Success Criteria

- **SC-001**: Test
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))

        # Should have issue for missing overview
        overview_issues = [i for i in issues if i.rule_id == "require-overview"]
        assert len(overview_issues) == 1
        assert "overview" in overview_issues[0].message.lower()


class TestValidationServiceWithConfig:
    """Tests for ValidationService with custom configuration."""

    def test_loads_config_from_project_root(self, temp_dir):
        """Test that ValidationService loads config from project root."""
        config_dir = temp_dir / ".doit"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "validation-rules.yaml"
        config_file.write_text("""
version: "1.0"
disabled_rules:
  - missing-user-scenarios
""")

        service = ValidationService(project_root=temp_dir)

        assert "missing-user-scenarios" in service.config.disabled_rules

    def test_custom_rules_in_validation(self, temp_dir):
        """Test that custom rules are applied during validation."""
        # Create config with custom rule
        config_dir = temp_dir / ".doit"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "validation-rules.yaml"
        config_file.write_text("""
version: "1.0"
custom_rules:
  - name: no-placeholder
    description: No placeholder text allowed
    pattern: '\\[PLACEHOLDER\\]'
    severity: error
    category: clarity
    check: absent
""")

        # Create spec with placeholder
        spec_dir = temp_dir / "specs" / "001-test"
        spec_dir.mkdir(parents=True)
        spec_file = spec_dir / "spec.md"
        spec_file.write_text("""# Feature: Test

**Status**: In Progress

## User Scenarios

[PLACEHOLDER] Add user scenarios

## Requirements

- **FR-001**: Test

## Success Criteria

- **SC-001**: Test
""")

        service = ValidationService(project_root=temp_dir)
        result = service.validate_file(spec_file)

        # Should have custom rule violation
        placeholder_issues = [i for i in result.issues if i.rule_id == "no-placeholder"]
        assert len(placeholder_issues) > 0


class TestCustomRulePatterns:
    """Tests for custom rule pattern matching."""

    def test_present_check_finds_missing(self):
        """Test that 'present' check finds missing patterns."""
        config = ValidationConfig(
            custom_rules=[
                CustomRule(
                    name="require-technical-notes",
                    description="Must have technical notes",
                    pattern=r"^## Technical Notes",
                    severity="info",
                    category="structure",
                    check="present",
                ),
            ],
        )
        engine = RuleEngine(config=config)

        content = """# Feature: Test

## User Scenarios

### User Story 1

- **Given** setup **When** action **Then** result

## Requirements

- **FR-001**: Test

## Success Criteria

- **SC-001**: Test
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))
        tech_issues = [i for i in issues if i.rule_id == "require-technical-notes"]
        assert len(tech_issues) == 1

    def test_present_check_passes_when_found(self):
        """Test that 'present' check passes when pattern is found."""
        config = ValidationConfig(
            custom_rules=[
                CustomRule(
                    name="require-technical-notes",
                    description="Must have technical notes",
                    pattern=r"^## Technical Notes",
                    severity="info",
                    category="structure",
                    check="present",
                ),
            ],
        )
        engine = RuleEngine(config=config)

        content = """# Feature: Test

## User Scenarios

### User Story 1

- **Given** setup **When** action **Then** result

## Requirements

- **FR-001**: Test

## Success Criteria

- **SC-001**: Test

## Technical Notes

Some notes here.
"""

        issues = engine.evaluate(content, Path("/test/spec.md"))
        tech_issues = [i for i in issues if i.rule_id == "require-technical-notes"]
        assert len(tech_issues) == 0


class TestConvenienceFunction:
    """Tests for load_validation_config convenience function."""

    def test_load_validation_config(self, temp_dir):
        """Test the convenience function."""
        config = load_validation_config(temp_dir)

        assert config.enabled is True
        assert isinstance(config, ValidationConfig)
