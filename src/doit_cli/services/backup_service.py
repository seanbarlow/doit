"""Backup service for preserving files during updates."""

from datetime import datetime
from pathlib import Path
import shutil
from typing import Optional


class BackupService:
    """Service for creating backups before update operations."""

    BACKUP_DIR = "backups"
    TIMESTAMP_FORMAT = "%Y%m%dT%H%M%S"

    def __init__(self, project_path: Path):
        """Initialize backup service.

        Args:
            project_path: Root path of the project
        """
        self.project_path = project_path
        self.doit_folder = project_path / ".doit"
        self.backups_folder = self.doit_folder / self.BACKUP_DIR

    def create_backup(
        self,
        files: list[Path],
        backup_name: Optional[str] = None,
    ) -> Optional[Path]:
        """Create a timestamped backup of specified files.

        Args:
            files: List of file paths to backup
            backup_name: Optional custom backup name (defaults to timestamp)

        Returns:
            Path to backup directory, or None if no files to backup
        """
        if not files:
            return None

        # Generate timestamp-based backup directory name
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        backup_dir_name = backup_name or timestamp
        backup_dir = self.backups_folder / backup_dir_name

        # Create backup directory
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Copy each file preserving relative structure
        for file_path in files:
            if not file_path.exists():
                continue

            # Calculate relative path from project root
            try:
                rel_path = file_path.relative_to(self.project_path)
            except ValueError:
                # File is not under project path, use filename only
                rel_path = Path(file_path.name)

            # Create backup target path
            backup_target = backup_dir / rel_path
            backup_target.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(file_path, backup_target)

        return backup_dir

    def create_doit_backup(self, include_memory: bool = False) -> Optional[Path]:
        """Create a backup of doit-managed files.

        Args:
            include_memory: Whether to include .doit/memory/ files

        Returns:
            Path to backup directory, or None if no files to backup
        """
        files_to_backup = []

        # Find all doit-prefixed files in command directories
        command_dirs = [
            self.project_path / ".claude" / "commands",
            self.project_path / ".github" / "prompts",
        ]

        for cmd_dir in command_dirs:
            if cmd_dir.exists():
                # Backup doit-prefixed files
                for pattern in ["doit.*.md", "doit-*.prompt.md"]:
                    files_to_backup.extend(cmd_dir.glob(pattern))

        # Optionally include memory folder
        if include_memory:
            memory_dir = self.doit_folder / "memory"
            if memory_dir.exists():
                files_to_backup.extend(memory_dir.rglob("*"))

        # Filter to only include actual files (not directories)
        files_to_backup = [f for f in files_to_backup if f.is_file()]

        return self.create_backup(files_to_backup)

    def list_backups(self) -> list[Path]:
        """List all available backups.

        Returns:
            List of backup directory paths, sorted by name (newest first)
        """
        if not self.backups_folder.exists():
            return []

        backups = [
            d for d in self.backups_folder.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        # Sort by name (timestamp format ensures chronological order)
        return sorted(backups, reverse=True)

    def restore_backup(self, backup_path: Path) -> dict:
        """Restore files from a backup.

        Args:
            backup_path: Path to backup directory

        Returns:
            Dict with 'restored' list of paths and 'errors' list
        """
        result = {
            "restored": [],
            "errors": [],
        }

        if not backup_path.exists() or not backup_path.is_dir():
            result["errors"].append(f"Backup not found: {backup_path}")
            return result

        # Walk through backup and restore files
        for backup_file in backup_path.rglob("*"):
            if not backup_file.is_file():
                continue

            # Calculate original location
            rel_path = backup_file.relative_to(backup_path)
            original_path = self.project_path / rel_path

            try:
                # Ensure parent directory exists
                original_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy backup file to original location
                shutil.copy2(backup_file, original_path)
                result["restored"].append(original_path)
            except Exception as e:
                result["errors"].append(f"Failed to restore {rel_path}: {e}")

        return result

    def cleanup_old_backups(self, keep_count: int = 5) -> list[Path]:
        """Remove old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of recent backups to keep

        Returns:
            List of removed backup paths
        """
        backups = self.list_backups()
        removed = []

        if len(backups) <= keep_count:
            return removed

        # Remove older backups
        for old_backup in backups[keep_count:]:
            try:
                shutil.rmtree(old_backup)
                removed.append(old_backup)
            except Exception:
                # Silently skip backups that can't be removed
                pass

        return removed

    def get_backup_size(self, backup_path: Path) -> int:
        """Calculate total size of a backup in bytes.

        Args:
            backup_path: Path to backup directory

        Returns:
            Total size in bytes
        """
        if not backup_path.exists():
            return 0

        total = 0
        for file_path in backup_path.rglob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size

        return total
