"""Template manager service for copying bundled templates."""

import importlib.resources
from pathlib import Path
from typing import Optional
import shutil

from ..models.agent import Agent
from ..models.template import Template, DOIT_COMMANDS


class TemplateManager:
    """Service for managing and copying bundled templates."""

    # Copilot instructions section markers
    COPILOT_SECTION_START = "<!-- DOIT INSTRUCTIONS START -->"
    COPILOT_SECTION_END = "<!-- DOIT INSTRUCTIONS END -->"

    def __init__(self, custom_source: Optional[Path] = None):
        """Initialize template manager.

        Args:
            custom_source: Optional custom template source directory.
                          If None, uses bundled templates.
        """
        self.custom_source = custom_source

    def get_template_source_path(self, agent: Agent) -> Path:
        """Get the source path for templates.

        Args:
            agent: Target agent

        Returns:
            Path to template directory
        """
        if self.custom_source:
            return self.custom_source / agent.template_directory

        # Use bundled templates
        # Templates are bundled at doit_cli/templates/commands/ and doit_cli/templates/prompts/
        try:
            # Try importlib.resources first (Python 3.9+)
            import importlib.resources as resources

            # Get the package location
            with resources.as_file(resources.files("doit_cli")) as pkg_path:
                return pkg_path / "templates" / agent.template_directory
        except (ImportError, TypeError, AttributeError):
            # Fallback: look relative to this file
            # During development, templates are at repo_root/templates/
            module_path = Path(__file__).parent.parent.parent.parent
            return module_path / "templates" / agent.template_directory

    def get_bundled_templates(self, agent: Agent) -> list[Template]:
        """Get all bundled templates for an agent.

        Args:
            agent: Target agent

        Returns:
            List of Template objects
        """
        source_dir = self.get_template_source_path(agent)

        if not source_dir.exists():
            return []

        templates = []
        for file_path in source_dir.iterdir():
            if file_path.is_file() and file_path.suffix == ".md":
                try:
                    template = Template.from_file(file_path, agent)
                    templates.append(template)
                except Exception:
                    # Skip files that can't be parsed
                    continue

        return templates

    def validate_template_source(self, agent: Agent) -> dict:
        """Validate template source has all required templates.

        Args:
            agent: Target agent

        Returns:
            Dict with 'valid' bool, 'found' list, 'missing' list, 'extra' list,
            and 'source_exists' bool
        """
        source_path = self.get_template_source_path(agent)
        source_exists = source_path.exists()

        if not source_exists:
            return {
                "valid": False,
                "found": [],
                "missing": list(DOIT_COMMANDS),
                "extra": [],
                "source_exists": False,
                "source_path": str(source_path),
            }

        templates = self.get_bundled_templates(agent)
        found_names = {t.name for t in templates}
        required = set(DOIT_COMMANDS)

        missing = required - found_names
        extra = found_names - required

        return {
            "valid": len(missing) == 0,
            "found": list(found_names),
            "missing": list(missing),
            "extra": list(extra),
            "source_exists": True,
            "source_path": str(source_path),
        }

    def validate_custom_source(self) -> dict:
        """Validate custom template source directory.

        Returns:
            Dict with validation results for all agents
        """
        if not self.custom_source:
            return {"valid": True, "is_custom": False}

        if not self.custom_source.exists():
            return {
                "valid": False,
                "is_custom": True,
                "error": f"Custom template directory does not exist: {self.custom_source}",
            }

        if not self.custom_source.is_dir():
            return {
                "valid": False,
                "is_custom": True,
                "error": f"Custom template path is not a directory: {self.custom_source}",
            }

        # Check for at least one agent's templates
        claude_result = self.validate_template_source(Agent.CLAUDE)
        copilot_result = self.validate_template_source(Agent.COPILOT)

        has_any_templates = (
            claude_result.get("source_exists", False) or
            copilot_result.get("source_exists", False)
        )

        return {
            "valid": has_any_templates,
            "is_custom": True,
            "claude": claude_result,
            "copilot": copilot_result,
            "warnings": self._get_validation_warnings(claude_result, copilot_result),
        }

    def _get_validation_warnings(self, claude_result: dict, copilot_result: dict) -> list[str]:
        """Generate warning messages from validation results.

        Args:
            claude_result: Validation result for Claude
            copilot_result: Validation result for Copilot

        Returns:
            List of warning messages
        """
        warnings = []

        if not claude_result.get("source_exists", False):
            warnings.append(
                f"No Claude templates found at: {claude_result.get('source_path', 'unknown')}"
            )
        elif claude_result.get("missing"):
            warnings.append(
                f"Missing Claude templates: {', '.join(sorted(claude_result['missing']))}"
            )

        if not copilot_result.get("source_exists", False):
            warnings.append(
                f"No Copilot templates found at: {copilot_result.get('source_path', 'unknown')}"
            )
        elif copilot_result.get("missing"):
            warnings.append(
                f"Missing Copilot templates: {', '.join(sorted(copilot_result['missing']))}"
            )

        return warnings

    def copy_templates_for_agent(
        self,
        agent: Agent,
        target_dir: Path,
        overwrite: bool = False,
    ) -> dict:
        """Copy templates for an agent to target directory.

        Args:
            agent: Target agent
            target_dir: Destination directory
            overwrite: Whether to overwrite existing files

        Returns:
            Dict with 'created', 'updated', 'skipped' lists of paths
        """
        result = {
            "created": [],
            "updated": [],
            "skipped": [],
        }

        templates = self.get_bundled_templates(agent)

        for template in templates:
            target_path = target_dir / template.target_filename

            if target_path.exists():
                if overwrite:
                    # Overwrite existing file
                    target_path.write_text(template.content, encoding="utf-8")
                    result["updated"].append(target_path)
                else:
                    # Skip existing file
                    result["skipped"].append(target_path)
            else:
                # Create new file
                target_path.write_text(template.content, encoding="utf-8")
                result["created"].append(target_path)

        return result

    def copy_single_template(
        self,
        agent: Agent,
        template_name: str,
        target_dir: Path,
        overwrite: bool = False,
    ) -> Optional[Path]:
        """Copy a single template.

        Args:
            agent: Target agent
            template_name: Name of template (e.g., 'specit')
            target_dir: Destination directory
            overwrite: Whether to overwrite existing file

        Returns:
            Path to created/updated file, or None if skipped
        """
        templates = self.get_bundled_templates(agent)
        template = next((t for t in templates if t.name == template_name), None)

        if template is None:
            return None

        target_path = target_dir / template.target_filename

        if target_path.exists() and not overwrite:
            return None

        target_path.write_text(template.content, encoding="utf-8")
        return target_path

    def create_copilot_instructions(
        self,
        target_path: Path,
        update_only: bool = False,
    ) -> bool:
        """Create or update .github/copilot-instructions.md with doit section.

        Args:
            target_path: Path to copilot-instructions.md
            update_only: If True, only update existing file

        Returns:
            True if file was created/updated
        """
        doit_section = f"""{self.COPILOT_SECTION_START}
## Doit Workflow Commands

This project uses the Doit workflow for structured development. The following prompts are available in `.github/prompts/`:

| Command | Description |
|---------|-------------|
| #doit-specit | Create feature specifications |
| #doit-planit | Generate implementation plans |
| #doit-taskit | Create task breakdowns |
| #doit-implementit | Execute implementation tasks |
| #doit-testit | Run tests and generate reports |
| #doit-reviewit | Review code for quality |
| #doit-checkin | Complete feature and create PR |
| #doit-constitution | Manage project constitution |
| #doit-scaffoldit | Scaffold new projects |
| #doit-roadmapit | Manage feature roadmap |
| #doit-documentit | Manage documentation |

Use the agent mode (`@workspace /doit-*`) for multi-step workflows.
{self.COPILOT_SECTION_END}"""

        if target_path.exists():
            content = target_path.read_text(encoding="utf-8")

            # Check if doit section already exists
            if self.COPILOT_SECTION_START in content:
                # Replace existing section
                start_idx = content.find(self.COPILOT_SECTION_START)
                end_idx = content.find(self.COPILOT_SECTION_END)
                if end_idx != -1:
                    end_idx += len(self.COPILOT_SECTION_END)
                    new_content = content[:start_idx] + doit_section + content[end_idx:]
                    target_path.write_text(new_content, encoding="utf-8")
                    return True
            else:
                # Append doit section
                new_content = content.rstrip() + "\n\n" + doit_section + "\n"
                target_path.write_text(new_content, encoding="utf-8")
                return True
        elif not update_only:
            # Create new file
            content = f"# Copilot Instructions\n\n{doit_section}\n"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
            return True

        return False
