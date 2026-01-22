"""Factory for creating git provider instances.

This module provides the ProviderFactory class for instantiating
the appropriate git provider based on configuration.
"""

import subprocess
from typing import TYPE_CHECKING, Optional

from .providers.base import GitProvider, ProviderType
from .providers.exceptions import ProviderError, ProviderNotConfiguredError

if TYPE_CHECKING:
    from .provider_config import ProviderConfig


class ProviderFactory:
    """Factory for creating the appropriate git provider.

    This factory handles provider instantiation based on configuration,
    with fallback to auto-detection from git remote URL.

    Usage:
        # With auto-detection
        provider = ProviderFactory.create()

        # With explicit configuration
        config = ProviderConfig.load()
        provider = ProviderFactory.create(config)
    """

    @classmethod
    def create(cls, config: Optional["ProviderConfig"] = None) -> GitProvider:
        """Create a provider instance based on configuration.

        Args:
            config: Optional provider configuration. If not provided,
                   configuration is loaded from file or auto-detected.

        Returns:
            GitProvider instance for the configured provider.

        Raises:
            ProviderNotConfiguredError: If no provider is configured or detected.
            ProviderError: If provider instantiation fails.
        """
        from .provider_config import ProviderConfig

        if config is None:
            config = ProviderConfig.load()

        # Get provider type from config or auto-detect
        provider_type = config.provider
        if provider_type is None:
            provider_type = cls.detect_provider()
            if provider_type is None:
                raise ProviderNotConfiguredError()

        # Instantiate the appropriate provider
        if provider_type == ProviderType.GITHUB:
            from .providers.github import GitHubProvider

            return GitHubProvider()

        elif provider_type == ProviderType.AZURE_DEVOPS:
            from .providers.azure_devops import AzureDevOpsProvider

            return AzureDevOpsProvider(config.azure_devops)

        elif provider_type == ProviderType.GITLAB:
            from .providers.gitlab import GitLabProvider

            return GitLabProvider()

        else:
            raise ProviderError(f"Unknown provider type: {provider_type}")

    @classmethod
    def detect_provider(cls) -> Optional[ProviderType]:
        """Auto-detect provider from git remote URL.

        Examines the origin remote URL to determine which git hosting
        provider is being used.

        Returns:
            ProviderType if detected, None if detection fails.
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return None

            remote_url = result.stdout.strip().lower()

            # Check for GitHub (including enterprise)
            if "github.com" in remote_url or "ghe." in remote_url:
                return ProviderType.GITHUB

            # Check for Azure DevOps
            if "dev.azure.com" in remote_url or "visualstudio.com" in remote_url:
                return ProviderType.AZURE_DEVOPS

            # Check for GitLab (including self-hosted)
            if "gitlab" in remote_url:
                return ProviderType.GITLAB

            return None

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None

    @classmethod
    def is_provider_available(cls, provider_type: ProviderType) -> bool:
        """Check if a specific provider is available.

        Args:
            provider_type: The provider type to check.

        Returns:
            True if the provider is available, False otherwise.
        """
        try:
            from .provider_config import ProviderConfig

            config = ProviderConfig()
            config.provider = provider_type

            provider = cls.create(config)
            return provider.is_available
        except (ProviderError, ImportError):
            return False

    @classmethod
    def is_offline(cls) -> bool:
        """Check if we're in offline mode (no network connectivity).

        Returns:
            True if offline, False if online.
        """
        try:
            # Try a simple network check
            import socket

            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                ("github.com", 443)
            )
            return False
        except (socket.error, socket.timeout, OSError):
            return True

    @classmethod
    def create_safe(
        cls, config: Optional["ProviderConfig"] = None
    ) -> Optional[GitProvider]:
        """Create a provider instance, returning None if unavailable.

        This method is useful for offline-safe operations where
        provider features are optional.

        Args:
            config: Optional provider configuration.

        Returns:
            GitProvider instance if available, None otherwise.

        Example:
            provider = ProviderFactory.create_safe()
            if provider:
                issues = provider.list_issues()
            else:
                print("Running in offline mode")
        """
        try:
            provider = cls.create(config)
            if provider.is_available:
                return provider
            return None
        except (ProviderError, ProviderNotConfiguredError):
            return None
