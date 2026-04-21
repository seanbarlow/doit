"""Linter-mode enricher for ``.doit/memory/personas.md``.

Unlike the constitution and tech-stack enrichers, this enricher is
**linter-only**: it detects remaining ``{placeholder}`` template tokens
and reports :attr:`EnrichmentAction.PARTIAL` with a sorted, deduplicated
``unresolved_fields`` list — but **never modifies the file**.

Why linter-only: persona content (names, roles, goals, pain points) is
intrinsically project-specific. An enricher has no upstream source to
infer "Developer Dana" vs "PM Pat" from. The user's remediation path is
interactive: ``/doit.roadmapit`` (project-level) or ``/doit.researchit``
(feature-level Q&A).

The placeholder regex matches template-style ``{Identifier}`` tokens
without swallowing JSON or shell-variable syntax. Examples of what it
flags:

- ``{Persona Name}``, ``{Role}``, ``{Archetype}``
- ``{FEATURE_NAME}``, ``{DATE}``, ``{BRANCH_NAME}``

Examples of what it ignores:

- ``${VAR}`` (shell variable syntax — preceded by ``$``)
- ``{}`` (empty braces)
- ``{"key": "value"}`` (JSON — non-identifier content)

Result types (``EnrichmentAction``, ``EnrichmentResult``) are reused
from :mod:`doit_cli.services.constitution_enricher`.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from ..errors import DoitError
from .constitution_enricher import EnrichmentAction, EnrichmentResult

__all__ = ("enrich_personas",)


_PLACEHOLDER_RE = re.compile(r"(?<!\$)\{([A-Za-z_][A-Za-z0-9_ .-]*)\}")
"""Curly-brace template tokens (e.g. ``{Persona Name}``, ``{FEATURE_NAME}``).

The ``(?<!\\$)`` lookbehind excludes shell-variable syntax like ``${VAR}``.
The identifier-like inner character class (``[A-Za-z_][A-Za-z0-9_ .-]*``)
avoids false positives from JSON objects or Python f-strings whose content
doesn't look like an identifier.
"""


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def enrich_personas(path: Path) -> EnrichmentResult:
    """Scan ``.doit/memory/personas.md`` for remaining template placeholders.

    Behaviour matrix (see spec 062 contracts/migrators.md §2):

    - File does not exist → :attr:`EnrichmentAction.NO_OP` (opt-in semantic).
    - File exists, zero ``{placeholder}`` tokens → :attr:`EnrichmentAction.NO_OP`.
    - File exists, ≥ 1 placeholder → :attr:`EnrichmentAction.PARTIAL` with
      the sorted, deduplicated set in ``unresolved_fields``.
    - I/O or UTF-8 decode error → :attr:`EnrichmentAction.ERROR`.

    Never returns :attr:`EnrichmentAction.ENRICHED` — this enricher is
    linter-only and never modifies the file on disk.
    """

    path = Path(path)

    if not path.exists():
        return EnrichmentResult(path=path, action=EnrichmentAction.NO_OP)

    try:
        # Bypass universal-newline translation to keep CRLF scans consistent
        # with the rest of the memory-file pipeline.
        original = path.read_bytes().decode("utf-8")
    except OSError as e:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.ERROR,
            error=DoitError(f"Could not read {path}: {e}"),
        )
    except UnicodeDecodeError as e:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.ERROR,
            error=DoitError(f"Could not decode {path} as UTF-8: {e}"),
        )

    tokens = sorted({match.group(1) for match in _PLACEHOLDER_RE.finditer(original)})

    if not tokens:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.NO_OP,
            preserved_body_hash=_body_hash(original),
        )

    return EnrichmentResult(
        path=path,
        action=EnrichmentAction.PARTIAL,
        unresolved_fields=tuple(tokens),
        preserved_body_hash=_body_hash(original),
    )
