"""Service to detect synchronization drift between commands and prompts."""

from datetime import datetime
from pathlib import Path

from ..models.sync_models import CommandTemplate, PromptFile, SyncStatus, SyncStatusEnum
from .template_reader import TemplateReader


class DriftDetector:
    """Detects when command templates and prompts are out of sync."""

    DEFAULT_PROMPTS_DIR = ".github/prompts"

    def __init__(self, project_root: Path | None = None):
        """Initialize the drift detector.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        # Use TemplateReader to resolve the correct templates directory
        reader = TemplateReader(self.project_root)
        self.templates_dir = reader.get_templates_directory()
        self.prompts_dir = self.project_root / self.DEFAULT_PROMPTS_DIR

    def get_prompt_path(self, template: CommandTemplate) -> Path:
        """Get the expected prompt file path for a template.

        Args:
            template: The command template.

        Returns:
            Expected prompt file path.
        """
        return self.prompts_dir / template.prompt_filename

    def check_sync_status(self, template: CommandTemplate) -> SyncStatus:
        """Check the sync status for a command template.

        Args:
            template: The command template to check.

        Returns:
            SyncStatus indicating whether prompt is synchronized.
        """
        prompt_path = self.get_prompt_path(template)
        now = datetime.now()

        if not prompt_path.exists():
            return SyncStatus(
                command_name=template.name,
                status=SyncStatusEnum.MISSING,
                checked_at=now,
                reason="No corresponding prompt file exists",
            )

        # Compare timestamps
        prompt_mtime = prompt_path.stat().st_mtime
        template_mtime = template.modified_at.timestamp()

        if template_mtime > prompt_mtime:
            return SyncStatus(
                command_name=template.name,
                status=SyncStatusEnum.OUT_OF_SYNC,
                checked_at=now,
                reason="Command template modified after prompt was generated",
            )

        return SyncStatus(
            command_name=template.name,
            status=SyncStatusEnum.SYNCHRONIZED,
            checked_at=now,
            reason="Prompt is up-to-date with command template",
        )

    def check_all(self, templates: list[CommandTemplate]) -> list[SyncStatus]:
        """Check sync status for all templates.

        Args:
            templates: List of command templates to check.

        Returns:
            List of SyncStatus for each template.
        """
        return [self.check_sync_status(t) for t in templates]

    def get_out_of_sync(self, templates: list[CommandTemplate]) -> list[SyncStatus]:
        """Get only the templates that are out of sync.

        Args:
            templates: List of command templates to check.

        Returns:
            List of SyncStatus for templates that need synchronization.
        """
        statuses = self.check_all(templates)
        return [s for s in statuses if s.status != SyncStatusEnum.SYNCHRONIZED]

    def is_all_synced(self, templates: list[CommandTemplate]) -> bool:
        """Check if all templates are synchronized.

        Args:
            templates: List of command templates to check.

        Returns:
            True if all templates are synchronized, False otherwise.
        """
        return len(self.get_out_of_sync(templates)) == 0
