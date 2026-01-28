"""Filesystem validation utilities for macOS testing.

Provides tools to detect and validate macOS-specific filesystem features:
- Volume type detection (APFS, HFS+, etc.)
- Case-sensitivity detection
- APFS feature checking
"""

import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional


class FilesystemValidator:
    """Validates macOS-specific filesystem characteristics."""

    @staticmethod
    def detect_volume_type(path: str = ".") -> Optional[str]:
        """Detect the filesystem type for the given path.

        Args:
            path: Path to check (defaults to current directory)

        Returns:
            Filesystem type string (e.g., "apfs", "hfs", "exfat") or None if unable to detect
        """
        if platform.system() != "Darwin":
            return None

        try:
            # Use diskutil to get filesystem info
            abs_path = os.path.abspath(path)
            result = subprocess.run(
                ["diskutil", "info", abs_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "File System Personality:" in line or "Type (Bundle):" in line:
                        fs_type = line.split(":")[-1].strip().lower()
                        if "apfs" in fs_type:
                            return "apfs"
                        elif "hfs" in fs_type or "mac os extended" in fs_type:
                            return "hfs"
                        elif "exfat" in fs_type:
                            return "exfat"
                        elif "msdos" in fs_type or "fat" in fs_type:
                            return "fat"
                        return fs_type

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass

        return None

    @staticmethod
    def is_case_sensitive(path: str = ".") -> bool:
        """Check if the filesystem at the given path is case-sensitive.

        Args:
            path: Path to check (defaults to current directory)

        Returns:
            True if case-sensitive, False otherwise
        """
        if platform.system() != "Darwin":
            # Assume case-sensitive on non-macOS for testing purposes
            return True

        try:
            # Create a temporary directory in the target path
            test_dir = tempfile.mkdtemp(dir=path)

            try:
                # Try to create two files that differ only in case
                lower_file = os.path.join(test_dir, "casesensitivitytest.txt")
                upper_file = os.path.join(test_dir, "CASESENSITIVITYTEST.txt")

                # Create lowercase file
                Path(lower_file).touch()

                # Try to create uppercase file
                Path(upper_file).touch()

                # If both files exist, it's case-sensitive
                lower_exists = os.path.exists(lower_file)
                upper_exists = os.path.exists(upper_file)

                # Check if they're different files
                if lower_exists and upper_exists:
                    # Verify they're actually different files
                    return os.path.samefile(lower_file, upper_file) is False

                return False

            finally:
                # Clean up
                import shutil
                shutil.rmtree(test_dir, ignore_errors=True)

        except (OSError, IOError):
            # If we can't test, assume case-insensitive (macOS default)
            return False

    @staticmethod
    def check_apfs_features(path: str = ".") -> Dict[str, bool]:
        """Check which APFS features are available/enabled.

        Args:
            path: Path to check (defaults to current directory)

        Returns:
            Dictionary of APFS feature flags:
            - is_apfs: Whether the volume is APFS
            - supports_cloning: Whether file cloning is supported
            - supports_snapshots: Whether snapshots are supported
            - is_encrypted: Whether the volume is encrypted
            - case_sensitive: Whether the volume is case-sensitive
        """
        features = {
            "is_apfs": False,
            "supports_cloning": False,
            "supports_snapshots": False,
            "is_encrypted": False,
            "case_sensitive": False,
        }

        if platform.system() != "Darwin":
            return features

        # Check if it's APFS
        fs_type = FilesystemValidator.detect_volume_type(path)
        features["is_apfs"] = fs_type == "apfs"

        if not features["is_apfs"]:
            return features

        # APFS always supports cloning and snapshots
        features["supports_cloning"] = True
        features["supports_snapshots"] = True

        # Check case sensitivity
        features["case_sensitive"] = FilesystemValidator.is_case_sensitive(path)

        # Check encryption status using diskutil
        try:
            abs_path = os.path.abspath(path)
            result = subprocess.run(
                ["diskutil", "info", abs_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                # Look for encryption indicators
                features["is_encrypted"] = (
                    "encrypted: yes" in output or
                    "filevault: yes" in output or
                    "encryption" in output
                )

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass

        return features

    @staticmethod
    def get_volume_info(path: str = ".") -> Dict[str, str]:
        """Get detailed volume information for the given path.

        Args:
            path: Path to check (defaults to current directory)

        Returns:
            Dictionary containing volume information
        """
        info = {
            "path": os.path.abspath(path),
            "filesystem": FilesystemValidator.detect_volume_type(path) or "unknown",
            "case_sensitive": str(FilesystemValidator.is_case_sensitive(path)),
        }

        if platform.system() == "Darwin":
            try:
                abs_path = os.path.abspath(path)
                result = subprocess.run(
                    ["diskutil", "info", abs_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        if "Volume Name:" in line:
                            info["volume_name"] = line.split(":")[-1].strip()
                        elif "Mount Point:" in line:
                            info["mount_point"] = line.split(":")[-1].strip()

            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                pass

        return info
