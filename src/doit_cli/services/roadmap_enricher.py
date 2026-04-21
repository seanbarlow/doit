"""Deterministic enrichment of placeholder roadmap.md.

The enricher does exactly two narrow things:

1. Replaces a placeholder ``## Vision`` paragraph with the first sentence
   of ``.doit/memory/constitution.md``'s ``### Project Purpose`` section.
2. Inserts an HTML-comment block near the top of
   ``## Active Requirements`` listing every row from
   ``.doit/memory/completed_roadmap.md``'s "Recently Completed" table,
   so users can see what has shipped without re-adding it to the roadmap.

Priority subsections (P1/P2/P3/P4) are **not** auto-populated — that
requires product judgment that belongs in the ``/doit.roadmapit`` skill.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from ..errors import DoitError
from ..utils.atomic_write import write_text_atomic
from .constitution_enricher import EnrichmentAction, EnrichmentResult

__all__ = ("enrich_roadmap",)


_STUB_TOKEN_RE = re.compile(r"\[PROJECT_[A-Z_]+\]")
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)

# Marker used to identify our inserted completed-items comment block so
# re-runs don't duplicate it.
_COMPLETED_BLOCK_START = "<!-- [060] completed-items-hint START"
_COMPLETED_BLOCK_END = "<!-- [060] completed-items-hint END -->"


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def _find_h2_span(source: str, h2_title: str) -> tuple[int, int] | None:
    target = h2_title.strip().lower()
    matches = list(_H2_RE.finditer(source))
    for i, m in enumerate(matches):
        if m.group(1).strip().lower() == target:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(source)
            return (start, end)
    return None


def _find_h3_body_in_section(section: str, h3_title: str) -> str | None:
    target = h3_title.strip().lower()
    matches = list(_H3_RE.finditer(section))
    for i, m in enumerate(matches):
        if m.group(1).strip().lower() == target:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(section)
            return section[start:end].strip()
    return None


_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_MARKDOWN_INLINE_RE = re.compile(r"[`*_]")


def _strip_inline_markdown(text: str) -> str:
    """Remove markdown link/emphasis markers.

    Truncating a markdown-rich sentence can leave dangling link/code
    fences that break rendering. Strip the markers — Vision is plain
    prose anyway.
    """

    # Replace `[label](url)` → `label`, then drop remaining *, _, ` chars.
    text = _MARKDOWN_LINK_RE.sub(r"\1", text)
    text = _MARKDOWN_INLINE_RE.sub("", text)
    return text


def _infer_vision(constitution_source: str) -> str | None:
    """First sentence of constitution's `### Project Purpose` section."""

    ts = _find_h2_span(constitution_source, "Purpose & Goals")
    if ts is None:
        return None
    section = constitution_source[ts[0]:ts[1]]
    purpose_body = _find_h3_body_in_section(section, "Project Purpose")
    if not purpose_body:
        return None

    # Take the first non-empty paragraph, then the first sentence.
    paragraph = next(
        (p.strip() for p in re.split(r"\n\s*\n", purpose_body, maxsplit=1) if p.strip()),
        "",
    )
    if not paragraph:
        return None
    # Strip inline markdown before sentence extraction so truncation
    # can't leave dangling `]` or `` ` `` markers.
    paragraph = _strip_inline_markdown(paragraph)
    match = re.search(r".+?[.!?](?=\s|$)", paragraph, re.DOTALL)
    sentence = match.group(0) if match else paragraph
    sentence = re.sub(r"\s+", " ", sentence).strip()
    if len(sentence) > 140:
        sentence = sentence[:139].rstrip() + "…"
    return sentence or None


_ESCAPED_PIPE_SENTINEL = "\x00ESCAPED_PIPE\x00"


def _split_gfm_row(row: str) -> list[str]:
    """Split a GFM table row on unescaped ``|`` characters.

    ``\\|`` inside a cell is preserved as a literal ``|`` in the output.
    Leading/trailing empty cells from outer pipes are discarded.
    """

    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    # Preserve escaped pipes through the split, then restore.
    tokens = row.replace("\\|", _ESCAPED_PIPE_SENTINEL).split("|")
    return [c.replace(_ESCAPED_PIPE_SENTINEL, "|").strip() for c in tokens]


