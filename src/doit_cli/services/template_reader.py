"""Service to read and scan doit command templates."""

from pathlib import Path

from ..models.sync_models import CommandTemplate


class TemplateReader:
    """Reads command templates from bundled or project templates directory.

    Supports two template locations:
    - Bundled: src/doit_cli/templates/commands/ (for the CLI repo itself)
    - Project: .doit/templates/commands/ (for end-user projects)

    When running in the CLI repo, bundled templates are used as source of truth.
    """

    BUNDLED_TEMPLATES_DIR = "src/doit_cli/templates/commands"
    PROJECT_TEMPLATES_DIR = ".doit/templates/commands"
    COMMAND_PATTERN = "doit.*.md"

    def __init__(self, project_root: Path | None = None):
        """Initialize the template reader.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.templates_dir = self._resolve_templates_directory()

    def _resolve_templates_directory(self) -> Path:
        """Resolve the templates directory, preferring bundled over project.

        Returns:
            Path to the templates directory to use.
        """
        # First, check for bundled templates (CLI repo development)
        bundled_dir = self.project_root / self.BUNDLED_TEMPLATES_DIR
        if bundled_dir.exists() and any(bundled_dir.glob(self.COMMAND_PATTERN)):
            return bundled_dir

        # Fall back to project templates (end-user projects)
        return self.project_root / self.PROJECT_TEMPLATES_DIR

    def get_templates_directory(self) -> Path:
        """Get the templates directory path."""
        return self.templates_dir

    def is_using_bundled_templates(self) -> bool:
        """Check if using bundled templates (CLI repo) vs project templates.

        Returns:
            True if using bundled templates, False if using project templates.
        """
        return self.BUNDLED_TEMPLATES_DIR in str(self.templates_dir)

    def scan_templates(self, filter_name: str | None = None) -> list[CommandTemplate]:
        """Scan for command templates in the templates directory.

        Args:
            filter_name: Optional command name to filter by (e.g., "doit.checkin").

        Returns:
            List of CommandTemplate objects found.
        """
        if not self.templates_dir.exists():
            return []

        templates = []
        pattern = self.COMMAND_PATTERN

        for path in sorted(self.templates_dir.glob(pattern)):
            if not path.is_file():
                continue

            # Apply name filter if specified
            if filter_name:
                # Allow matching with or without .md extension
                filter_stem = filter_name.replace(".md", "")
                if path.stem != filter_stem:
                    continue

            try:
                template = CommandTemplate.from_path(path)
                templates.append(template)
            except (OSError, UnicodeDecodeError) as e:
                # Log error but continue with other templates
                print(f"Warning: Could not read template {path}: {e}")

        return templates

    def get_template(self, name: str) -> CommandTemplate | None:
        """Get a specific command template by name.

        Args:
            name: Command name (e.g., "doit.checkin" or "doit.checkin.md").

        Returns:
            CommandTemplate if found, None otherwise.
        """
        templates = self.scan_templates(filter_name=name)
        return templates[0] if templates else None

    def list_template_names(self) -> list[str]:
        """List all available template names.

        Returns:
            List of template names (e.g., ["doit.checkin", "doit.specit", ...]).
        """
        templates = self.scan_templates()
        return [t.name for t in templates]
