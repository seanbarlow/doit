"""Hook configuration models for workflow enforcement."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class HookRule:
    """Configuration for a specific hook type."""

    enabled: bool = True
    require_spec: bool = True
    require_plan: bool = True
    require_tasks: bool = False
    validate_spec: bool = True  # Run spec validation rules
    validate_spec_threshold: int = 70  # Minimum quality score to pass
    allowed_statuses: list[str] = field(
        default_factory=lambda: ["In Progress", "Complete", "Approved"]
    )
    exempt_branches: list[str] = field(
        default_factory=lambda: ["main", "develop"]
    )
    exempt_paths: list[str] = field(default_factory=list)


@dataclass
class LoggingConfig:
    """Configuration for hook logging."""

    enabled: bool = True
    log_bypasses: bool = True
    log_path: str = ".doit/logs/hook-bypasses.log"


@dataclass
class HookConfig:
    """Main configuration for Git hooks workflow enforcement."""

    version: int = 1
    pre_commit: HookRule = field(default_factory=HookRule)
    pre_push: HookRule = field(default_factory=HookRule)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "HookConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to the hooks.yaml configuration file.

        Returns:
            HookConfig instance with values from file or defaults.
        """
        if not config_path.exists():
            return cls()

        try:
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            # Return default config on parse error
            return cls()

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "HookConfig":
        """Create HookConfig from dictionary."""
        pre_commit_data = data.get("pre_commit", {})
        pre_push_data = data.get("pre_push", {})
        logging_data = data.get("logging", {})

        # Handle alternate key names
        if "require_spec_status" in pre_commit_data:
            pre_commit_data["allowed_statuses"] = pre_commit_data.pop(
                "require_spec_status"
            )
        if "require_spec_status" in pre_push_data:
            pre_push_data["allowed_statuses"] = pre_push_data.pop(
                "require_spec_status"
            )

        return cls(
            version=data.get("version", 1),
            pre_commit=HookRule(**{
                k: v for k, v in pre_commit_data.items()
                if k in HookRule.__dataclass_fields__
            }) if pre_commit_data else HookRule(),
            pre_push=HookRule(**{
                k: v for k, v in pre_push_data.items()
                if k in HookRule.__dataclass_fields__
            }) if pre_push_data else HookRule(),
            logging=LoggingConfig(**{
                k: v for k, v in logging_data.items()
                if k in LoggingConfig.__dataclass_fields__
            }) if logging_data else LoggingConfig(),
        )

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get the default configuration file path."""
        return Path(".doit/config/hooks.yaml")

    @classmethod
    def load_default(cls) -> "HookConfig":
        """Load configuration from default location."""
        return cls.load_from_file(cls.get_default_config_path())

    def get_rule_for_hook(self, hook_type: str) -> Optional[HookRule]:
        """Get the rule configuration for a specific hook type.

        Args:
            hook_type: Type of hook ('pre-commit' or 'pre-push').

        Returns:
            HookRule for the specified hook type, or None if invalid.
        """
        hook_map = {
            "pre-commit": self.pre_commit,
            "pre-push": self.pre_push,
        }
        return hook_map.get(hook_type)
