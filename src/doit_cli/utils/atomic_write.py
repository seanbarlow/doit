"""Atomic file-write helper.

Writes content to a path in a way that guarantees the original file on
disk is either fully replaced with the new content or left byte-identical
— never partially written. Used by migration code paths where a
mid-write crash must not corrupt user data.

The implementation writes to a sibling temp file in the same directory
(so ``os.replace`` is atomic on both POSIX and Windows), fsyncs the temp
file, and then atomically replaces the target.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def write_text_atomic(
    path: Path, content: str, *, encoding: str = "utf-8"
) -> None:
    """Write ``content`` to ``path`` atomically.

    Args:
        path: Destination file. Parent directory must already exist.
        content: Text to write.
        encoding: Text encoding for the write (default UTF-8).

    Raises:
        OSError: On any filesystem-level failure (permissions, disk full,
            parent dir missing). When this raises, the file at ``path``
            is byte-identical to its state before the call.
    """

    path = Path(path)
    directory = path.parent

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=directory
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except OSError:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise
