"""Service to read and scan doit command templates."""

import importlib.resources
from pathlib import Path

from ..models.sync_models import CommandTemplate


class TemplateReader:
    """Reads command templates from bundled or project templates directory.

    Supports three template locations (checked in order):
    1. CLI repo development: src/doit_cli/templates/commands/
    2. Installed package: via importlib.resources (doit_cli.templates.commands)
    3. Project templates: .doit/templates/commands/ (for end-user projects)

    When running from an installed package, bundled templates are used.
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
        """Resolve the templates directory.

        Priority order:
        1. Project templates (.doit/templates/commands/) - allows customization
        2. CLI repo development (src/doit_cli/templates/commands/)
        3. Installed package templates (via importlib.resources)

        Returns:
            Path to the templates directory to use.
        """
        # First, check for project templates (allows customization)
        project_dir = self.project_root / self.PROJECT_TEMPLATES_DIR
        if project_dir.exists() and any(project_dir.glob(self.COMMAND_PATTERN)):
            return project_dir

        # Second, check for CLI repo development templates
        bundled_dir = self.project_root / self.BUNDLED_TEMPLATES_DIR
        if bundled_dir.exists() and any(bundled_dir.glob(self.COMMAND_PATTERN)):
            return bundled_dir

        # Third, try to find templates from installed package
        package_templates = self._get_package_templates_directory()
        if package_templates and package_templates.exists():
            if any(package_templates.glob(self.COMMAND_PATTERN)):
                return package_templates

        # Fall back to project templates path (will be empty/not exist)
        return project_dir

    def _get_package_templates_directory(self) -> Path | None:
        """Get the templates directory from the installed package.

        Returns:
            Path to bundled templates directory, or None if not found.
        """
        try:
            # Use importlib.resources to find package templates
            # Get the actual path from the package location
            pkg_files = importlib.resources.files("doit_cli")
            templates_path = pkg_files.joinpath("templates/commands")

            # Check if it's a real path we can use
            if hasattr(templates_path, "_path"):
                # Direct filesystem path (editable install or source)
                return Path(templates_path._path)

            # Try to get path via traversable
            # For installed packages, get the actual location
            import doit_cli
            pkg_location = Path(doit_cli.__file__).parent
            templates_dir = pkg_location / "templates" / "commands"
            if templates_dir.exists():
                return templates_dir

            return None
        except (ImportError, TypeError, AttributeError, FileNotFoundError):
            return None

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
