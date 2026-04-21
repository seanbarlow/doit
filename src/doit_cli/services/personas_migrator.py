"""Migrate ``.doit/memory/personas.md`` to the 0.4.0 memory-contract shape.

The memory validator requires two H2 sections in ``personas.md`` when the
file exists: ``## Persona Summary`` (the summary table of personas) and
``## Detailed Profiles`` (the per-persona ``### Persona: P-NNN`` blocks).

This migrator inserts stubs for whichever required H2 is missing, preserving
all pre-existing prose byte-for-byte. Unlike the constitution / roadmap /
tech-stack migrators, **this migrator is opt-in**: when
``.doit/memory/personas.md`` does not exist, it returns
:attr:`MigrationAction.NO_OP` without creating the file. Personas are a
methodology choice, not a project requirement.

Sibling of :mod:`doit_cli.services.constitution_migrator`,
:mod:`doit_cli.services.roadmap_migrator`, and
:mod:`doit_cli.services.tech_stack_migrator`. Result types
(``MigrationAction``, ``MigrationResult``) are reused from the constitution
migrator.
"""

from __future__ import annotations

import hashlib
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
    "REQUIRED_PERSONAS_H2",
    "migrate_personas",
)


REQUIRED_PERSONAS_H2: Final[tuple[str, ...]] = (
    "Persona Summary",
    "Detailed Profiles",
)
"""H2 headings the memory contract requires in ``.doit/memory/personas.md``.

Ordered for deterministic stub insertion. Sourced from
``src/doit_cli/templates/personas-output-template.md`` (the canonical
personas schema). No H3 subsections are required by shape — persona
entries are project-specific content, authored via ``/doit.roadmapit``
or ``/doit.researchit``.
"""


_PERSONA_SUMMARY_STUB = (
    "<!-- Add [PROJECT_NAME]'s personas table here.\n"
    "     Each row references a persona defined under ## Detailed Profiles.\n"
    "     Run /doit.roadmapit or /doit.researchit to populate interactively.\n"
    "     See [PERSONA_EXAMPLE] and [SEE_ROADMAPIT] for guidance. -->\n"
    "\n"
    "| ID | Name | Role | Archetype | Primary Goal |\n"
    "|----|------|------|-----------|--------------|\n"
)


_DETAILED_PROFILES_STUB = (
    "<!-- Add [PROJECT_NAME]'s persona detail blocks here.\n"
    "     Each block MUST use the heading `### Persona: P-NNN` where NNN is a\n"
    "     three-digit zero-padded ID matching a row in ## Persona Summary.\n"
    "     See [PERSONA_EXAMPLE] and [SEE_ROADMAPIT] for guidance. -->\n"
)


def _personas_stub_body(h2_title: str) -> str:
    """Body inserted beneath each missing required H2.

    Each stub carries ≥ 3 distinct ``[TOKEN]`` placeholders so the
    validator's ``_is_placeholder`` threshold classifies freshly-migrated
    files as needing enrichment.
    """

    if h2_title == "Persona Summary":
        return _PERSONA_SUMMARY_STUB
    if h2_title == "Detailed Profiles":
        return _DETAILED_PROFILES_STUB
    # Defensive default — should never be reached given REQUIRED_PERSONAS_H2.
    return (
        f"<!-- Add [PROJECT_NAME]'s {h2_title} section content here.\n"
        f"     See [PERSONA_EXAMPLE] and [SEE_ROADMAPIT] for guidance. -->\n"
    )


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def migrate_personas(path: Path) -> MigrationResult:
    """Migrate ``.doit/memory/personas.md`` in place to the required shape.

    Behaviour matrix:

    - File does not exist → :attr:`MigrationAction.NO_OP` (opt-in; no file created).
    - Both required H2s present → :attr:`MigrationAction.NO_OP` with byte-identical file.
    - One or both required H2s missing → :attr:`MigrationAction.PATCHED` with
      ``added_fields`` listing the inserted H2 titles in canonical order.
    - I/O or UTF-8 decode error → :attr:`MigrationAction.ERROR` with populated
      :attr:`MigrationResult.error`.

    Unlike the constitution / roadmap / tech-stack migrators, this function
    never returns :attr:`MigrationAction.PREPENDED` — the opt-in semantic
    means the file must exist before the migrator touches it.

    The function never raises. Callers inspect
    :attr:`MigrationResult.action` and :attr:`MigrationResult.error`.
    """

    path = Path(path)

    # Opt-in semantic: absent file is a valid NO_OP.
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

    # Two required H2s, no required H3s under either — call the shared helper
    # twice, threading the updated source through.
    working = original
    added: list[str] = []
    for h2_title in REQUIRED_PERSONAS_H2:
        working, added_this_pass = insert_section_if_missing(
            working,
            h2_title=h2_title,
            h3_titles=(),
            stub_body=_personas_stub_body,
        )
        added.extend(added_this_pass)

    if not added:
        return MigrationResult(
            path=path,
            action=MigrationAction.NO_OP,
            preserved_body_hash=_body_hash(original),
        )

    try:
        write_text_atomic(path, working)
    except OSError as e:
        return MigrationResult(
            path=path,
            action=MigrationAction.ERROR,
            error=ConstitutionMigrationError(f"Could not write {path}: {e}"),
        )

    return MigrationResult(
        path=path,
        action=MigrationAction.PATCHED,
        added_fields=tuple(added),
        preserved_body_hash=_body_hash(original),
    )


# Keep DoitError in the import chain for pyright completeness.
_ = DoitError
