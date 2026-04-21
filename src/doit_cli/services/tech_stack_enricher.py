"""Deterministic enrichment of placeholder-stubbed tech-stack.md.

Reads `.doit/memory/constitution.md` and extracts bullet content from
any ``## Tech Stack`` (with `### Languages/Frameworks/Libraries` children),
``## Infrastructure``, and ``## Deployment`` sections. Writes the same
bullet lists into the corresponding subsections of ``tech-stack.md``,
replacing placeholder stubs but preserving any non-placeholder
user-authored subsection content.

Reuses ``EnrichmentAction`` / ``EnrichmentResult`` types from spec 059's
:mod:`doit_cli.services.constitution_enricher`.

**PARTIAL state is intentional, not a bug.** When the constitution has
Languages content but no Frameworks content, the enricher fills
Languages and leaves Frameworks as a placeholder. The result is
reported as ``EnrichmentAction.PARTIAL`` with ``unresolved_fields =
("Frameworks",)``. On the next run the enricher only acts on fields
that are still placeholders, so the already-populated Languages
subsection is preserved verbatim. Rolling back partial successes would
force the user to re-do deterministic work they don't control — better
to keep what we have and surface what remains.

The write is still atomic at the file level: we mutate an in-memory
``working`` copy, then call ``write_text_atomic`` exactly once. If any
step before that write raises, the file on disk is unchanged.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from ..errors import DoitError
from ..utils.atomic_write import write_text_atomic
from ._memory_shape import insert_section_if_missing
from .constitution_enricher import EnrichmentAction, EnrichmentResult
from .tech_stack_migrator import REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK

__all__ = ("enrich_tech_stack",)


# Sources in constitution.md to extract bullets from.
# Maps (constitution H2, expected target H3) — when the constitution's
# H2 has `### Languages/Frameworks/Libraries` children, those fill
# the same-named subsections in tech-stack.md. Top-level `## Infrastructure`
# and `## Deployment` sections map to synonymous `### Infrastructure`
# and `### Deployment` subsections under the tech-stack `## Tech Stack`.
_CONSTITUTION_SOURCES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Tech Stack", REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK),
    ("Infrastructure", ("Infrastructure",)),
    ("Deployment", ("Deployment",)),
)

# Placeholder-stub detector: subsection body equals the stub the
# tech_stack_migrator inserts, OR contains any [PROJECT_NAME] token.
_STUB_TOKEN_RE = re.compile(r"\[PROJECT_[A-Z_]+\]")

_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def _extract_h2_section(source: str, h2_title: str) -> str | None:
    """Return the body (everything between this H2 and the next H2), or None."""

    target = h2_title.strip().lower()
    matches = list(_H2_RE.finditer(source))
    for i, m in enumerate(matches):
        if m.group(1).strip().lower() == target:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(source)
            return source[start:end]
    return None


def _extract_h3_body(section_body: str, h3_title: str) -> str | None:
    """From a H2 section body, extract the body of the named H3 (or None)."""

    target = h3_title.strip().lower()
    matches = list(_H3_RE.finditer(section_body))
    for i, m in enumerate(matches):
        if m.group(1).strip().lower() == target:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(section_body)
            return section_body[start:end].strip()
    return None


def _bullet_lines(body: str) -> list[str]:
    """Return the leading bullet-list lines from ``body`` (up to the first
    non-bullet/blank block)."""

    lines = body.splitlines()
    out: list[str] = []
    started = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            out.append(line)
            started = True
        elif stripped == "":
            if started:
                # Allow one blank line between bullets, otherwise stop.
                out.append(line)
            # before the list starts, just skip
        else:
            if started:
                break
    # Trim trailing blank lines
    while out and out[-1].strip() == "":
        out.pop()
    return out


def _extract_bullets_for_target(
    constitution_source: str, constitution_h2: str, target_h3: str
) -> list[str] | None:
    """Get the bullets to place under ``target_h3`` in tech-stack.md.

    For ``## Tech Stack`` source, look inside for a matching ``### <target_h3>``
    subsection's bullets. For ``## Infrastructure`` / ``## Deployment``
    sources, the whole H2 section's bullets flow to the synonymous H3.

    Returns ``None`` when no source content is found.
    """

    section_body = _extract_h2_section(constitution_source, constitution_h2)
    if section_body is None:
        return None

    # When target H3 matches the constitution H2 name (Infrastructure,
    # Deployment), use the H2 body directly.
    if constitution_h2.lower() == target_h3.lower():
        bullets = _bullet_lines(section_body)
        return bullets if bullets else None

    # Otherwise look inside Tech Stack for the matching H3.
    h3_body = _extract_h3_body(section_body, target_h3)
    if h3_body is None:
        return None
    bullets = _bullet_lines(h3_body)
    return bullets if bullets else None


def _find_h3_span(source: str, h2_title: str, h3_title: str) -> tuple[int, int] | None:
    """Return the (start, end) char offsets of the body of an H3 under an H2.

    ``start`` points at the first character after the H3 line's newline;
    ``end`` points at the start of the next H3 / H2 line (or end-of-file).
    """

    h2_target = h2_title.strip().lower()
    h3_target = h3_title.strip().lower()
    # First locate the H2
    h2_matches = list(_H2_RE.finditer(source))
    h2_start_idx = None
    h2_end_idx = None
    for i, m in enumerate(h2_matches):
        if m.group(1).strip().lower() == h2_target:
            h2_start_idx = m.end()
            h2_end_idx = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(source)
            break
    if h2_start_idx is None or h2_end_idx is None:
        return None

    # Now scan H3s within this H2 span
    section = source[h2_start_idx:h2_end_idx]
    h3_matches = list(_H3_RE.finditer(section))
    for i, m in enumerate(h3_matches):
        if m.group(1).strip().lower() == h3_target:
            # body starts on the line AFTER the H3 line
            start_rel = m.end()
            end_rel = (
                h3_matches[i + 1].start()
                if i + 1 < len(h3_matches)
                else len(section)
            )
            # Skip the newline immediately after the H3 line
            if start_rel < len(section) and section[start_rel] == "\n":
                start_rel += 1
            return (h2_start_idx + start_rel, h2_start_idx + end_rel)
    return None


def _is_placeholder_h3(source: str, h2_title: str, h3_title: str) -> bool:
    span = _find_h3_span(source, h2_title, h3_title)
    if span is None:
        # H3 doesn't exist → treat as placeholder-equivalent so the
        # enricher can create it.
        return True
    body = source[span[0]:span[1]]
    return bool(_STUB_TOKEN_RE.search(body))


def _replace_h3_body(
    source: str, h2_title: str, h3_title: str, new_body: str
) -> str:
    """Replace the body of H3 under H2 with ``new_body``.

    ``new_body`` should not include the heading line itself; it should
    end with a single blank-line separator. Ensures byte-identical output
    outside the replaced span.
    """

    span = _find_h3_span(source, h2_title, h3_title)
    if span is None:
        return source  # caller must insert the H3 first
    start, end = span
    # Normalise trailing whitespace on the new body
    body = new_body.rstrip("\n") + "\n\n"
    return source[:start] + body + source[end:]


def _ensure_h3_exists(
    source: str, h2_title: str, h3_title: str, stub: str = ""
) -> str:
    """Insert an H3 under an H2 if it doesn't already exist."""

    if _find_h3_span(source, h2_title, h3_title) is not None:
        return source

    def _stub_body(title: str) -> str:
        return stub or ""

    new, _added = insert_section_if_missing(
        source,
        h2_title=h2_title,
        h3_titles=(h3_title,),
        stub_body=_stub_body,
    )
    return new


