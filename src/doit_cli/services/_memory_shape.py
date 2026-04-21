"""Section-insertion helper shared by the memory-file migrators.

Both :mod:`doit_cli.services.roadmap_migrator` and
:mod:`doit_cli.services.tech_stack_migrator` need the same primitive:
"inspect a markdown source for a required H2 section and its required
H3 subsections; when one is missing, insert a placeholder stub preserving
every other byte."

This helper does exactly that. It is intentionally private
(underscore-prefixed) — external callers should go through the
migrators, which add error handling, atomic writes, and validator
coordination.
"""

from __future__ import annotations

import re
from collections.abc import Callable

_H2_LINE_RE = re.compile(r"^(##)\s+(.+?)\s*$")
_H3_LINE_RE = re.compile(r"^(###)\s+(.+?)\s*$")


def _normalise(title: str) -> str:
    return title.strip().lower()


def _find_h2_span(lines: list[str], h2_title: str) -> tuple[int, int] | None:
    """Return (start, end) indices of the H2 block matching ``h2_title``.

    ``start`` is the index of the ``## <title>`` line; ``end`` is the
    index of the next H2 line (or ``len(lines)`` when the section runs
    to EOF). Returns ``None`` when no matching H2 exists.
    """

    target = _normalise(h2_title)
    start: int | None = None
    for i, line in enumerate(lines):
        m = _H2_LINE_RE.match(line)
        if not m:
            continue
        if start is None and _normalise(m.group(2)) == target:
            start = i
            continue
        if start is not None and i > start:
            return (start, i)
    if start is not None:
        return (start, len(lines))
    return None


def _h3_titles_in_section(lines: list[str], start: int, end: int) -> list[str]:
    """Return the list of `### <title>` headings between ``start`` and ``end``."""

    out: list[str] = []
    for i in range(start + 1, end):
        m = _H3_LINE_RE.match(lines[i])
        if m:
            out.append(m.group(2).strip())
    return out


def insert_section_if_missing(
    source: str,
    h2_title: str,
    h3_titles: tuple[str, ...],
    *,
    stub_body: Callable[[str], str],
) -> tuple[str, list[str]]:
    """Ensure ``source`` has ``## <h2_title>`` + every ``### <h3_title>``.

    Args:
        source: Full markdown source of the file.
        h2_title: Required H2 heading text (case-insensitive match).
        h3_titles: Required H3 heading titles in canonical schema order.
        stub_body: Callable returning the body content that should follow
            a freshly inserted ``### <h3_title>`` heading. Receives the
            H3 title; returns a string that must end with ``\\n\\n`` to
            separate it from following content.

    Returns:
        ``(new_source, added_titles)`` where ``added_titles`` contains
        the H2 and/or H3 titles that were newly inserted (empty list
        when the file was already complete).

    Behaviour:

    - **H2 absent**: appends the full H2 + every H3 block at end-of-file
      (with a single blank-line separator if the file doesn't end with
      a newline).
    - **H2 present, all H3s present**: returns the source unchanged and
      an empty ``added_titles`` list.
    - **H2 present, some H3s missing**: inserts only the missing H3
      subsections at the end of the existing H2 section, in
      ``h3_titles`` order, preserving existing H3 ordering.

    Matching is case-insensitive for both H2 and H3 titles (consistent
    with ``memory_validator._has_heading``). Existing subsection
    ordering is preserved; new H3s are appended after any pre-existing
    H3s in the section.
    """

    # Detect the source's dominant line ending so we can round-trip
    # through splitlines without silently converting CRLF → LF.
    newline = _detect_newline(source)

    lines = source.splitlines(keepends=False)
    span = _find_h2_span(lines, h2_title)
    added: list[str] = []

    if span is None:
        # H2 missing — append full block at EOF.
        added.append(h2_title)
        added.extend(h3_titles)

        block_lines: list[str] = ["", f"## {h2_title}", ""]
        for h3 in h3_titles:
            block_lines.append(f"### {h3}")
            block_lines.append("")
            body = stub_body(h3).rstrip("\n").rstrip("\r")
            if body:
                # Split on universal newlines so multi-line stubs don't embed
                # bare LFs when the surrounding file uses CRLF.
                block_lines.extend(body.splitlines())
                block_lines.append("")

        # Ensure a single blank line between prior content and the new block.
        if source and not source.endswith(("\n", "\r\n", "\r")):
            joined = source + newline + newline.join(block_lines[1:]) + newline
        elif source:
            joined = source + newline.join(block_lines[1:]) + newline
        else:
            joined = newline.join(block_lines[1:]) + newline
        return joined, added

    # H2 present — check H3s.
    start, end = span
    existing = {_normalise(t) for t in _h3_titles_in_section(lines, start, end)}
    missing = [h3 for h3 in h3_titles if _normalise(h3) not in existing]
    if not missing:
        return source, []

    # Build insertion block for the missing H3s, in canonical order.
    insertion: list[str] = []
    for h3 in missing:
        insertion.append(f"### {h3}")
        insertion.append("")
        body = stub_body(h3).rstrip("\n").rstrip("\r")
        if body:
            # Split on universal newlines to avoid embedding bare LFs
            # inside a CRLF file.
            insertion.extend(body.splitlines())
            insertion.append("")
        added.append(h3)

    # Find the logical insertion point: end of the H2 section, dropping
    # any trailing blank lines so we produce clean spacing.
    insert_at = end
    while insert_at > start + 1 and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    # One blank line separator before the new H3s, then the insertion.
    new_lines = [*lines[:insert_at], "", *insertion, *lines[insert_at:]]

    # Preserve the original trailing-newline behaviour.
    trailing_newline = source.endswith(("\n", "\r\n", "\r"))
    result = newline.join(new_lines)
    if trailing_newline and not result.endswith(newline):
        result += newline
    return result, added


def _detect_newline(source: str) -> str:
    """Return the dominant line-ending in ``source``.

    Inspects the first line terminator found. Defaults to ``"\\n"`` for
    empty input or sources without any terminator. Ensures migrated
    files preserve CRLF when the source was CRLF (Windows, mixed repos).
    """

    # Look for the first newline character(s) to decide.
    for i, ch in enumerate(source):
        if ch == "\r":
            if i + 1 < len(source) and source[i + 1] == "\n":
                return "\r\n"
            return "\r"
        if ch == "\n":
            return "\n"
    return "\n"
