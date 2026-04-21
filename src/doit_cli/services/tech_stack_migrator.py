"""Migrate ``.doit/memory/tech-stack.md`` to the 0.4.0 memory-contract shape.

The memory validator requires an H2 ``## Tech Stack`` section containing
at least one H3 ``### <Group>`` subsection. This service inserts a
placeholder stub for Languages / Frameworks / Libraries when any of them
is missing, preserving all pre-existing prose byte-for-byte.

Sibling of :mod:`doit_cli.services.constitution_migrator` and
:mod:`doit_cli.services.roadmap_migrator`. Result types
(``MigrationAction``, ``MigrationResult``) are reused from the
constitution migrator.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Final

from ..errors import DoitError
from ..utils.atomic_write import write_text_atomic
from ._memory_shape import insert_section_if_missing
from .constitution_migrator import (
    ConstitutionMigrationError,
    MigrationAction,
    MigrationResult,
)

__all__ = (
    "REQUIRED_TECHSTACK_H2",
    "REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK",
    "migrate_tech_stack",
)


REQUIRED_TECHSTACK_H2: Final[tuple[str, ...]] = ("Tech Stack",)
"""H2 headings the memory contract requires in ``tech-stack.md``."""


REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK: Final[tuple[str, ...]] = (
    "Languages",
    "Frameworks",
    "Libraries",
)
"""H3 subsections required under ``## Tech Stack``.

The validator's baseline is "at least one H3 under Tech Stack"; we ensure
all three canonical groups are present so the enricher downstream has
predictable targets.
"""


_H2_LINE_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _tech_stack_stub_body(h3_title: str) -> str:
    """Default body inserted beneath each missing ``### <Group>`` heading."""

    return (
        f"<!-- Add [PROJECT_NAME]'s {h3_title} here.\n"
        f"     Populate from [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] context. -->\n"
    )


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def _has_h2(source: str, title: str) -> bool:
    target = title.strip().lower()
    return any(m.group(1).strip().lower() == target for m in _H2_LINE_RE.finditer(source))


def migrate_tech_stack(path: Path) -> MigrationResult:
    """Migrate ``.doit/memory/tech-stack.md`` in place.

    Same contract as :func:`roadmap_migrator.migrate_roadmap`.
    """

    path = Path(path)

    if not path.exists():
        return MigrationResult(path=path, action=MigrationAction.NO_OP)

    try:
        # Bypass universal-newline translation — see roadmap_migrator for rationale.
        original = path.read_bytes().decode("utf-8")
    except OSError as e:
        return MigrationResult(
            path=path,
            action=MigrationAction.ERROR,
            error=ConstitutionMigrationError(f"Could not read {path}: {e}"),
        )
    except UnicodeDecodeError as e:
        return MigrationResult(
            path=path,
            action=MigrationAction.ERROR,
            error=ConstitutionMigrationError(
                f"Could not decode {path} as UTF-8: {e}"
            ),
        )

    had_h2 = _has_h2(original, REQUIRED_TECHSTACK_H2[0])

    new_source, added = insert_section_if_missing(
        original,
        h2_title=REQUIRED_TECHSTACK_H2[0],
        h3_titles=REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK,
        stub_body=_tech_stack_stub_body,
    )

    if not added:
        return MigrationResult(
            path=path,
            action=MigrationAction.NO_OP,
            preserved_body_hash=_body_hash(original),
        )

    try:
        write_text_atomic(path, new_source)
    except OSError as e:
        return MigrationResult(
            path=path,
            action=MigrationAction.ERROR,
            error=ConstitutionMigrationError(f"Could not write {path}: {e}"),
        )

    action = MigrationAction.PATCHED if had_h2 else MigrationAction.PREPENDED
    return MigrationResult(
        path=path,
        action=action,
        added_fields=tuple(added),
        preserved_body_hash=_body_hash(original),
    )


# Keep DoitError in the import chain for pyright completeness.
_ = DoitError
