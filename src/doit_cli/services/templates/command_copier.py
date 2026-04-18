"""Command-template copier with optional Copilot transformation.

`CommandCopier` is the extracted-and-refactored form of what used to
live as `TemplateManager.copy_templates_for_agent` + friends. It handles
just one job: take a set of bundled command templates and write them to
a target directory, either verbatim (Claude) or transformed through
`PromptTransformer` (Copilot).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from ...models.agent import Agent
from ...models.sync_models import CommandTemplate
from ...models.template import Template
from ..prompt_transformer import PromptTransformer

logger = logging.getLogger(__name__)


@dataclass
class CopyResult:
    """Outcome of copying a batch of templates.

    Each field is a list of the target Paths that ended up in that state.
    This mirrors the dict shape the legacy TemplateManager returned so
    existing callers don't need changes.
    """

    created: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)

    def as_dict(self) -> dict[str, list[Path]]:
        """Return the result in the dict shape TemplateManager used."""
        return {
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
        }


class CommandCopier:
    """Copies command templates to a target directory."""

    def __init__(self, source_dir: Path) -> None:
        """Initialize with the bundled commands source directory.

        Args:
            source_dir: Path to `src/doit_cli/templates/commands/` (or a
                custom override). Only files matching `*.md` are read.
        """
        self.source_dir = source_dir

    def read_templates(self) -> list[Template]:
        """Return Template objects for every `.md` file in the source dir.

        Unparseable files are logged and skipped so a single bad template
        doesn't abort the batch.
        """
        if not self.source_dir.exists():
            return []

        templates: list[Template] = []
        for file_path in sorted(self.source_dir.iterdir()):
            if not (file_path.is_file() and file_path.suffix == ".md"):
                continue
            try:
                templates.append(Template.from_file(file_path, Agent.CLAUDE))
            except (OSError, ValueError, UnicodeDecodeError) as exc:
                logger.debug("skipping unparseable template %s: %s", file_path, exc)
        return templates

    def copy_for_agent(
        self,
        agent: Agent,
        target_dir: Path,
        *,
        overwrite: bool = False,
    ) -> CopyResult:
        """Copy every command template into `target_dir`, transforming for Copilot.

        Claude: verbatim copy, filename is the template's `target_filename`.
        Copilot: run each through `PromptTransformer` and write as
        `doit.<name>.prompt.md`.
        """
        templates = self.read_templates()

        if agent.needs_transformation:
            return self._transform_and_write(templates, target_dir, overwrite=overwrite)

        result = CopyResult()
        for template in templates:
            target_path = target_dir / template.target_filename
            self._write_or_skip(target_path, template.content, overwrite, result)
        return result

    def _transform_and_write(
        self,
        templates: list[Template],
        target_dir: Path,
        *,
        overwrite: bool,
    ) -> CopyResult:
        """Run each template through `PromptTransformer` and write it."""
        result = CopyResult()
        transformer = PromptTransformer()

        for template in templates:
            command_template = CommandTemplate.from_path(template.source_path)
            transformed = transformer.transform(command_template)
            target_path = target_dir / f"doit.{template.name}.prompt.md"
            self._write_or_skip(target_path, transformed, overwrite, result)

        return result

    @staticmethod
    def _write_or_skip(
        target_path: Path,
        content: str,
        overwrite: bool,
        result: CopyResult,
    ) -> None:
        if target_path.exists():
            if overwrite:
                target_path.write_text(content, encoding="utf-8")
                result.updated.append(target_path)
            else:
                result.skipped.append(target_path)
        else:
            target_path.write_text(content, encoding="utf-8")
            result.created.append(target_path)
