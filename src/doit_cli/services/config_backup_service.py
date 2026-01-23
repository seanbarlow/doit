"""Configuration backup service for provider switching.

This module manages configuration backups when reconfiguring providers,
ensuring no data loss during provider switching.
"""

from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Optional

import yaml

from ..models.wizard_models import ConfigBackup, BackupNotFoundError
from .provider_config import ProviderConfig
from .providers.base import ProviderType


class ConfigBackupService:
    """Manages provider configuration backups."""

    BACKUP_PATH: Path = Path(".doit/config/provider_backup.yaml")
    MAX_BACKUPS: int = 5

    def __init__(self, backup_path: Optional[Path] = None) -> None:
        """Initialize backup service.

        Args:
            backup_path: Optional custom backup file path
        """
        self.backup_path = backup_path or self.BACKUP_PATH

    def create_backup(
        self,
        config: ProviderConfig,
        reason: str,
    ) -> ConfigBackup:
        """Create a backup of the current configuration.

        Args:
            config: Current provider configuration
            reason: Why backup is being created

        Returns:
            ConfigBackup object with backup details
        """
        # Serialize config to dict
        config_data = self._config_to_dict(config)

        # Create backup object
        backup = ConfigBackup.create(reason=reason, config_data=config_data)

        # Load existing backups
        backups = self.list_backups()

        # Prepend new backup
        backups.insert(0, backup)

        # Prune old backups
        if len(backups) > self.MAX_BACKUPS:
            backups = backups[: self.MAX_BACKUPS]

        # Save updated backup list
        self._save_backups(backups)

        return backup

    def list_backups(self) -> list[ConfigBackup]:
        """List all stored backups, newest first.

        Returns:
            List of ConfigBackup objects
        """
        if not self.backup_path.exists():
            return []

        try:
            with open(self.backup_path) as f:
                data = yaml.safe_load(f) or {}

            backups_data = data.get("backups", [])
            backups = []

            for item in backups_data:
                backup = ConfigBackup(
                    backup_id=item.get("backup_id", ""),
                    created_at=self._parse_datetime(item.get("created_at")),
                    reason=item.get("reason", ""),
                    config_data=item.get("config_data", {}),
                )
                backups.append(backup)

            # Sort by created_at descending (newest first)
            backups.sort(key=lambda b: b.created_at, reverse=True)
            return backups

        except (yaml.YAMLError, OSError):
            return []

    def restore_backup(self, backup_id: str) -> ProviderConfig:
        """Restore a specific backup.

        Args:
            backup_id: ID of backup to restore

        Returns:
            Restored ProviderConfig

        Raises:
            BackupNotFoundError: If backup_id doesn't exist
        """
        backups = self.list_backups()

        for backup in backups:
            if backup.backup_id == backup_id:
                return self._dict_to_config(backup.config_data)

        raise BackupNotFoundError(backup_id)

    def get_latest_backup(self) -> Optional[ConfigBackup]:
        """Get the most recent backup.

        Returns:
            Latest ConfigBackup or None if no backups
        """
        backups = self.list_backups()
        return backups[0] if backups else None

    def prune_old_backups(self) -> int:
        """Remove backups exceeding MAX_BACKUPS.

        Returns:
            Number of backups removed
        """
        backups = self.list_backups()

        if len(backups) <= self.MAX_BACKUPS:
            return 0

        removed_count = len(backups) - self.MAX_BACKUPS
        backups = backups[: self.MAX_BACKUPS]
        self._save_backups(backups)

        return removed_count

    def delete_backup(self, backup_id: str) -> None:
        """Delete a specific backup.

        Args:
            backup_id: ID of backup to delete

        Raises:
            BackupNotFoundError: If backup_id doesn't exist
        """
        backups = self.list_backups()
        original_count = len(backups)

        backups = [b for b in backups if b.backup_id != backup_id]

        if len(backups) == original_count:
            raise BackupNotFoundError(backup_id)

        self._save_backups(backups)

    def _save_backups(self, backups: list[ConfigBackup]) -> None:
        """Save backups to YAML file."""
        # Ensure directory exists
        self.backup_path.parent.mkdir(parents=True, exist_ok=True)

        backups_data = []
        for backup in backups:
            backups_data.append(
                {
                    "backup_id": backup.backup_id,
                    "created_at": backup.created_at.isoformat(),
                    "reason": backup.reason,
                    "config_data": backup.config_data,
                }
            )

        data = {"backups": backups_data}

        with open(self.backup_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def _config_to_dict(self, config: ProviderConfig) -> dict[str, Any]:
        """Convert ProviderConfig to serializable dict."""
        data: dict[str, Any] = {}

        if config.provider:
            data["provider"] = config.provider.value

        data["auto_detected"] = config.auto_detected

        if config.detection_source:
            data["detection_source"] = config.detection_source

        # Provider-specific config
        if config.provider == ProviderType.GITHUB:
            data["github"] = {
                "auth_method": config.github.auth_method,
            }
            if config.github.enterprise_host:
                data["github"]["enterprise_host"] = config.github.enterprise_host

        elif config.provider == ProviderType.AZURE_DEVOPS:
            data["azure_devops"] = {
                "organization": config.azure_devops.organization,
                "project": config.azure_devops.project,
                "auth_method": config.azure_devops.auth_method,
                "api_version": config.azure_devops.api_version,
            }

        elif config.provider == ProviderType.GITLAB:
            data["gitlab"] = {
                "host": config.gitlab.host,
                "auth_method": config.gitlab.auth_method,
            }

        return data

    def _dict_to_config(self, data: dict[str, Any]) -> ProviderConfig:
        """Convert dict back to ProviderConfig."""
        config = ProviderConfig()

        # Parse provider type
        if "provider" in data:
            try:
                config.provider = ProviderType(data["provider"])
            except ValueError:
                pass

        config.auto_detected = data.get("auto_detected", False)
        config.detection_source = data.get("detection_source")

        # Parse GitHub config
        if "github" in data:
            gh = data["github"]
            config.github.auth_method = gh.get("auth_method", "gh_cli")
            config.github.enterprise_host = gh.get("enterprise_host")

        # Parse Azure DevOps config
        if "azure_devops" in data:
            ado = data["azure_devops"]
            config.azure_devops.organization = ado.get("organization", "")
            config.azure_devops.project = ado.get("project", "")
            config.azure_devops.auth_method = ado.get("auth_method", "pat")
            config.azure_devops.api_version = ado.get("api_version", "7.0")

        # Parse GitLab config
        if "gitlab" in data:
            gl = data["gitlab"]
            config.gitlab.host = gl.get("host", "gitlab.com")
            config.gitlab.auth_method = gl.get("auth_method", "token")

        return config

    def _parse_datetime(self, value: Any) -> datetime:
        """Parse datetime from string or return current time."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                # Handle ISO format
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.now(UTC)
