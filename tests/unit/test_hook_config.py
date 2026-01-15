"""Unit tests for HookConfig model."""

import pytest
from pathlib import Path

from doit_cli.models.hook_config import HookConfig, HookRule, LoggingConfig


class TestHookRule:
    """Tests for HookRule dataclass."""

    def test_default_values(self):
        """Test default HookRule values."""
        rule = HookRule()
        assert rule.enabled is True
        assert rule.require_spec is True
        assert rule.require_plan is True
        assert rule.require_tasks is False
        assert "In Progress" in rule.allowed_statuses
        assert "main" in rule.exempt_branches
        assert rule.exempt_paths == []

    def test_custom_values(self):
        """Test HookRule with custom values."""
        rule = HookRule(
            enabled=False,
            require_spec=False,
            exempt_branches=["custom/*"],
            exempt_paths=["*.md"],
        )
        assert rule.enabled is False
        assert rule.require_spec is False
        assert rule.exempt_branches == ["custom/*"]
        assert rule.exempt_paths == ["*.md"]


class TestLoggingConfig:
    """Tests for LoggingConfig dataclass."""

    def test_default_values(self):
        """Test default LoggingConfig values."""
        config = LoggingConfig()
        assert config.enabled is True
        assert config.log_bypasses is True
        assert config.log_path == ".doit/logs/hook-bypasses.log"

    def test_custom_values(self):
        """Test LoggingConfig with custom values."""
        config = LoggingConfig(
            enabled=False,
            log_bypasses=False,
            log_path="/custom/path.log",
        )
        assert config.enabled is False
        assert config.log_bypasses is False
        assert config.log_path == "/custom/path.log"


class TestHookConfig:
    """Tests for HookConfig dataclass."""

    def test_default_values(self):
        """Test default HookConfig values."""
        config = HookConfig()
        assert config.version == 1
        assert isinstance(config.pre_commit, HookRule)
        assert isinstance(config.pre_push, HookRule)
        assert isinstance(config.logging, LoggingConfig)

    def test_get_rule_for_hook_pre_commit(self):
        """Test getting pre-commit rule."""
        config = HookConfig()
        rule = config.get_rule_for_hook("pre-commit")
        assert rule is config.pre_commit

    def test_get_rule_for_hook_pre_push(self):
        """Test getting pre-push rule."""
        config = HookConfig()
        rule = config.get_rule_for_hook("pre-push")
        assert rule is config.pre_push

    def test_get_rule_for_invalid_hook(self):
        """Test getting invalid hook returns None."""
        config = HookConfig()
        rule = config.get_rule_for_hook("invalid")
        assert rule is None


class TestHookConfigFileLoading:
    """Tests for configuration file loading."""

    def test_load_from_nonexistent_file(self, tmp_path: Path):
        """Test loading from nonexistent file returns defaults."""
        config_path = tmp_path / "nonexistent.yaml"
        config = HookConfig.load_from_file(config_path)

        assert config.version == 1
        assert config.pre_commit.enabled is True

    def test_load_from_valid_yaml(self, tmp_path: Path):
        """Test loading from valid YAML file."""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
version: 2
pre_commit:
  enabled: false
  require_spec: true
  exempt_branches:
    - main
    - hotfix/*
pre_push:
  enabled: true
  require_plan: false
logging:
  log_bypasses: false
""")
        config = HookConfig.load_from_file(config_path)

        assert config.version == 2
        assert config.pre_commit.enabled is False
        assert "hotfix/*" in config.pre_commit.exempt_branches
        assert config.pre_push.require_plan is False
        assert config.logging.log_bypasses is False

    def test_load_from_invalid_yaml(self, tmp_path: Path):
        """Test loading from invalid YAML returns defaults."""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("invalid: yaml: content:")

        config = HookConfig.load_from_file(config_path)

        # Should return defaults on parse error
        assert config.version == 1
        assert config.pre_commit.enabled is True

    def test_load_from_empty_file(self, tmp_path: Path):
        """Test loading from empty file returns defaults."""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("")

        config = HookConfig.load_from_file(config_path)

        assert config.version == 1
        assert config.pre_commit.enabled is True

    def test_load_with_require_spec_status_alias(self, tmp_path: Path):
        """Test loading handles require_spec_status as alias."""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
pre_commit:
  require_spec_status:
    - Draft
    - In Progress
""")
        config = HookConfig.load_from_file(config_path)

        # Should convert require_spec_status to allowed_statuses
        assert "Draft" in config.pre_commit.allowed_statuses
        assert "In Progress" in config.pre_commit.allowed_statuses

    def test_load_default_returns_defaults(self, tmp_path: Path, monkeypatch):
        """Test load_default returns defaults when no config file."""
        # Change to temp directory where no config exists
        monkeypatch.chdir(tmp_path)

        config = HookConfig.load_default()

        assert config.version == 1
        assert config.pre_commit.enabled is True

    def test_get_default_config_path(self):
        """Test default config path."""
        path = HookConfig.get_default_config_path()
        assert path == Path(".doit/config/hooks.yaml")


class TestHookConfigPartialOverrides:
    """Tests for partial configuration overrides."""

    def test_partial_pre_commit_override(self, tmp_path: Path):
        """Test partially overriding pre_commit settings."""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
pre_commit:
  enabled: false
""")
        config = HookConfig.load_from_file(config_path)

        # Overridden value
        assert config.pre_commit.enabled is False
        # Default values preserved
        assert config.pre_commit.require_spec is True

    def test_partial_logging_override(self, tmp_path: Path):
        """Test partially overriding logging settings."""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
logging:
  log_bypasses: false
""")
        config = HookConfig.load_from_file(config_path)

        # Overridden value
        assert config.logging.log_bypasses is False
        # Default values preserved
        assert config.logging.enabled is True

    def test_unknown_fields_ignored(self, tmp_path: Path):
        """Test unknown fields are ignored."""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
pre_commit:
  enabled: true
  unknown_field: some_value
  another_unknown: 123
""")
        config = HookConfig.load_from_file(config_path)

        # Known field works
        assert config.pre_commit.enabled is True
        # Unknown fields don't cause errors
        assert not hasattr(config.pre_commit, "unknown_field")
