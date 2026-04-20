"""Migrate ``.doit/memory/constitution.md`` to the 0.3.0 frontmatter shape.

Users on projects initialized before the memory contract landed have
constitutions with no YAML frontmatter block. This service is invoked by
``doit update`` to detect shape drift and either prepend a placeholder
skeleton or patch in missing required fields, preserving the prose body
byte-for-byte.

Downstream, the ``/doit.constitution`` skill replaces the placeholder
values with concrete ones inferred from the body.

Public surface:

- :data:`REQUIRED_FIELDS` — the seven fields the schema requires, in
  schema order.
- :data:`PLACEHOLDER_REGISTRY` — exact-match sentinel values emitted for
  each required field. The memory validator imports this mapping to
  classify a placeholder as WARNING (not ERROR).
- :class:`MigrationAction` — enum of the four outcomes the migrator can
  report.
- :class:`MigrationResult` — frozen dataclass returned by
  :func:`migrate_constitution`.
- :func:`migrate_constitution` — the one-function public API.

The service **never raises**. Callers inspect :attr:`MigrationResult.error`
to decide whether to propagate an exit code.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from ..errors import DoitError, DoitValidationError
from ..models.memory_contract import (
    PLACEHOLDER_REGISTRY,
)
from ..models.memory_contract import (
    REQUIRED_FRONTMATTER_FIELDS as REQUIRED_FIELDS,
)

__all__ = (
    "PLACEHOLDER_REGISTRY",
    "REQUIRED_FIELDS",
    "ConstitutionMigrationError",
    "MalformedFrontmatterError",
    "MigrationAction",
    "MigrationResult",
    "migrate_constitution",
)


class MigrationAction(str, Enum):
    """Outcome categories for :func:`migrate_constitution`."""

    NO_OP = "no_op"
    """File is already valid-shape, or does not exist. No write performed."""

    PREPENDED = "prepended"
    """File had no frontmatter block; a placeholder skeleton was prepended."""

    PATCHED = "patched"
    """File had partial frontmatter; missing required fields were added."""

    ERROR = "error"
    """Frontmatter block is present but YAML is malformed; no write performed."""


@dataclass(frozen=True)
class MigrationResult:
    """Report returned by :func:`migrate_constitution`.

    Attributes:
        path: The file the migrator was asked to act on.
        action: Which branch of the decision tree ran.
        added_fields: Required-field keys that were added by this run, in
            schema order. Empty for ``NO_OP`` / ``ERROR``.
        preserved_body_hash: SHA-256 of the post-frontmatter body bytes,
            unchanged across input and output when ``action`` is
            ``NO_OP``, ``PREPENDED``, or ``PATCHED``. ``None`` when
            ``action == ERROR``.
        error: The :class:`DoitError` subclass describing the failure
            when ``action == ERROR``. ``None`` otherwise.
    """

    path: Path
    action: MigrationAction
    added_fields: tuple[str, ...] = ()
    preserved_body_hash: bytes | None = None
    error: DoitError | None = None


class ConstitutionMigrationError(DoitError):
    """Base class for migration errors.

    Subclasses carry an :attr:`exit_code` hint that CLI callers can use
    when turning a :class:`MigrationResult` into a ``typer.Exit``.
    """


class MalformedFrontmatterError(DoitValidationError, ConstitutionMigrationError):
    """Raised when an existing ``---`` block contains invalid YAML.

    The message includes the line and column from
    ``yaml.YAMLError.problem_mark`` when available.
    """


# ---------------------------------------------------------------------------
# Internal helpers


_FRONTMATTER_RE = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)


def _parse_frontmatter(source: str) -> tuple[dict[str, Any] | None, str, bool]:
    """Detect and parse the frontmatter block.

    Returns a tuple ``(parsed, body, has_block)`` where:

    - ``parsed`` is the loaded YAML dict, or ``None`` when YAML is
      malformed.
    - ``body`` is everything after the closing ``---\\n`` (or the whole
      source when no block is present).
    - ``has_block`` indicates whether a ``---\\n...---\\n`` block exists
      at the top of the file.

    This is intentionally stricter than
    :func:`doit_cli.models.memory_contract.split_frontmatter`, which
    silently hides ``yaml.YAMLError`` — the migrator needs to surface
    malformed YAML to the user.
    """

    match = _FRONTMATTER_RE.match(source)
    if not match:
        return {}, source, False

    try:
        import yaml
    except ImportError:  # pragma: no cover - pyyaml is a base dep
        return {}, source, True

    raw = match.group(1)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, source[match.end():], True

    if data is None:
        data = {}
    if not isinstance(data, dict):
        # A frontmatter block whose YAML is a scalar/list is malformed
        # from our schema's point of view.
        return None, source[match.end():], True

    return data, source[match.end():], True


def _format_frontmatter(data: Mapping[str, Any]) -> str:
    """Render ``data`` as a YAML frontmatter block.

    Emits required fields in :data:`REQUIRED_FIELDS` order, followed by
    any other keys in the order they appeared in the input mapping.
    ``sort_keys=False`` preserves that order.
    """

    try:
        import yaml
    except ImportError as e:  # pragma: no cover - pyyaml is a base dep
        raise ConstitutionMigrationError(
            "PyYAML is required to migrate constitution frontmatter"
        ) from e

    ordered: dict[str, Any] = {}
    for key in REQUIRED_FIELDS:
        if key in data:
            ordered[key] = data[key]
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value

    rendered = yaml.safe_dump(
        ordered,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    return f"---\n{rendered}---\n"


def _format_malformed_yaml_error(source: str) -> MalformedFrontmatterError:
    """Re-parse the frontmatter to extract a precise error message."""

    match = _FRONTMATTER_RE.match(source)
    if not match:
        # Unreachable when this is called on a file _parse_frontmatter
        # flagged as malformed, but return a generic error anyway.
        return MalformedFrontmatterError(
            "constitution.md frontmatter could not be parsed"
        )

    try:
        import yaml
    except ImportError:  # pragma: no cover
        return MalformedFrontmatterError(
            "PyYAML is required to diagnose frontmatter errors"
        )

    raw = match.group(1)
    try:
        yaml.safe_load(raw)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        if mark is not None:
            return MalformedFrontmatterError(
                f"constitution.md frontmatter has invalid YAML at "
                f"line {mark.line + 1}, column {mark.column + 1}: "
                f"{getattr(e, 'problem', 'parse error')}"
            )
        return MalformedFrontmatterError(
            f"constitution.md frontmatter has invalid YAML: {e}"
        )

    # Shouldn't get here (we reached this path because parsing failed or
    # produced a non-dict).
    return MalformedFrontmatterError(
        "constitution.md frontmatter is not a mapping"
    )


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


# ---------------------------------------------------------------------------
# Public API


def migrate_constitution(path: Path) -> MigrationResult:
    """Migrate ``.doit/memory/constitution.md`` in place.

    Behaviour matrix:

    - File does not exist → :attr:`MigrationAction.NO_OP`.
    - File has no frontmatter block → prepend a placeholder skeleton,
      preserve body byte-for-byte → :attr:`MigrationAction.PREPENDED`.
    - File has a frontmatter block missing required fields → patch in
      placeholders for the missing keys, preserve all existing keys and
      the body → :attr:`MigrationAction.PATCHED`.
    - File has a complete, well-formed frontmatter block → no write →
      :attr:`MigrationAction.NO_OP`.
    - File has a frontmatter block with malformed YAML → no write →
      :attr:`MigrationAction.ERROR` with a populated :attr:`error`.

    The function never raises. Callers inspect
    :attr:`MigrationResult.action` and :attr:`MigrationResult.error`.

    Args:
        path: Path to ``.doit/memory/constitution.md``.

    Returns:
        A :class:`MigrationResult` describing the outcome.
    """

    from ..utils.atomic_write import write_text_atomic

    path = Path(path)

    if not path.exists():
        return MigrationResult(path=path, action=MigrationAction.NO_OP)

    original = path.read_text(encoding="utf-8")
    parsed, body, has_block = _parse_frontmatter(original)

    if parsed is None:
        # Frontmatter block present but YAML is malformed.
        return MigrationResult(
            path=path,
            action=MigrationAction.ERROR,
            error=_format_malformed_yaml_error(original),
        )

    missing = tuple(k for k in REQUIRED_FIELDS if k not in parsed)

    if not missing:
        # File is already valid-shape. No write.
        return MigrationResult(
            path=path,
            action=MigrationAction.NO_OP,
            preserved_body_hash=_body_hash(body),
        )

    merged: dict[str, Any] = dict(parsed)
    for key in missing:
        merged[key] = PLACEHOLDER_REGISTRY[key]

    new_frontmatter = _format_frontmatter(merged)
    new_content = new_frontmatter + body

    try:
        write_text_atomic(path, new_content)
    except OSError as e:
        return MigrationResult(
            path=path,
            action=MigrationAction.ERROR,
            error=ConstitutionMigrationError(
                f"Could not write {path}: {e}"
            ),
        )

    return MigrationResult(
        path=path,
        action=(MigrationAction.PREPENDED if not has_block else MigrationAction.PATCHED),
        added_fields=missing,
        preserved_body_hash=_body_hash(body),
    )
