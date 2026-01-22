# Contract: ConfigBackupService

**Branch**: `047-provider-config-wizard` | **Date**: 2026-01-22

## Overview

The ConfigBackupService manages configuration backups when reconfiguring providers, ensuring no data loss during provider switching.

## Interface

```python
class ConfigBackupService:
    """Manages provider configuration backups."""

    BACKUP_PATH: Path = Path(".doit/config/provider_backup.yaml")
    MAX_BACKUPS: int = 5

    def __init__(self, backup_path: Path | None = None) -> None:
        """
        Initialize backup service.

        Args:
            backup_path: Optional custom backup file path
        """

    def create_backup(
        self,
        config: ProviderConfig,
        reason: str,
    ) -> ConfigBackup:
        """
        Create a backup of the current configuration.

        Args:
            config: Current provider configuration
            reason: Why backup is being created

        Returns:
            ConfigBackup object with backup details
        """

    def list_backups(self) -> list[ConfigBackup]:
        """
        List all stored backups, newest first.

        Returns:
            List of ConfigBackup objects
        """

    def restore_backup(self, backup_id: str) -> ProviderConfig:
        """
        Restore a specific backup.

        Args:
            backup_id: ID of backup to restore

        Returns:
            Restored ProviderConfig

        Raises:
            BackupNotFoundError: If backup_id doesn't exist
        """

    def get_latest_backup(self) -> ConfigBackup | None:
        """
        Get the most recent backup.

        Returns:
            Latest ConfigBackup or None if no backups
        """

    def prune_old_backups(self) -> int:
        """
        Remove backups exceeding MAX_BACKUPS.

        Returns:
            Number of backups removed
        """
```

## Data Structures

```python
@dataclass
class ConfigBackup:
    """A stored configuration backup."""
    backup_id: str  # Format: YYYYMMDD_HHMMSS
    created_at: datetime
    reason: str
    config_data: dict[str, Any]

    def to_provider_config(self) -> ProviderConfig:
        """Convert backup data to ProviderConfig instance."""


class BackupNotFoundError(Exception):
    """Raised when a requested backup doesn't exist."""
    def __init__(self, backup_id: str):
        self.backup_id = backup_id
        super().__init__(f"Backup '{backup_id}' not found")
```

## Method Behaviors

### create_backup()

1. Generate backup_id: `datetime.now().strftime("%Y%m%d_%H%M%S")`
2. Serialize config to dict
3. Create ConfigBackup object
4. Load existing backups from file
5. Prepend new backup to list
6. Call prune_old_backups() to maintain MAX_BACKUPS
7. Save updated backup list
8. Return new ConfigBackup

### list_backups()

1. Load backup file if exists
2. Parse YAML into list of ConfigBackup objects
3. Return sorted by created_at descending
4. Return empty list if file doesn't exist

### restore_backup()

1. Load all backups
2. Find backup with matching backup_id
3. If not found: raise BackupNotFoundError
4. Convert config_data to ProviderConfig
5. Return ProviderConfig (caller is responsible for saving)

### prune_old_backups()

1. Load all backups
2. If count <= MAX_BACKUPS: return 0
3. Keep first MAX_BACKUPS (newest)
4. Save pruned list
5. Return number removed

## Storage Format

### provider_backup.yaml

```yaml
backups:
  - backup_id: "20260122_153000"
    created_at: "2026-01-22T15:30:00Z"
    reason: "provider_switch"
    config_data:
      provider: github
      auto_detected: true
      detection_source: git_remote
      validated_at: "2026-01-20T10:00:00Z"
      github:
        auth_method: gh_cli

  - backup_id: "20260115_090000"
    created_at: "2026-01-15T09:00:00Z"
    reason: "reconfigure"
    config_data:
      provider: azure_devops
      auto_detected: false
      azure_devops:
        organization: old-org
        project: old-project
        auth_method: pat
```

## Usage in Wizard

The WizardService uses ConfigBackupService when:

1. **Reconfiguration requested**: Before collecting new config
   ```python
   if existing_config.is_configured():
       backup = backup_service.create_backup(
           existing_config,
           reason="reconfigure",
       )
       console.print(f"[dim]Backup created: {backup.backup_id}[/dim]")
   ```

2. **Provider switch**: Explicit reason for audit trail
   ```python
   backup = backup_service.create_backup(
       existing_config,
       reason=f"provider_switch:{existing_config.provider.value}_to_{new_provider.value}",
   )
   ```

3. **Cancellation recovery**: Restore if wizard cancelled
   ```python
   def handle_cancellation(self):
       latest = backup_service.get_latest_backup()
       if latest:
           config = latest.to_provider_config()
           config.save()
   ```

## Dependencies

- `yaml` - For backup file serialization
- `datetime` - For timestamps and backup IDs
- `pathlib` - For file path handling
