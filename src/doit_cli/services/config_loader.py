"""Config loader for validation rules configuration."""

from pathlib import Path
from typing import Optional

import yaml

from ..models.validation_models import (
    CustomRule,
    RuleOverride,
    ValidationConfig,
)


class ConfigLoader:
    """Loads validation configuration from YAML files."""

    # Default configuration file path
    DEFAULT_CONFIG_PATH = ".doit/validation-rules.yaml"

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize config loader.

        Args:
            project_root: Project root directory. Defaults to cwd.
        """
        self.project_root = project_root or Path.cwd()

    def load(self, config_path: Optional[Path] = None) -> ValidationConfig:
        """Load validation configuration from YAML file.

        Args:
            config_path: Path to config file. Uses default if None.

        Returns:
            ValidationConfig with loaded or default settings.
        """
        if config_path is None:
            config_path = self.project_root / self.DEFAULT_CONFIG_PATH

        if not config_path.exists():
            return ValidationConfig.default()

        try:
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            # Return default config on parse error
            return ValidationConfig.default()

        return self._from_dict(data, str(config_path))

    def _from_dict(self, data: dict, path: str = "") -> ValidationConfig:
        """Create ValidationConfig from dictionary.

        Args:
            data: Parsed YAML data.
            path: Path to config file for reference.

        Returns:
            Populated ValidationConfig.
        """
        # Parse disabled rules
        disabled_rules = data.get("disabled_rules", [])

        # Parse overrides
        overrides = []
        for override_data in data.get("overrides", []):
            if "rule" in override_data and "severity" in override_data:
                overrides.append(
                    RuleOverride(
                        rule=override_data["rule"],
                        severity=override_data["severity"],
                    )
                )

        # Parse custom rules
        custom_rules = []
        for rule_data in data.get("custom_rules", []):
            if "name" in rule_data and "pattern" in rule_data:
                custom_rules.append(
                    CustomRule(
                        name=rule_data["name"],
                        description=rule_data.get("description", ""),
                        pattern=rule_data["pattern"],
                        severity=rule_data.get("severity", "warning"),
                        category=rule_data.get("category", "custom"),
                        check=rule_data.get("check", "present"),
                        max=rule_data.get("max"),
                    )
                )

        return ValidationConfig(
            path=path,
            version=data.get("version", "1.0"),
            enabled=data.get("enabled", True),
            disabled_rules=disabled_rules,
            overrides=overrides,
            custom_rules=custom_rules,
        )


def load_validation_config(project_root: Optional[Path] = None) -> ValidationConfig:
    """Convenience function to load validation config.

    Args:
        project_root: Project root directory.

    Returns:
        ValidationConfig from file or defaults.
    """
    loader = ConfigLoader(project_root)
    return loader.load()
