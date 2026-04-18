"""Safe file copy: no-ops when source and target resolve to the same path.

Extracted from `TemplateManager._safe_copy` so other services can depend
on it without pulling the whole manager. Fixes the SameFileError
surfaced by #650 when `doit init --update` runs inside the doit repo.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def safe_copy(source_path: Path, target_path: Path) -> bool:
    """Copy `source_path` to `target_path` unless they resolve to the same file.

    Returns True if the copy actually happened, False if it was skipped
    because the two paths point at the same file on disk.
    """
    if source_path.resolve() == target_path.resolve():
        return False
    shutil.copy2(source_path, target_path)
    return True
