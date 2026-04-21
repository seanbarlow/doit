"""Unit tests for :mod:`doit_cli.services._memory_shape`."""

from __future__ import annotations

import hashlib

from doit_cli.services._memory_shape import insert_section_if_missing


def _stub(h3: str) -> str:
    return f"<!-- Add [PROJECT_NAME]'s {h3} here -->\n"


def _sha(text: str) -> bytes:
    return hashlib.sha256(text.encode("utf-8")).digest()


def test_appends_full_block_when_h2_missing() -> None:
    source = "# Title\n\n## Other Section\n\nPre-existing content.\n"
    new, added = insert_section_if_missing(
        source,
        h2_title="Active Requirements",
        h3_titles=("P1", "P2"),
        stub_body=_stub,
    )

    assert added == ["Active Requirements", "P1", "P2"]
    assert "## Active Requirements" in new
    assert "### P1" in new
    assert "### P2" in new
    # Original content survives byte-for-byte
    assert "## Other Section\n\nPre-existing content." in new


def test_noop_when_fully_complete() -> None:
    source = (
        "# Title\n\n## Tech Stack\n\n"
        "### Languages\nPython\n\n"
        "### Frameworks\nTyper\n\n"
        "### Libraries\nRich\n"
    )
    pre_hash = _sha(source)
    new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages", "Frameworks", "Libraries"),
        stub_body=_stub,
    )

    assert added == []
    assert new == source
    assert _sha(new) == pre_hash


def test_inserts_only_missing_h3s() -> None:
    source = (
        "# Title\n\n"
        "## Tech Stack\n\n"
        "### Languages\nPython\n"
    )
    new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages", "Frameworks", "Libraries"),
        stub_body=_stub,
    )

    assert added == ["Frameworks", "Libraries"]
    # Existing Languages untouched
    assert "### Languages\nPython" in new
    # Both missing sections added
    assert "### Frameworks" in new
    assert "### Libraries" in new
    # Still exactly one occurrence of each heading
    assert new.count("### Languages") == 1
    assert new.count("### Frameworks") == 1
    assert new.count("### Libraries") == 1


def test_preserves_existing_h3_ordering() -> None:
    source = (
        "# Title\n\n"
        "## Tech Stack\n\n"
        "### Libraries\nRich\n\n"
        "### Languages\nPython\n"
    )
    new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages", "Frameworks", "Libraries"),
        stub_body=_stub,
    )

    # Only Frameworks should have been added (Libraries + Languages are present,
    # albeit in reversed order)
    assert added == ["Frameworks"]
    # Existing ordering preserved: Libraries before Languages
    libraries_idx = new.index("### Libraries")
    languages_idx = new.index("### Languages")
    assert libraries_idx < languages_idx


def test_case_insensitive_h2_match() -> None:
    source = "# Title\n\n## tech stack\n\n### Languages\nPython\n"
    _new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages",),
        stub_body=_stub,
    )
    assert added == []  # H2 matched case-insensitively


def test_case_insensitive_h3_match() -> None:
    source = "# Title\n\n## Tech Stack\n\n### languages\nPython\n"
    _new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages",),
        stub_body=_stub,
    )
    assert added == []


def test_preserves_body_outside_target_section() -> None:
    """Bytes in unrelated sections must be preserved byte-for-byte."""

    preamble = "# Roadmap\n\n## Vision\n\nShip widgets.\n\n"
    trailing = "\n## Notes\n\n- legacy note\n"
    source = preamble + trailing
    new, added = insert_section_if_missing(
        source,
        h2_title="Active Requirements",
        h3_titles=("P1", "P2", "P3", "P4"),
        stub_body=_stub,
    )

    assert added == ["Active Requirements", "P1", "P2", "P3", "P4"]
    # Both unrelated sections survive byte-for-byte
    assert preamble in new
    assert trailing in new


def test_handles_source_without_trailing_newline() -> None:
    source = "# Title"  # no trailing newline
    new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages",),
        stub_body=_stub,
    )
    assert added == ["Tech Stack", "Languages"]
    assert new.startswith("# Title")
    assert "## Tech Stack" in new
    assert "### Languages" in new


def test_handles_empty_source() -> None:
    new, added = insert_section_if_missing(
        "",
        h2_title="Tech Stack",
        h3_titles=("Languages",),
        stub_body=_stub,
    )
    assert added == ["Tech Stack", "Languages"]
    assert new.startswith("## Tech Stack")


def test_inserted_stub_includes_placeholder_tokens() -> None:
    """The default stub emits [PROJECT_NAME] — required for validator
    detection."""

    source = "# Title\n"
    new, _ = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages", "Frameworks", "Libraries"),
        stub_body=_stub,
    )
    assert new.count("[PROJECT_NAME]") == 3


# ---------------------------------------------------------------------------
# Edge cases surfaced during review


def test_crlf_line_endings_are_preserved() -> None:
    """Sources with CRLF line endings must round-trip with CRLF preserved.

    Users on Windows and in cross-platform repos depend on this — a
    silent CRLF → LF conversion shows up as a spurious diff on every
    run.
    """

    source = "# Title\r\n\r\nSome prose.\r\n"
    new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages",),
        stub_body=_stub,
    )

    assert added == ["Tech Stack", "Languages"]
    assert "\r\n" in new, "CRLF line endings must be preserved"
    # Confirm there are no bare LFs (which would indicate mixed endings)
    bare_lf_count = new.count("\n") - new.count("\r\n")
    assert bare_lf_count == 0, (
        f"Mixed line endings in output — got {bare_lf_count} bare LFs"
    )
    # Original content preserved verbatim
    assert "# Title\r\n\r\nSome prose." in new


def test_duplicate_h2_headings_uses_first_match() -> None:
    """A source with two `## Tech Stack` headings (user error) should not
    cause the migrator to insert duplicate content or crash. We match
    the FIRST occurrence — consistent with memory_validator._has_heading.
    """

    source = (
        "# Title\n\n"
        "## Tech Stack\n\n"
        "### Languages\nPython\n\n"
        "## Tech Stack\n\n"  # duplicate, user error
        "### Frameworks\nTyper\n"
    )
    new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages", "Frameworks", "Libraries"),
        stub_body=_stub,
    )

    # First Tech Stack section has Languages; Libraries gets appended to
    # that section (the first match). Frameworks lives in the 2nd section,
    # which the migrator ignores — it only sees the 1st span. Libraries
    # may therefore still be missing per first-section scan. Expected
    # behaviour: only Libraries gets added to the first section;
    # Frameworks in the 2nd section is NOT counted since we scan only
    # the first span.
    assert "Libraries" in added
    # No new `## Tech Stack` heading was added; still exactly two.
    assert new.count("## Tech Stack") == 2


def test_whitespace_only_source() -> None:
    """A file containing only whitespace must produce a valid block at
    end-of-file, not a crash."""

    source = "   \n\n\t\n"
    new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages",),
        stub_body=_stub,
    )

    assert added == ["Tech Stack", "Languages"]
    assert "## Tech Stack" in new
    assert "### Languages" in new


def test_h2_line_with_extra_spaces() -> None:
    """Migrator matches H2 titles with trailing whitespace / extra spaces."""

    source = "# Title\n\n##   Tech Stack   \n\n### Languages\nPython\n"
    _new, added = insert_section_if_missing(
        source,
        h2_title="Tech Stack",
        h3_titles=("Languages",),
        stub_body=_stub,
    )
    # The extra-spaces H2 should still match; Languages already present → NO_OP
    assert added == []
