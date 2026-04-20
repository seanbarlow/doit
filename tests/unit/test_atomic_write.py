"""Unit tests for :mod:`doit_cli.utils.atomic_write`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from doit_cli.utils.atomic_write import write_text_atomic


def test_creates_file_with_content(tmp_path: Path) -> None:
    target = tmp_path / "new.txt"
    write_text_atomic(target, "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"


def test_replaces_existing_file_atomically(tmp_path: Path) -> None:
    target = tmp_path / "existing.txt"
    target.write_text("old contents", encoding="utf-8")

    write_text_atomic(target, "new contents")

    assert target.read_text(encoding="utf-8") == "new contents"


def test_write_failure_leaves_original_intact(tmp_path: Path) -> None:
    """If the temp write fails, the original file is byte-identical."""

    target = tmp_path / "preserved.txt"
    original_bytes = b"original\ncontents\n"
    target.write_bytes(original_bytes)

    with patch(
        "doit_cli.utils.atomic_write.os.replace",
        side_effect=OSError("simulated replace failure"),
    ):
        with pytest.raises(OSError, match="simulated replace failure"):
            write_text_atomic(target, "this should never land")

    assert target.read_bytes() == original_bytes


def test_temp_file_is_cleaned_up_on_failure(tmp_path: Path) -> None:
    """A failed write leaves no ``.tmp`` sibling behind."""

    target = tmp_path / "clean.txt"
    target.write_text("original", encoding="utf-8")

    with patch(
        "doit_cli.utils.atomic_write.os.replace",
        side_effect=OSError("fail"),
    ):
        with pytest.raises(OSError):
            write_text_atomic(target, "replacement")

    leftover = [p for p in tmp_path.iterdir() if p.name != "clean.txt"]
    assert leftover == [], f"Unexpected leftover files: {leftover}"


def test_utf8_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "unicode.txt"
    content = "café — résumé — 日本語\n"
    write_text_atomic(target, content)
    assert target.read_text(encoding="utf-8") == content


def test_preserves_exact_bytes_without_line_ending_rewriting(
    tmp_path: Path,
) -> None:
    """The writer must not transform ``\\n`` to ``\\r\\n`` or strip trailing
    newlines — the migrator depends on byte-for-byte body preservation."""

    target = tmp_path / "bytes.txt"
    content = "line1\nline2\nline3"  # no trailing newline
    write_text_atomic(target, content)

    # Read as bytes so we see any line-ending translation.
    assert target.read_bytes() == content.encode("utf-8")
