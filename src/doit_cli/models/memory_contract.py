"""Models for the .doit/memory/* contract.

This module defines the shape that doit's downstream tooling (notably the
docs generator used by velocity-platform) expects from a project's memory
files. The contract consists of:

- A YAML frontmatter block at the top of ``constitution.md`` (:class:`ConstitutionFrontmatter`).
- A ``## Open Questions`` table in ``roadmap.md`` (rows modelled by :class:`OpenQuestion`).
- Structural expectations (headings under ``## Tech Stack``, ``## Active Requirements``)
  enforced by :mod:`doit_cli.services.memory_validator`.

We deliberately avoid a Pydantic dependency (doit uses stdlib dataclasses
throughout) and instead provide a ``validate`` method on each model that
returns a list of issues.

The canonical JSON Schema is shipped at
``src/doit_cli/schemas/frontmatter.schema.json`` and surfaced via
``doit memory schema``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


ID_PATTERN = re.compile(r"^(app|platform)-[a-z][a-z0-9-]+$")
ICON_PATTERN = re.compile(r"^[A-Z0-9]{2,4}$")
VALID_KINDS = frozenset({"application", "service"})
VALID_PHASES = frozenset({1, 2, 3, 4})
VALID_PRIORITIES = ("High", "Medium", "Low")


class MemoryIssueSeverity(str, Enum):
    """Severity level for memory-file contract issues."""

    ERROR = "error"
    WARNING = "warning"


@dataclass
class MemoryContractIssue:
    """One validation finding against the memory-file contract.

    Attributes:
        file: Path to the offending file, relative to the project root.
        severity: :class:`MemoryIssueSeverity` value.
        message: Human-readable description of the problem.
        line: 1-based line number inside ``file`` if known, else ``None``.
        field_name: Name of the offending frontmatter field, if applicable.
    """

    file: str
    severity: MemoryIssueSeverity
    message: str
    line: int | None = None
    field_name: str | None = None

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "severity": self.severity.value,
            "message": self.message,
            "line": self.line,
            "field": self.field_name,
        }


@dataclass
class ConstitutionFrontmatter:
    """YAML frontmatter contract for ``.doit/memory/constitution.md``.

    Every project scaffolded by doit emits a placeholder version of this
    block. The :skill:`doit.constitution` skill is responsible for filling
    it in. The docs generator in ``platform-docs-site/tools/gen-data`` reads
    it via ``gray-matter`` to produce component metadata.
    """

    id: str
    name: str
    kind: str
    phase: int
    icon: str
    tagline: str
    competitor: str | None = None
    dependencies: list[str] = field(default_factory=list)
    consumers: str | None = None
    status: str | None = None

    REQUIRED_FIELDS = ("id", "name", "kind", "phase", "icon", "tagline", "dependencies")

    @classmethod
    def from_dict(cls, data: dict) -> ConstitutionFrontmatter:
        """Build an instance from a loaded YAML dict.

        Missing optional fields default to ``None`` / ``[]``. Missing required
        fields are allowed here — they'll surface as issues when
        :meth:`validate` runs.
        """

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            kind=data.get("kind", ""),
            phase=int(data["phase"]) if data.get("phase") is not None else 0,
            icon=data.get("icon", ""),
            tagline=data.get("tagline", ""),
            competitor=data.get("competitor"),
            dependencies=list(data.get("dependencies") or []),
            consumers=data.get("consumers"),
            status=data.get("status"),
        )

    def validate(self, file: str = "constitution.md") -> list[MemoryContractIssue]:
        """Return a list of contract issues. Empty list means valid."""

        issues: list[MemoryContractIssue] = []

        def err(msg: str, field_name: str | None = None) -> None:
            issues.append(
                MemoryContractIssue(
                    file=file,
                    severity=MemoryIssueSeverity.ERROR,
                    message=msg,
                    field_name=field_name,
                )
            )

        if not self.id:
            err("frontmatter field 'id' is required", "id")
        elif not ID_PATTERN.match(self.id):
            err(
                f"frontmatter id '{self.id}' must match ^(app|platform)-... pattern",
                "id",
            )

        if not self.name:
            err("frontmatter field 'name' is required", "name")

        if not self.kind:
            err("frontmatter field 'kind' is required", "kind")
        elif self.kind not in VALID_KINDS:
            err(
                f"frontmatter kind '{self.kind}' must be one of {sorted(VALID_KINDS)}",
                "kind",
            )

        if self.phase not in VALID_PHASES:
            err(
                f"frontmatter phase {self.phase} must be 1, 2, 3, or 4",
                "phase",
            )

        if not self.icon:
            err("frontmatter field 'icon' is required", "icon")
        elif not ICON_PATTERN.match(self.icon):
            err(
                f"frontmatter icon '{self.icon}' must be 2-4 uppercase chars/digits",
                "icon",
            )

        if not self.tagline:
            err("frontmatter field 'tagline' is required", "tagline")

        if not isinstance(self.dependencies, list):
            err("frontmatter field 'dependencies' must be a list", "dependencies")

        return issues


@dataclass
class OpenQuestion:
    """One row in the ``## Open Questions`` GFM table of a roadmap.md.

    Column order on disk is fixed: ``Priority | Question | Owner``.
    """

    priority: str
    question: str
    owner: str = "N/A"

    @classmethod
    def normalise(
        cls, priority: str, question: str, owner: str
    ) -> tuple[OpenQuestion | None, MemoryContractIssue | None]:
        """Build an :class:`OpenQuestion` with normalised priority/owner.

        Returns ``(question, None)`` on success or ``(None, issue)`` when the
        priority cell fails the ``High|Medium|Low`` constraint.
        """

        p_key = (priority or "").strip()
        match = next(
            (p for p in VALID_PRIORITIES if p.lower() == p_key.lower()),
            None,
        )
        if match is None:
            return None, MemoryContractIssue(
                file="roadmap.md",
                severity=MemoryIssueSeverity.WARNING,
                message=(
                    f"open-questions row has priority '{priority}'; "
                    f"must be one of {VALID_PRIORITIES}"
                ),
            )

        o = (owner or "").strip()
        if not o or o in {"\u2014", "-"} or o.lower() == "n/a":
            o = "N/A"

        return (
            cls(priority=match, question=(question or "").strip(), owner=o),
            None,
        )


def split_frontmatter(source: str) -> tuple[dict, str, int]:
    """Split a markdown source into (frontmatter-dict, body, body-start-line).

    Returns ``({}, source, 1)`` when no ``---\\n...---\\n`` block is found at
    the top of the file. Missing PyYAML lands as an empty dict.
    """

    match = re.match(r"^---\n(.*?\n)---\n", source, re.DOTALL)
    if not match:
        return {}, source, 1

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:  # pragma: no cover - pyyaml is a base dep
        return {}, source, 1

    raw = match.group(1)
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        data = {}

    body = source[match.end():]
    body_start_line = source[: match.end()].count("\n") + 1
    return data if isinstance(data, dict) else {}, body, body_start_line
