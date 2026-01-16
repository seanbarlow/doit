"""Hook manager service for installing and managing Git hooks."""

import json
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Optional

from importlib import resources


class HookManager:
    """Manages Git hook installation, backup, and restoration."""

    HOOK_NAMES = ["pre-commit", "pre-push", "post-commit", "post-merge"]
    BACKUP_DIR = ".doit/backups/hooks"
    MANIFEST_FILE = "manifest.json"

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the hook manager.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.backup_dir = self.project_root / self.BACKUP_DIR

    def is_git_repo(self) -> bool:
        """Check if the project is a Git repository."""
        return (self.project_root / ".git").is_dir()

    def get_template_path(self, hook_name: str) -> Optional[Path]:
        """Get the path to a hook template.

        Args:
            hook_name: Name of the hook (e.g., 'pre-commit').

        Returns:
            Path to the template file, or None if not found.
        """
        # Try to get from package resources
        try:
            with resources.files("doit_cli.templates.hooks") as templates_dir:
                template_path = Path(templates_dir) / f"{hook_name}.sh"
                if template_path.exists():
                    return template_path
        except (TypeError, FileNotFoundError):
            pass

        # Fallback: try relative path from this file
        fallback_path = (
            Path(__file__).parent.parent / "templates" / "hooks" / f"{hook_name}.sh"
        )
        if fallback_path.exists():
            return fallback_path

        return None

    def install_hooks(
        self, backup: bool = False, force: bool = False
    ) -> tuple[list[str], list[str]]:
        """Install Git hooks.

        Args:
            backup: Whether to backup existing hooks before installing.
            force: Whether to overwrite existing hooks without prompting.

        Returns:
            Tuple of (installed hooks, skipped hooks).

        Raises:
            RuntimeError: If not in a Git repository.
        """
        if not self.is_git_repo():
            raise RuntimeError("Not a Git repository. Run 'git init' first.")

        # Ensure hooks directory exists
        self.git_hooks_dir.mkdir(parents=True, exist_ok=True)

        installed = []
        skipped = []

        for hook_name in self.HOOK_NAMES:
            template_path = self.get_template_path(hook_name)
            if template_path is None:
                continue

            hook_path = self.git_hooks_dir / hook_name

            # Check if hook already exists
            if hook_path.exists():
                if backup:
                    self._backup_hook(hook_name)
                elif not force:
                    skipped.append(hook_name)
                    continue

            # Copy template to hooks directory
            shutil.copy2(template_path, hook_path)

            # Make executable
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            installed.append(hook_name)

        return installed, skipped

    def uninstall_hooks(self) -> list[str]:
        """Remove installed Git hooks.

        Returns:
            List of removed hook names.
        """
        removed = []

        for hook_name in self.HOOK_NAMES:
            hook_path = self.git_hooks_dir / hook_name
            if hook_path.exists():
                # Check if it's our hook by looking for the marker comment
                content = hook_path.read_text()
                if "installed by doit" in content.lower():
                    hook_path.unlink()
                    removed.append(hook_name)

        return removed

    def _backup_hook(self, hook_name: str) -> Optional[Path]:
        """Backup an existing hook.

        Args:
            hook_name: Name of the hook to backup.

        Returns:
            Path to the backup file, or None if hook doesn't exist.
        """
        hook_path = self.git_hooks_dir / hook_name
        if not hook_path.exists():
            return None

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        backup_name = f"{hook_name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        # Copy the hook
        shutil.copy2(hook_path, backup_path)

        # Update manifest
        self._update_manifest(hook_name, timestamp)

        return backup_path

    def _update_manifest(self, hook_name: str, timestamp: str) -> None:
        """Update the backup manifest file.

        Args:
            hook_name: Name of the backed up hook.
            timestamp: Timestamp of the backup.
        """
        manifest_path = self.backup_dir / self.MANIFEST_FILE

        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        else:
            manifest = {"latest_backup": None, "backups": []}

        # Add new backup entry
        manifest["latest_backup"] = timestamp

        # Find or create entry for this timestamp
        existing_entry = next(
            (b for b in manifest["backups"] if b["timestamp"] == timestamp),
            None
        )
        if existing_entry:
            if hook_name not in existing_entry["hooks"]:
                existing_entry["hooks"].append(hook_name)
        else:
            manifest["backups"].append({
                "timestamp": timestamp,
                "hooks": [hook_name]
            })

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def restore_hooks(self, timestamp: Optional[str] = None) -> list[str]:
        """Restore hooks from backup.

        Args:
            timestamp: Specific backup timestamp to restore. Defaults to latest.

        Returns:
            List of restored hook names.

        Raises:
            RuntimeError: If no backups exist.
        """
        manifest_path = self.backup_dir / self.MANIFEST_FILE

        if not manifest_path.exists():
            raise RuntimeError("No hook backups found.")

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        if not manifest.get("backups"):
            raise RuntimeError("No hook backups found.")

        # Use specified timestamp or latest
        target_timestamp = timestamp or manifest.get("latest_backup")
        if not target_timestamp:
            raise RuntimeError("No backup timestamp available.")

        # Find the backup entry
        backup_entry = next(
            (b for b in manifest["backups"] if b["timestamp"] == target_timestamp),
            None
        )
        if not backup_entry:
            raise RuntimeError(f"No backup found for timestamp: {target_timestamp}")

        restored = []
        for hook_name in backup_entry["hooks"]:
            backup_path = self.backup_dir / f"{hook_name}.{target_timestamp}.bak"
            if backup_path.exists():
                hook_path = self.git_hooks_dir / hook_name
                shutil.copy2(backup_path, hook_path)
                # Make executable
                hook_path.chmod(
                    hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )
                restored.append(hook_name)

        return restored

    def get_installed_hooks(self) -> list[str]:
        """Get list of currently installed doit hooks.

        Returns:
            List of installed hook names.
        """
        installed = []

        for hook_name in self.HOOK_NAMES:
            hook_path = self.git_hooks_dir / hook_name
            if hook_path.exists():
                content = hook_path.read_text()
                if "installed by doit" in content.lower():
                    installed.append(hook_name)

        return installed