def _parse_completed_items(completed_source: str) -> list[str]:
    """Extract the Item column from the 'Recently Completed' GFM table.

    Handles GFM escape syntax — a cell containing ``API \\| REST layer`` is
    preserved verbatim (without the backslash) in the output. Rows that
    are empty or that only contain divider chars are skipped.
    """

    m = re.search(
        r"^##\s+Recently Completed\s*$",
        completed_source,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if not m:
        return []
    rest = completed_source[m.end():]
    # Stop at next H2
    next_h2 = _H2_RE.search(rest)
    section = rest[: next_h2.start()] if next_h2 else rest

    rows = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return []

    items: list[str] = []
    # Skip header + divider
    for row in rows[2:]:
        cells = _split_gfm_row(row)
        if not cells or not cells[0]:
            continue
        # Skip "---" / ":---:" divider-looking cells
        first = cells[0]
        if set(first.replace(":", "").replace("-", "")) == set():
            continue
        items.append(first)
    return items


def _has_vision_placeholder(source: str) -> bool:
    vs = _find_h2_span(source, "Vision")
    if vs is None:
        return False
    section = source[vs[0]:vs[1]]
    return bool(_STUB_TOKEN_RE.search(section))


def _replace_vision_body(source: str, new_sentence: str) -> str:
    """Replace the body of `## Vision` with ``new_sentence`` paragraph."""

    vs = _find_h2_span(source, "Vision")
    if vs is None:
        return source
    start, end = vs
    # Preserve a trailing blank line before the next H2
    body = f"\n{new_sentence}\n\n"
    return source[:start] + body + source[end:]


def _insert_completed_block(source: str, completed_items: list[str]) -> str:
    """Insert (or replace) the completed-items hint block near the top of
    ``## Active Requirements``."""

    if not completed_items:
        return source

    ar = _find_h2_span(source, "Active Requirements")
    if ar is None:
        return source

    # Build the block.
    block_lines = [_COMPLETED_BLOCK_START + " -->"]
    block_lines.append("<!-- Completed items from .doit/memory/completed_roadmap.md.")
    block_lines.append("     Do not re-add unless there's a new change in scope. -->")
    block_lines.append("<!--")
    for item in completed_items:
        block_lines.append(f"  - [DONE] {item}")
    block_lines.append("-->")
    block_lines.append(_COMPLETED_BLOCK_END)
    block = "\n".join(block_lines) + "\n\n"

    ar_start, ar_end = ar
    section = source[ar_start:ar_end]

    # If an existing block is present, replace it in place.
    existing_start = section.find(_COMPLETED_BLOCK_START)
    if existing_start != -1:
        existing_end = section.find(_COMPLETED_BLOCK_END, existing_start)
        if existing_end != -1:
            existing_end += len(_COMPLETED_BLOCK_END)
            # Extend to swallow a trailing single newline so spacing stays clean.
            if existing_end < len(section) and section[existing_end] == "\n":
                existing_end += 1
            new_section = (
                section[:existing_start]
                + block
                + section[existing_end:].lstrip("\n")
            )
            return source[:ar_start] + new_section + source[ar_end:]

    # Insert at the top of the H2 body (after the heading's newline).
    # The H2 span starts right after the heading line, so section begins
    # with a leading newline.
    leading_newlines = 0
    while leading_newlines < len(section) and section[leading_newlines] == "\n":
        leading_newlines += 1
    # Preserve the original leading newline after the H2 line (one blank line).
    prefix = "\n" + block
    new_section = prefix + section[leading_newlines:]
    return source[:ar_start] + new_section + source[ar_end:]


def enrich_roadmap(
    path: Path, *, project_root: Path | None = None
) -> EnrichmentResult:
    """Enrich a placeholder-stubbed roadmap.md.

    See module docstring for behaviour.
    """

    path = Path(path)

    if not path.exists():
        return EnrichmentResult(path=path, action=EnrichmentAction.NO_OP)

    if project_root is None:
        try:
            project_root = path.resolve().parents[2]
        except IndexError:  # pragma: no cover
            return EnrichmentResult(
                path=path,
                action=EnrichmentAction.ERROR,
                error=DoitError("Could not locate project root for enrichment"),
            )

    try:
        # read_bytes + decode bypasses Python's universal-newline
        # translation (which would convert CRLF → LF on read).
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
    completed_path = project_root / ".doit" / "memory" / "completed_roadmap.md"

    constitution_source = (
        constitution_path.read_text(encoding="utf-8")
        if constitution_path.exists()
        else ""
    )
    completed_source = (
        completed_path.read_text(encoding="utf-8") if completed_path.exists() else ""
    )

    enriched: list[str] = []
    unresolved: list[str] = []
    working = original

    # --- Vision -----------------------------------------------------------
    if _has_vision_placeholder(working):
        sentence = _infer_vision(constitution_source)
        if sentence:
            working = _replace_vision_body(working, sentence)
            enriched.append("Vision")
        else:
            unresolved.append("Vision")
    # If no placeholder, leave Vision alone (user has real content).

    # --- Completed-items hint --------------------------------------------
    items = _parse_completed_items(completed_source)
    if items:
        new_working = _insert_completed_block(working, items)
        if new_working != working:
            working = new_working
            enriched.append("completed_items_hint")

    if not enriched and not unresolved:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.NO_OP,
            preserved_body_hash=_body_hash(original),
        )

    if not enriched:
        # Nothing was written but we did detect placeholders — report PARTIAL.
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.PARTIAL,
            unresolved_fields=tuple(unresolved),
            preserved_body_hash=_body_hash(original),
        )

    if working == original:
        # Defensive: no byte change despite thinking we enriched.
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.NO_OP,
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
