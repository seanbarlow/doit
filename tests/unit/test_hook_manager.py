"""Unit tests for HookManager service."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from doit_cli.services.hook_manager import HookManager


class TestHookManager:
    """Tests for HookManager class."""

    def test_is_git_repo_true(self, tmp_path: Path):
        """Test is_git_repo returns True when .git exists."""
        (tmp_path / ".git").mkdir()
        manager = HookManager(project_root=tmp_path)
        assert manager.is_git_repo() is True

    def test_is_git_repo_false(self, tmp_path: Path):
        """Test is_git_repo returns False when .git doesn't exist."""
        manager = HookManager(project_root=tmp_path)
        assert manager.is_git_repo() is False

    def test_install_hooks_not_git_repo(self, tmp_path: Path):
        """Test install_hooks raises error when not in git repo."""
        manager = HookManager(project_root=tmp_path)
        with pytest.raises(RuntimeError, match="Not a Git repository"):
            manager.install_hooks()

    def test_install_hooks_creates_hooks_dir(self, tmp_path: Path):
        """Test install_hooks creates .git/hooks directory if missing."""
        (tmp_path / ".git").mkdir()
        manager = HookManager(project_root=tmp_path)

        # Mock get_template_path to return a fake template
        with patch.object(manager, "get_template_path") as mock_template:
            mock_template.return_value = None  # No templates available
            installed, skipped = manager.install_hooks()

        assert (tmp_path / ".git" / "hooks").is_dir()
        assert installed == []
        assert skipped == []

    def test_install_hooks_with_template(self, tmp_path: Path):
        """Test install_hooks installs hooks from templates."""
        # Setup git repo
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()

        # Create a fake template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "pre-commit.sh"
        template_file.write_text("#!/bin/bash\n# installed by doit\necho test")

        manager = HookManager(project_root=tmp_path)

        with patch.object(manager, "get_template_path") as mock_template:
            def get_template(hook_name):
                if hook_name == "pre-commit":
                    return template_file
                return None
            mock_template.side_effect = get_template

            installed, skipped = manager.install_hooks()

        assert "pre-commit" in installed
        assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()

    def test_install_hooks_skips_existing(self, tmp_path: Path):
        """Test install_hooks skips existing hooks without force."""
        # Setup git repo with existing hook
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()
        existing_hook = tmp_path / ".git" / "hooks" / "pre-commit"
        existing_hook.write_text("#!/bin/bash\necho existing")

        # Create a fake template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "pre-commit.sh"
        template_file.write_text("#!/bin/bash\n# installed by doit\necho test")

        manager = HookManager(project_root=tmp_path)

        with patch.object(manager, "get_template_path") as mock_template:
            mock_template.return_value = template_file
            installed, skipped = manager.install_hooks(force=False)

        assert "pre-commit" in skipped
        assert "pre-commit" not in installed
        # Original content preserved
        assert "existing" in existing_hook.read_text()

    def test_install_hooks_force_overwrites(self, tmp_path: Path):
        """Test install_hooks with force overwrites existing hooks."""
        # Setup git repo with existing hook
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()
        existing_hook = tmp_path / ".git" / "hooks" / "pre-commit"
        existing_hook.write_text("#!/bin/bash\necho existing")

        # Create a fake template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "pre-commit.sh"
        template_file.write_text("#!/bin/bash\n# installed by doit\necho new")

        manager = HookManager(project_root=tmp_path)

        with patch.object(manager, "get_template_path") as mock_template:
            mock_template.return_value = template_file
            installed, skipped = manager.install_hooks(force=True)

        assert "pre-commit" in installed
        assert "pre-commit" not in skipped
        # New content installed
        assert "new" in existing_hook.read_text()

    def test_uninstall_hooks_removes_doit_hooks(self, tmp_path: Path):
        """Test uninstall_hooks removes only doit-installed hooks."""
        # Setup git repo with hooks
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()

        doit_hook = tmp_path / ".git" / "hooks" / "pre-commit"
        doit_hook.write_text("#!/bin/bash\n# installed by doit\necho doit")

        other_hook = tmp_path / ".git" / "hooks" / "prepare-commit-msg"
        other_hook.write_text("#!/bin/bash\necho other")

        manager = HookManager(project_root=tmp_path)
        removed = manager.uninstall_hooks()

        assert "pre-commit" in removed
        assert not doit_hook.exists()
        assert other_hook.exists()  # Non-doit hook preserved

    def test_get_installed_hooks(self, tmp_path: Path):
        """Test get_installed_hooks returns only doit hooks."""
        # Setup git repo with hooks
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()

        doit_hook = tmp_path / ".git" / "hooks" / "pre-commit"
        doit_hook.write_text("#!/bin/bash\n# installed by doit\necho doit")

        other_hook = tmp_path / ".git" / "hooks" / "prepare-commit-msg"
        other_hook.write_text("#!/bin/bash\necho other")

        manager = HookManager(project_root=tmp_path)
        installed = manager.get_installed_hooks()

        assert "pre-commit" in installed
        assert "prepare-commit-msg" not in installed


class TestHookManagerBackup:
    """Tests for HookManager backup functionality."""

    def test_backup_creates_backup_dir(self, tmp_path: Path):
        """Test backup creates backup directory."""
        # Setup git repo with hook
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()
        existing_hook = tmp_path / ".git" / "hooks" / "pre-commit"
        existing_hook.write_text("#!/bin/bash\necho existing")

        manager = HookManager(project_root=tmp_path)
        backup_path = manager._backup_hook("pre-commit")

        assert backup_path is not None
        assert backup_path.exists()
        assert (tmp_path / ".doit" / "backups" / "hooks").is_dir()

    def test_backup_creates_manifest(self, tmp_path: Path):
        """Test backup creates manifest file."""
        # Setup git repo with hook
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()
        existing_hook = tmp_path / ".git" / "hooks" / "pre-commit"
        existing_hook.write_text("#!/bin/bash\necho existing")

        manager = HookManager(project_root=tmp_path)
        manager._backup_hook("pre-commit")

        manifest_path = tmp_path / ".doit" / "backups" / "hooks" / "manifest.json"
        assert manifest_path.exists()

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "latest_backup" in manifest
        assert "backups" in manifest
        assert len(manifest["backups"]) > 0
        assert "pre-commit" in manifest["backups"][0]["hooks"]

    def test_restore_hooks_from_backup(self, tmp_path: Path):
        """Test restore_hooks restores from backup."""
        # Setup git repo
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()

        # Create a backup manually
        backup_dir = tmp_path / ".doit" / "backups" / "hooks"
        backup_dir.mkdir(parents=True)

        timestamp = "2026-01-15T12-00-00"
        backup_file = backup_dir / f"pre-commit.{timestamp}.bak"
        backup_file.write_text("#!/bin/bash\necho restored")

        manifest = {
            "latest_backup": timestamp,
            "backups": [{"timestamp": timestamp, "hooks": ["pre-commit"]}]
        }
        (backup_dir / "manifest.json").write_text(json.dumps(manifest))

        manager = HookManager(project_root=tmp_path)
        restored = manager.restore_hooks()

        assert "pre-commit" in restored
        hook_path = tmp_path / ".git" / "hooks" / "pre-commit"
        assert hook_path.exists()
        assert "restored" in hook_path.read_text()

    def test_restore_hooks_no_backup(self, tmp_path: Path):
        """Test restore_hooks raises error when no backups exist."""
        (tmp_path / ".git").mkdir()
        manager = HookManager(project_root=tmp_path)

        with pytest.raises(RuntimeError, match="No hook backups found"):
            manager.restore_hooks()
