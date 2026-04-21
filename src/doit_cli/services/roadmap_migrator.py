"""Migrate ``.doit/memory/roadmap.md`` to the 0.4.0 memory-contract shape.

The memory validator requires an H2 ``## Active Requirements`` section
containing H3 priority subsections `### P1`, `### P2`, `### P3`, `### P4`.
Pre-0.4.0 roadmaps often lack this structure. This service detects the
gap and inserts a placeholder stub in place, preserving all pre-existing
prose byte-for-byte.

This is the sibling of :mod:`doit_cli.services.constitution_migrator`.
Result types (``MigrationAction``, ``MigrationResult``) are reused from
that module — no duplicate class definitions.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from ..errors import DoitError
from ..utils.atomic_write import write_text_atomic
from ._memory_shape import H3Matcher, insert_section_if_missing
from .constitution_migrator import (
    ConstitutionMigrationError,
    MigrationAction,
    MigrationResult,
)

__all__ = (
    "REQUIRED_ROADMAP_H2",
    "REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS",
    "migrate_roadmap",
)


REQUIRED_ROADMAP_H2: Final[tuple[str, ...]] = ("Active Requirements",)
"""H2 headings the memory contract requires in ``roadmap.md``."""


REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS: Final[tuple[str, ...]] = (
    "P1",
    "P2",
    "P3",
    "P4",
)
"""H3 priority subsections required under ``## Active Requirements``.

Matches the validator's expectation in
``memory_validator._validate_roadmap``: at least one ``### P[1-4]`` must
exist; we ensure all four are present so stubs render predictably.
"""


def _priority_matcher(required_title: str) -> H3Matcher:
    """Return a prefix-matching predicate for a priority H3 title.

    Mirrors ``memory_validator._validate_roadmap``'s ``^p[1-4]\\b`` regex
    semantics so the migrator treats any title the validator accepts
    (e.g. ``P1 - Critical (Must Have for MVP)``) as already present.
    The matcher is case-insensitive and word-boundary-anchored — it does
    NOT accept ``P10 - …`` as matching ``P1``.
    """

    token = required_title.strip().lower()
    pattern = re.compile(rf"^{re.escape(token)}\b", re.IGNORECASE)
    return lambda existing: bool(pattern.match(existing.strip()))


_PRIORITY_MATCHERS: Final[Mapping[str, H3Matcher]] = {
    p: _priority_matcher(p) for p in REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS
}
"""Per-priority prefix matchers passed to ``insert_section_if_missing``.

Keyed by canonical priority title (``P1``..``P4``); values honour the
same ``^p[1-4]\\b`` semantics the memory validator uses. See spec 061
``contracts/migrators.md`` for the full contract.
"""


def _roadmap_stub_body(h3_title: str) -> str:
    """Default body inserted beneath each missing ``### PN`` heading.

    Each stub carries three distinct placeholder tokens so the validator's
    ``_is_placeholder`` threshold (≥ 3 distinct ``[TOKEN]`` names) triggers
    even if the enricher later rewrites some of them.
    """

    return (
        f"<!-- Add [PROJECT_NAME]'s {h3_title} items here.\n"
        f"     See [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] for guidance. -->\n"
    )


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def migrate_roadmap(path: Path) -> MigrationResult:
    """Migrate ``.doit/memory/roadmap.md`` in place to the required shape.

    Behaviour matrix (matches :func:`constitution_migrator.migrate_constitution`):

    - File does not exist → :attr:`MigrationAction.NO_OP`.
    - Required H2 + every required H3 present → :attr:`MigrationAction.NO_OP`.
    - Required H2 missing → insert full H2 + H3 block at EOF →
      :attr:`MigrationAction.PREPENDED`.
    - H2 present, some H3s missing → insert only missing subsections →
      :attr:`MigrationAction.PATCHED`.
    - I/O error → :attr:`MigrationAction.ERROR` with populated
      :attr:`MigrationResult.error`.

    The function never raises. Callers inspect
    :attr:`MigrationResult.action` and :attr:`MigrationResult.error`.
    """

    path = Path(path)

    if not path.exists():
        return MigrationResult(path=path, action=MigrationAction.NO_OP)

    try:
        # Use read_bytes + decode to bypass Python's universal-newline
        # translation — otherwise CRLF sources would be silently
        # converted to LF on read, defeating the line-ending preservation
        # in _memory_shape.
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

    # Track whether the H2 existed before migration — this distinguishes
    # PREPENDED (full block appended) from PATCHED (subsections added to
    # an existing H2).
    had_h2 = _has_h2(original, REQUIRED_ROADMAP_H2[0])

    new_source, added = insert_section_if_missing(
        original,
        h2_title=REQUIRED_ROADMAP_H2[0],
        h3_titles=REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS,
        stub_body=_roadmap_stub_body,
        matchers=_PRIORITY_MATCHERS,
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


# ---------------------------------------------------------------------------
# Private helpers


def _has_h2(source: str, title: str) -> bool:
    pattern = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
    target = title.strip().lower()
    return any(m.group(1).strip().lower() == target for m in pattern.finditer(source))


# Silence pyright's unused-import guard for DoitError — it's part of the
# public re-export chain via constitution_migrator.MigrationResult.error.
_ = DoitError
