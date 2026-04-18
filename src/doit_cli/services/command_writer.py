"""Service to write Claude Code command files."""

from __future__ import annotations

from pathlib import Path

from ..models.sync_models import (
    CommandTemplate,
    FileOperation,
    OperationType,
    SyncResult,
)


class CommandWriter:
    """Writes command files to .claude/commands/ directory (direct copy, no transformation)."""

    DEFAULT_COMMANDS_DIR = ".claude/commands"

    def __init__(
        self,
        project_root: Path | None = None,
    ):
        """Initialize the command writer.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.commands_dir = self.project_root / self.DEFAULT_COMMANDS_DIR

    def get_commands_directory(self) -> Path:
        """Get the commands directory path."""
        return self.commands_dir

    def ensure_commands_directory(self) -> None:
        """Ensure the commands directory exists."""
        self.commands_dir.mkdir(parents=True, exist_ok=True)

    def get_command_path(self, template: CommandTemplate) -> Path:
        """Get the output path for a command file.

        Args:
            template: The command template.

        Returns:
            Path where the command file should be written.
        """
        # Keep the original filename (e.g., doit.checkin.md)
        return self.commands_dir / template.path.name

    def write_command(
        self,
        template: CommandTemplate,
        force: bool = False,
    ) -> FileOperation:
        """Write a command file from a template (direct copy, no transformation).

        Args:
            template: The command template to copy.
            force: If True, overwrite even if file exists and is up-to-date.

        Returns:
            FileOperation describing what happened.
        """
        command_path = self.get_command_path(template)
        command_path_str = str(command_path)

        try:
            # Check if command already exists and is up-to-date
            if command_path.exists() and not force:
                command_mtime = command_path.stat().st_mtime
                template_mtime = template.modified_at.timestamp()

                if command_mtime >= template_mtime:
                    return FileOperation(
                        file_path=command_path_str,
                        operation_type=OperationType.SKIPPED,
                        success=True,
                        message="Already up-to-date",
                    )

            # Ensure directory exists
            self.ensure_commands_directory()

            # Determine operation type
            operation_type = (
                OperationType.UPDATED if command_path.exists() else OperationType.CREATED
            )

            # Write file (direct copy of content, no transformation)
            command_path.write_text(template.content, encoding="utf-8")

            return FileOperation(
                file_path=command_path_str,
                operation_type=operation_type,
                success=True,
                message=f"{operation_type.value.title()} successfully",
            )

        except (OSError, UnicodeDecodeError) as e:
            return FileOperation(
                file_path=command_path_str,
                operation_type=OperationType.FAILED,
                success=False,
                message=str(e),
            )

    def write_commands(
        self,
        templates: list[CommandTemplate],
        force: bool = False,
    ) -> SyncResult:
        """Write command files for multiple templates.

        Args:
            templates: List of command templates to process.
            force: If True, overwrite even if files are up-to-date.

        Returns:
            SyncResult with summary of all operations.
        """
        result = SyncResult(total_commands=len(templates))

        for template in templates:
            operation = self.write_command(template, force=force)
            result.add_operation(operation)

        return result
