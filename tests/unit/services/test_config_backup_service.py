"""Unit tests for ConfigBackupService - T017."""

from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.doit_cli.models.wizard_models import BackupNotFoundError, ConfigBackup
from src.doit_cli.services.config_backup_service import ConfigBackupService
from src.doit_cli.services.provider_config import ProviderConfig
from src.doit_cli.services.providers.base import ProviderType


@pytest.fixture
def backup_service(tmp_path):
    """Create backup service with temporary storage path."""
    backup_path = tmp_path / "provider_backup.yaml"
    return ConfigBackupService(backup_path=backup_path)


@pytest.fixture
def github_config():
    """Create a configured GitHub ProviderConfig."""
    config = ProviderConfig()
    config.provider = ProviderType.GITHUB
    config.github.auth_method = "gh_cli"
    config.auto_detected = True
    config.detection_source = "git_remote"
    return config


@pytest.fixture
def azure_config():
    """Create a configured Azure DevOps ProviderConfig."""
    config = ProviderConfig()
    config.provider = ProviderType.AZURE_DEVOPS
    config.azure_devops.organization = "myorg"
    config.azure_devops.project = "myproject"
    config.auto_detected = False
    return config


class TestCreateBackup:
    """Tests for create_backup() method."""

    def test_creates_backup_with_timestamp_id(self, backup_service, github_config):
        """Backup ID is timestamp-based."""
        backup = backup_service.create_backup(github_config, reason="test")

        assert backup.backup_id is not None
        # Format: YYYYMMDD_HHMMSS_MICROSEC
        assert len(backup.backup_id) == 22
        assert backup.backup_id.count("_") == 2

    def test_stores_config_data(self, backup_service, github_config):
        """Backup contains serialized config data."""
        backup = backup_service.create_backup(github_config, reason="test")

        assert backup.config_data is not None
        assert backup.config_data["provider"] == "github"
        assert backup.config_data["github"]["auth_method"] == "gh_cli"

    def test_stores_reason(self, backup_service, github_config):
        """Backup stores the reason for creation."""
        backup = backup_service.create_backup(github_config, reason="reconfigure")

        assert backup.reason == "reconfigure"

    def test_persists_to_file(self, backup_service, github_config):
        """Backup is persisted to YAML file."""
        backup_service.create_backup(github_config, reason="test")

        assert backup_service.backup_path.exists()

    def test_multiple_backups_stored(self, backup_service, github_config, azure_config):
        """Multiple backups are stored in the file."""
        backup_service.create_backup(github_config, reason="first")
        backup_service.create_backup(azure_config, reason="second")

        backups = backup_service.list_backups()
        assert len(backups) == 2


class TestListBackups:
    """Tests for list_backups() method."""

    def test_empty_when_no_backups(self, backup_service):
        """Returns empty list when no backups exist."""
        backups = backup_service.list_backups()

        assert backups == []

    def test_returns_all_backups(self, backup_service, github_config):
        """Returns all stored backups."""
        backup_service.create_backup(github_config, reason="first")
        backup_service.create_backup(github_config, reason="second")
        backup_service.create_backup(github_config, reason="third")

        backups = backup_service.list_backups()

        assert len(backups) == 3

    def test_backups_ordered_newest_first(self, backup_service, github_config):
        """Backups are returned with newest first."""
        backup_service.create_backup(github_config, reason="first")
        backup_service.create_backup(github_config, reason="second")

        backups = backup_service.list_backups()

        assert backups[0].reason == "second"
        assert backups[1].reason == "first"


class TestRestoreBackup:
    """Tests for restore_backup() method."""

    def test_restores_config_from_backup(self, backup_service, github_config):
        """Restores ProviderConfig from backup data."""
        backup = backup_service.create_backup(github_config, reason="test")

        restored = backup_service.restore_backup(backup.backup_id)

        assert restored.provider == ProviderType.GITHUB
        assert restored.github.auth_method == "gh_cli"
        assert restored.auto_detected is True

    def test_raises_error_for_nonexistent_backup(self, backup_service):
        """Raises BackupNotFoundError for unknown backup ID."""
        with pytest.raises(BackupNotFoundError) as exc_info:
            backup_service.restore_backup("nonexistent_id")

        assert "nonexistent_id" in str(exc_info.value)

    def test_restores_azure_config(self, backup_service, azure_config):
        """Correctly restores Azure DevOps configuration."""
        backup = backup_service.create_backup(azure_config, reason="test")

        restored = backup_service.restore_backup(backup.backup_id)

        assert restored.provider == ProviderType.AZURE_DEVOPS
        assert restored.azure_devops.organization == "myorg"
        assert restored.azure_devops.project == "myproject"


class TestGetLatestBackup:
    """Tests for get_latest_backup() method."""

    def test_returns_none_when_no_backups(self, backup_service):
        """Returns None when no backups exist."""
        result = backup_service.get_latest_backup()

        assert result is None

    def test_returns_most_recent_backup(self, backup_service, github_config):
        """Returns the most recently created backup."""
        backup_service.create_backup(github_config, reason="first")
        backup_service.create_backup(github_config, reason="latest")

        latest = backup_service.get_latest_backup()

        assert latest is not None
        assert latest.reason == "latest"


class TestPruneOldBackups:
    """Tests for prune_old_backups() method."""

    def test_removes_oldest_when_over_limit(self, backup_service, github_config):
        """Removes oldest backups when count exceeds MAX_BACKUPS."""
        # Create more than MAX_BACKUPS
        for i in range(7):
            backup_service.create_backup(github_config, reason=f"backup_{i}")

        backup_service.prune_old_backups()

        backups = backup_service.list_backups()
        assert len(backups) == backup_service.MAX_BACKUPS

    def test_keeps_newest_backups(self, backup_service, github_config):
        """Keeps the newest backups after pruning."""
        for i in range(7):
            backup_service.create_backup(github_config, reason=f"backup_{i}")

        backup_service.prune_old_backups()

        backups = backup_service.list_backups()
        # Newest should be kept (backup_6, backup_5, backup_4, backup_3, backup_2)
        reasons = [b.reason for b in backups]
        assert "backup_6" in reasons
        assert "backup_0" not in reasons

    def test_does_nothing_under_limit(self, backup_service, github_config):
        """Does not prune when under MAX_BACKUPS."""
        backup_service.create_backup(github_config, reason="first")
        backup_service.create_backup(github_config, reason="second")

        backup_service.prune_old_backups()

        backups = backup_service.list_backups()
        assert len(backups) == 2


class TestDeleteBackup:
    """Tests for delete_backup() method."""

    def test_removes_specific_backup(self, backup_service, github_config):
        """Removes a specific backup by ID."""
        backup1 = backup_service.create_backup(github_config, reason="keep")
        backup2 = backup_service.create_backup(github_config, reason="delete")

        backup_service.delete_backup(backup2.backup_id)

        backups = backup_service.list_backups()
        assert len(backups) == 1
        assert backups[0].reason == "keep"

    def test_raises_error_for_nonexistent_backup(self, backup_service):
        """Raises BackupNotFoundError for unknown backup ID."""
        with pytest.raises(BackupNotFoundError):
            backup_service.delete_backup("nonexistent_id")
