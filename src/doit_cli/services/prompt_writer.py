"""Service to write GitHub Copilot prompt files."""

from pathlib import Path

from ..models.sync_models import (
    CommandTemplate,
    FileOperation,
    OperationType,
    SyncResult,
)
from .prompt_transformer import PromptTransformer


class PromptWriter:
    """Writes transformed prompts to .github/prompts/ directory."""

    DEFAULT_PROMPTS_DIR = ".github/prompts"

    def __init__(
        self,
        project_root: Path | None = None,
        transformer: PromptTransformer | None = None,
    ):
        """Initialize the prompt writer.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
            transformer: Transformer to use. Defaults to new PromptTransformer.
        """
        self.project_root = project_root or Path.cwd()
        self.prompts_dir = self.project_root / self.DEFAULT_PROMPTS_DIR
        self.transformer = transformer or PromptTransformer()

    def get_prompts_directory(self) -> Path:
        """Get the prompts directory path."""
        return self.prompts_dir

    def ensure_prompts_directory(self) -> None:
        """Ensure the prompts directory exists."""
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

    def get_prompt_path(self, template: CommandTemplate) -> Path:
        """Get the output path for a prompt file.

        Args:
            template: The command template.

        Returns:
            Path where the prompt file should be written.
        """
        return self.prompts_dir / template.prompt_filename

    def write_prompt(
        self,
        template: CommandTemplate,
        force: bool = False,
    ) -> FileOperation:
        """Write a prompt file from a command template.

        Args:
            template: The command template to transform and write.
            force: If True, overwrite even if file exists and is up-to-date.

        Returns:
            FileOperation describing what happened.
        """
        prompt_path = self.get_prompt_path(template)
        prompt_path_str = str(prompt_path)

        try:
            # Check if prompt already exists and is up-to-date
            if prompt_path.exists() and not force:
                prompt_mtime = prompt_path.stat().st_mtime
                template_mtime = template.modified_at.timestamp()

                if prompt_mtime >= template_mtime:
                    return FileOperation(
                        file_path=prompt_path_str,
                        operation_type=OperationType.SKIPPED,
                        success=True,
                        message="Already up-to-date",
                    )

            # Transform content
            content = self.transformer.transform(template)

            # Ensure directory exists
            self.ensure_prompts_directory()

            # Determine operation type
            operation_type = (
                OperationType.UPDATED if prompt_path.exists() else OperationType.CREATED
            )

            # Write file
            prompt_path.write_text(content, encoding="utf-8")

            return FileOperation(
                file_path=prompt_path_str,
                operation_type=operation_type,
                success=True,
                message=f"{operation_type.value.title()} successfully",
            )

        except (OSError, UnicodeDecodeError) as e:
            return FileOperation(
                file_path=prompt_path_str,
                operation_type=OperationType.FAILED,
                success=False,
                message=str(e),
            )

    def write_prompts(
        self,
        templates: list[CommandTemplate],
        force: bool = False,
    ) -> SyncResult:
        """Write prompt files for multiple command templates.

        Args:
            templates: List of command templates to process.
            force: If True, overwrite even if files are up-to-date.

        Returns:
            SyncResult with summary of all operations.
        """
        result = SyncResult(total_commands=len(templates))

        for template in templates:
            operation = self.write_prompt(template, force=force)
            result.add_operation(operation)

        return result