def enrich_tech_stack(
    path: Path, *, project_root: Path | None = None
) -> EnrichmentResult:
    """Populate placeholder-stubbed subsections of ``tech-stack.md`` from
    the constitution.

    See module docstring for behavioural details.
    """

    path = Path(path)

    if not path.exists():
        return EnrichmentResult(path=path, action=EnrichmentAction.NO_OP)

    if project_root is None:
        try:
            project_root = path.resolve().parents[2]
        except IndexError:  # pragma: no cover - path too shallow
            return EnrichmentResult(
                path=path,
                action=EnrichmentAction.ERROR,
                error=DoitError("Could not locate project root for enrichment"),
            )

    try:
        # Bypass universal-newline translation to preserve CRLF round-trip.
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

    constitution_path = project_root / ".doit" / "memory" / "constitution.md"
    if constitution_path.exists():
        try:
            constitution_source = constitution_path.read_text(encoding="utf-8")
        except OSError:
            constitution_source = ""
    else:
        constitution_source = ""

    # Canonical targets (Languages/Frameworks/Libraries) drive the
    # decision: if at least one is a placeholder, we enter enrichment
    # mode; otherwise NO_OP. Infrastructure / Deployment are
    # "opportunistic" extras — only added when canonical enrichment is
    # happening anyway (keeps NO_OP semantics clean for users whose
    # canonical sections are complete).
    canonical_targets = [("Tech Stack", h3) for h3 in REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK]
    opportunistic_targets = [
        (const_h2, h3)
        for const_h2, h3_titles in _CONSTITUTION_SOURCES
        for h3 in h3_titles
        if const_h2 != "Tech Stack"
    ]

    working = original
    enriched: list[str] = []
    unresolved: list[str] = []

    any_canonical_placeholder = any(
        _is_placeholder_h3(working, "Tech Stack", h3) for _, h3 in canonical_targets
    )
    if not any_canonical_placeholder:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.NO_OP,
            preserved_body_hash=_body_hash(original),
        )

    # Enrich canonical subsections.
    for const_h2, h3 in canonical_targets:
        is_placeholder = _is_placeholder_h3(working, "Tech Stack", h3)
        if not is_placeholder:
            continue
        bullets = _extract_bullets_for_target(constitution_source, const_h2, h3)
        if bullets is None:
            unresolved.append(h3)
            continue
        new_body = "\n".join(bullets)
        working = _replace_h3_body(working, "Tech Stack", h3, new_body)
        enriched.append(h3)

    # Opportunistic: add Infrastructure/Deployment only if the
    # constitution has that content (otherwise silently skip — these
    # subsections aren't required by the memory contract).
    for const_h2, h3 in opportunistic_targets:
        bullets = _extract_bullets_for_target(constitution_source, const_h2, h3)
        if bullets is None:
            continue
        working = _ensure_h3_exists(working, "Tech Stack", h3)
        new_body = "\n".join(bullets)
        working = _replace_h3_body(working, "Tech Stack", h3, new_body)
        enriched.append(h3)

    if not enriched:
        # All targets either pre-filled or unresolvable.
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.PARTIAL if unresolved else EnrichmentAction.NO_OP,
            unresolved_fields=tuple(unresolved),
            preserved_body_hash=_body_hash(original),
        )

    try:
        write_text_atomic(path, working)
    except OSError as e:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.ERROR,
            error=DoitError(f"Could not write {path}: {e}"),
        )

    action = (
        EnrichmentAction.PARTIAL if unresolved else EnrichmentAction.ENRICHED
    )
    return EnrichmentResult(
        path=path,
        action=action,
        enriched_fields=tuple(enriched),
        unresolved_fields=tuple(unresolved),
        preserved_body_hash=_body_hash(original),
    )
