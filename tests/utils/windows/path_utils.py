"""Windows path handling utilities for testing."""
import sys
from pathlib import Path, PurePosixPath
from typing import Optional


class WindowsPathInfo:
    """Information about a Windows path analysis."""

    def __init__(
        self,
        original_path: str,
        normalized_path: str,
        is_absolute: bool,
        drive_letter: Optional[str],
        is_unc: bool,
        length: int,
        exceeds_max_path: bool,
        contains_reserved_name: bool,
        reserved_name: Optional[str],
    ):
        self.original_path = original_path
        self.normalized_path = normalized_path
        self.is_absolute = is_absolute
        self.drive_letter = drive_letter
        self.is_unc = is_unc
        self.length = length
        self.exceeds_max_path = exceeds_max_path
        self.contains_reserved_name = contains_reserved_name
        self.reserved_name = reserved_name


class WindowsPathValidator:
    """Validator for Windows path characteristics and constraints."""

    RESERVED_NAMES = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    MAX_PATH_LENGTH = 260

    def analyze_path(self, path: str | Path) -> WindowsPathInfo:
        """
        Analyze a path for Windows-specific characteristics.

        Args:
            path: Path to analyze

        Returns:
            WindowsPathInfo with analysis results
        """
        path_str = str(path)
        path_obj = Path(path_str)

        # Normalize to forward slashes
        normalized = str(PurePosixPath(path_obj))

        # Check if absolute
        is_absolute = path_obj.is_absolute()

        # Extract drive letter (Windows-specific)
        drive_letter = None
        if is_absolute and len(path_str) >= 2 and path_str[1] == ":":
            drive_letter = path_str[0].upper()

        # Check for UNC path (\\server\share)
        is_unc = path_str.startswith("\\\\") or path_str.startswith("//")

        # Path length
        length = len(path_str)
        exceeds_max_path = length > self.MAX_PATH_LENGTH

        # Check for reserved names
        reserved_name = None
        contains_reserved = False
        for part in path_obj.parts:
            # Extract filename without extension
            name_without_ext = part.split(".")[0].upper()
            if name_without_ext in self.RESERVED_NAMES:
                contains_reserved = True
                reserved_name = name_without_ext
                break

        return WindowsPathInfo(
            original_path=path_str,
            normalized_path=normalized,
            is_absolute=is_absolute,
            drive_letter=drive_letter,
            is_unc=is_unc,
            length=length,
            exceeds_max_path=exceeds_max_path,
            contains_reserved_name=contains_reserved,
            reserved_name=reserved_name,
        )

    def is_reserved_name(self, filename: str) -> bool:
        """
        Check if filename is a Windows reserved name.

        Args:
            filename: Name to check (with or without extension)

        Returns:
            True if reserved, False otherwise
        """
        if sys.platform != "win32":
            return False

        # Extract name without extension
        name_without_ext = filename.split(".")[0].upper()
        return name_without_ext in self.RESERVED_NAMES

    def exceeds_max_path(self, path: str | Path) -> bool:
        """
        Check if path exceeds Windows MAX_PATH limitation.

        Args:
            path: Path to check

        Returns:
            True if path length > 260 characters
        """
        return len(str(path)) > self.MAX_PATH_LENGTH


def normalize_path_for_comparison(path_str: str) -> str:
    """
    Convert any path to forward-slash format for comparison.

    Args:
        path_str: Path string to normalize

    Returns:
        Normalized path with forward slashes
    """
    return str(PurePosixPath(Path(path_str)))
