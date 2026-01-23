"""Provider configuration management.

This module handles loading, saving, and managing provider
configuration stored in .doit/config/provider.yaml.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Optional

import yaml

from .providers.base import ProviderType


@dataclass
class AzureDevOpsConfig:
    """Azure DevOps-specific configuration."""

    organization: str = ""
    project: str = ""
    auth_method: str = "pat"  # personal access token
    api_version: str = "7.0"


@dataclass
class GitHubConfig:
    """GitHub-specific configuration."""

    auth_method: str = "gh_cli"  # or "token"
    enterprise_host: Optional[str] = None


@dataclass
class GitLabConfig:
    """GitLab-specific configuration."""

    host: str = "gitlab.com"
    auth_method: str = "token"


@dataclass
class ProviderConfig:
    """Provider configuration.

    Manages configuration for git providers, stored in
    .doit/config/provider.yaml.

    Attributes:
        provider: The configured provider type.
        auto_detected: Whether the provider was auto-detected.
        detection_source: How the provider was detected (e.g., "git_remote").
        github: GitHub-specific configuration.
        azure_devops: Azure DevOps-specific configuration.
        gitlab: GitLab-specific configuration.
        validated_at: Timestamp of last successful validation.
        configured_by: How the configuration was created ("wizard" or "manual").
        wizard_version: Version of wizard used for configuration.
    """

    provider: Optional[ProviderType] = None
    auto_detected: bool = False
    detection_source: Optional[str] = None
    github: GitHubConfig = field(default_factory=GitHubConfig)
    azure_devops: AzureDevOpsConfig = field(default_factory=AzureDevOpsConfig)
    gitlab: GitLabConfig = field(default_factory=GitLabConfig)
    validated_at: Optional[datetime] = None
    configured_by: Optional[str] = None
    wizard_version: Optional[str] = None

    CONFIG_PATH: Path = Path(".doit/config/provider.yaml")

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "ProviderConfig":
        """Load configuration from file.

        Args:
            config_path: Optional custom path. Defaults to .doit/config/provider.yaml

        Returns:
            ProviderConfig instance, empty if file doesn't exist.
        """
        path = config_path or cls.CONFIG_PATH

        if not path.exists():
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            return cls()

        config = cls()

        # Parse provider type
        if "provider" in data:
            try:
                config.provider = ProviderType(data["provider"])
            except ValueError:
                pass

        config.auto_detected = data.get("auto_detected", False)
        config.detection_source = data.get("detection_source")
        config.configured_by = data.get("configured_by")
        config.wizard_version = data.get("wizard_version")

        # Parse validated_at timestamp
        if "validated_at" in data:
            validated_str = data["validated_at"]
            if isinstance(validated_str, str):
                try:
                    config.validated_at = datetime.fromisoformat(
                        validated_str.replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

        # Parse GitHub config
        if "github" in data:
            gh = data["github"]
            config.github = GitHubConfig(
                auth_method=gh.get("auth_method", "gh_cli"),
                enterprise_host=gh.get("enterprise_host"),
            )

        # Parse Azure DevOps config
        if "azure_devops" in data:
            ado = data["azure_devops"]
            config.azure_devops = AzureDevOpsConfig(
                organization=ado.get("organization", ""),
                project=ado.get("project", ""),
                auth_method=ado.get("auth_method", "pat"),
                api_version=ado.get("api_version", "7.0"),
            )

        # Parse GitLab config
        if "gitlab" in data:
            gl = data["gitlab"]
            config.gitlab = GitLabConfig(
                host=gl.get("host", "gitlab.com"),
                auth_method=gl.get("auth_method", "token"),
            )

        return config

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file.

        Args:
            config_path: Optional custom path. Defaults to .doit/config/provider.yaml
        """
        path = config_path or self.CONFIG_PATH

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {}

        if self.provider:
            data["provider"] = self.provider.value

        data["auto_detected"] = self.auto_detected

        if self.detection_source:
            data["detection_source"] = self.detection_source

        if self.validated_at:
            data["validated_at"] = self.validated_at.isoformat()

        if self.configured_by:
            data["configured_by"] = self.configured_by

        if self.wizard_version:
            data["wizard_version"] = self.wizard_version

        # Save provider-specific config based on selected provider
        if self.provider == ProviderType.GITHUB:
            data["github"] = {
                "auth_method": self.github.auth_method,
            }
            if self.github.enterprise_host:
                data["github"]["enterprise_host"] = self.github.enterprise_host

        elif self.provider == ProviderType.AZURE_DEVOPS:
            data["azure_devops"] = {
                "organization": self.azure_devops.organization,
                "project": self.azure_devops.project,
                "auth_method": self.azure_devops.auth_method,
                "api_version": self.azure_devops.api_version,
            }

        elif self.provider == ProviderType.GITLAB:
            data["gitlab"] = {
                "host": self.gitlab.host,
                "auth_method": self.gitlab.auth_method,
            }

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def is_configured(self) -> bool:
        """Check if a provider is configured.

        Returns:
            True if a provider is set, False otherwise.
        """
        return self.provider is not None

    def get_provider_display_name(self) -> str:
        """Get a human-readable name for the configured provider.

        Returns:
            Display name or "Not configured" if no provider is set.
        """
        if self.provider is None:
            return "Not configured"

        names = {
            ProviderType.GITHUB: "GitHub",
            ProviderType.AZURE_DEVOPS: "Azure DevOps",
            ProviderType.GITLAB: "GitLab",
        }
        return names.get(self.provider, self.provider.value)
