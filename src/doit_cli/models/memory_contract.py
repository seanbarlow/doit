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
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final

ID_PATTERN = re.compile(r"^(app|platform)-[a-z][a-z0-9-]+$")
ICON_PATTERN = re.compile(r"^[A-Z0-9]{2,4}$")
VALID_KINDS = frozenset({"application", "service"})
VALID_PHASES = frozenset({1, 2, 3, 4})
VALID_PRIORITIES = ("High", "Medium", "Low")


REQUIRED_FRONTMATTER_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "name",
    "kind",
    "phase",
    "icon",
    "tagline",
    "dependencies",
)
"""Required frontmatter keys, in schema order.

Authoritative source for both the memory validator and the constitution
migrator. Mirrors the ``required`` array in
``src/doit_cli/schemas/frontmatter.schema.json`` index-by-index.
"""


PLACEHOLDER_REGISTRY: Final[Mapping[str, Any]] = {
    "id": "[PROJECT_ID]",
    "name": "[PROJECT_NAME]",
    "kind": "[PROJECT_KIND]",
    "phase": "[PROJECT_PHASE]",
    "icon": "[PROJECT_ICON]",
    "tagline": "[PROJECT_TAGLINE]",
    "dependencies": ["[PROJECT_DEPENDENCIES]"],
}
"""Exact-match sentinel values the constitution migrator emits.

The migrator prepends these when a required frontmatter field is missing;
the validator classifies matching values as WARNING (not ERROR). Callers
detect placeholders with ``==`` — reuse of a sentinel across fields would
make detection ambiguous.
"""


def is_placeholder_value(field_name: str, value: Any) -> bool:
    """Return ``True`` when ``value`` exactly matches ``field_name``'s placeholder."""

    expected = PLACEHOLDER_REGISTRY.get(field_name)
    if expected is None:
        return False
    return value == expected


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
    phase: int | str
    icon: str
    tagline: str
    competitor: str | None = None
    # `dependencies` is typed as ``Any`` at the dataclass layer because
    # YAML can yield anything here and the validator must be able to flag
    # non-list values at runtime. :meth:`from_dict` no longer coerces via
    # ``list(...)`` for the same reason.
    dependencies: Any = field(default_factory=list)
    consumers: str | None = None
    status: str | None = None

    REQUIRED_FIELDS = REQUIRED_FRONTMATTER_FIELDS

    @classmethod
    def from_dict(cls, data: dict) -> ConstitutionFrontmatter:
        """Build an instance from a loaded YAML dict.

        Missing optional fields default to ``None`` / ``[]``. Missing required
        fields are allowed here — they'll surface as issues when
        :meth:`validate` runs. Placeholder values (e.g. ``[PROJECT_PHASE]``)
        are preserved verbatim so :meth:`validate` can classify them as
        WARNING rather than raising during construction.
        """

        phase_raw = data.get("phase")
        phase_val: int | str
        if isinstance(phase_raw, bool):
            # bools are ints in Python; treat as bad input preserving the value.
            phase_val = str(phase_raw)
        elif isinstance(phase_raw, int):
            phase_val = phase_raw
        elif isinstance(phase_raw, str):
            try:
                phase_val = int(phase_raw)
            except ValueError:
                phase_val = phase_raw  # placeholder or otherwise non-numeric
        else:
            phase_val = 0

        # Preserve the raw ``dependencies`` value (no ``list(...)`` coercion):
        # the validator needs to see a non-list input as a contract error,
        # and ``list("string")`` would silently split it into characters.
        deps_raw: Any = data.get("dependencies")
        if deps_raw is None:
            deps_raw = []

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            kind=data.get("kind", ""),
            phase=phase_val,
            icon=data.get("icon", ""),
            tagline=data.get("tagline", ""),
            competitor=data.get("competitor"),
            dependencies=deps_raw,
            consumers=data.get("consumers"),
            status=data.get("status"),
        )

    def validate(self, file: str = "constitution.md") -> list[MemoryContractIssue]:
        """Return a list of contract issues. Empty list means valid.

        Fields whose values exactly match the corresponding
        :data:`PLACEHOLDER_REGISTRY` entry are reported as
        :attr:`MemoryIssueSeverity.WARNING` ("run /doit.constitution to
        enrich") instead of ERROR, so a freshly-migrated constitution
        passes ``doit verify-memory`` immediately.
        """

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

        def warn(field_name: str) -> None:
            issues.append(
                MemoryContractIssue(
                    file=file,
                    severity=MemoryIssueSeverity.WARNING,
                    message=(
                        f"frontmatter field '{field_name}' contains placeholder value"
                        " — run /doit.constitution to enrich"
                    ),
                    field_name=field_name,
                )
            )

        # id -----------------------------------------------------------------
        if is_placeholder_value("id", self.id):
            warn("id")
        elif not self.id:
            err("frontmatter field 'id' is required", "id")
        elif not ID_PATTERN.match(self.id):
            err(
                f"frontmatter id '{self.id}' must match ^(app|platform)-... pattern",
                "id",
            )

        # name ---------------------------------------------------------------
        if is_placeholder_value("name", self.name):
            warn("name")
        elif not self.name:
            err("frontmatter field 'name' is required", "name")

        # kind ---------------------------------------------------------------
        if is_placeholder_value("kind", self.kind):
            warn("kind")
        elif not self.kind:
            err("frontmatter field 'kind' is required", "kind")
        elif self.kind not in VALID_KINDS:
            err(
                f"frontmatter kind '{self.kind}' must be one of {sorted(VALID_KINDS)}",
                "kind",
            )

        # phase --------------------------------------------------------------
        if is_placeholder_value("phase", self.phase):
            warn("phase")
        elif self.phase not in VALID_PHASES:
            err(
                f"frontmatter phase {self.phase!r} must be 1, 2, 3, or 4",
                "phase",
            )

        # icon ---------------------------------------------------------------
        if is_placeholder_value("icon", self.icon):
            warn("icon")
        elif not self.icon:
            err("frontmatter field 'icon' is required", "icon")
        elif not ICON_PATTERN.match(self.icon):
            err(
                f"frontmatter icon '{self.icon}' must be 2-4 uppercase chars/digits",
                "icon",
            )

        # tagline ------------------------------------------------------------
        if is_placeholder_value("tagline", self.tagline):
            warn("tagline")
        elif not self.tagline:
            err("frontmatter field 'tagline' is required", "tagline")

        # dependencies -------------------------------------------------------
        if is_placeholder_value("dependencies", self.dependencies):
            warn("dependencies")
        elif not isinstance(self.dependencies, list):
            err(
                "frontmatter field 'dependencies' must be a list",
                "dependencies",
            )

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
        import yaml
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
