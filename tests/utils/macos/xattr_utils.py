"""Extended attribute utilities for macOS testing.

macOS supports extended attributes (xattr) which store metadata about files.
Common attributes include com.apple.metadata.*, com.apple.quarantine, etc.
This module provides utilities to work with extended attributes in tests.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ExtendedAttributeHandler:
    """Handler for macOS extended attributes (xattr)."""

    def __init__(self):
        """Initialize extended attribute handler."""
        self.is_macos = platform.system() == "Darwin"

    def get_xattr(self, filepath: str, attr_name: str) -> Optional[str]:
        """Get a specific extended attribute value.

        Args:
            filepath: path to file
            attr_name: name of attribute to get

        Returns:
            Attribute value as string, or None if not found
        """
        if not self.is_macos:
            return None

        if not os.path.exists(filepath):
            return None

        try:
            result = subprocess.run(
                ["xattr", "-p", attr_name, filepath],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass

        return None

    def set_xattr(self, filepath: str, attr_name: str, attr_value: str) -> bool:
        """Set an extended attribute value.

        Args:
            filepath: path to file
            attr_name: name of attribute to set
            attr_value: value to set

        Returns:
            True if successful, False otherwise
        """
        if not self.is_macos:
            return False

        if not os.path.exists(filepath):
            return False

        try:
            result = subprocess.run(
                ["xattr", "-w", attr_name, attr_value, filepath],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def list_xattrs(self, filepath: str) -> List[str]:
        """List all extended attributes for a file.

        Args:
            filepath: path to file

        Returns:
            List of attribute names
        """
        if not self.is_macos:
            return []

        if not os.path.exists(filepath):
            return []

        try:
            result = subprocess.run(
                ["xattr", "-l", filepath],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                attrs = []
                for line in result.stdout.split("\n"):
                    # Parse "attr_name: attr_value" format
                    if ":" in line:
                        attr_name = line.split(":")[0].strip()
                        if attr_name:
                            attrs.append(attr_name)
                return attrs

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass

        return []

    def remove_xattr(self, filepath: str, attr_name: str) -> bool:
        """Remove an extended attribute.

        Args:
            filepath: path to file
            attr_name: name of attribute to remove

        Returns:
            True if successful, False otherwise
        """
        if not self.is_macos:
            return False

        if not os.path.exists(filepath):
            return False

        try:
            result = subprocess.run(
                ["xattr", "-d", attr_name, filepath],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def clear_all_xattrs(self, filepath: str) -> bool:
        """Remove all extended attributes from a file.

        Args:
            filepath: path to file

        Returns:
            True if successful, False otherwise
        """
        if not self.is_macos:
            return False

        if not os.path.exists(filepath):
            return False

        try:
            result = subprocess.run(
                ["xattr", "-c", filepath],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def compare_xattrs(self, filepath1: str, filepath2: str) -> Tuple[bool, List[str]]:
        """Compare extended attributes between two files.

        Args:
            filepath1: first file path
            filepath2: second file path

        Returns:
            Tuple of (are_equal, list_of_differences)
        """
        if not self.is_macos:
            return True, []

        if not os.path.exists(filepath1) or not os.path.exists(filepath2):
            return False, ["One or both files not found"]

        attrs1 = set(self.list_xattrs(filepath1))
        attrs2 = set(self.list_xattrs(filepath2))

        differences = []

        # Check for missing attributes
        missing_in_2 = attrs1 - attrs2
        if missing_in_2:
            differences.append(f"Missing in file2: {', '.join(missing_in_2)}")

        missing_in_1 = attrs2 - attrs1
        if missing_in_1:
            differences.append(f"Missing in file1: {', '.join(missing_in_1)}")

        # Compare values for common attributes
        common_attrs = attrs1 & attrs2
        for attr in common_attrs:
            value1 = self.get_xattr(filepath1, attr)
            value2 = self.get_xattr(filepath2, attr)
            if value1 != value2:
                differences.append(f"Different value for {attr}")

        return len(differences) == 0, differences

    def has_quarantine_attr(self, filepath: str) -> bool:
        """Check if a file has the quarantine attribute.

        Files downloaded from the internet often have com.apple.quarantine.

        Args:
            filepath: path to file

        Returns:
            True if quarantine attribute exists, False otherwise
        """
        if not self.is_macos:
            return False

        attrs = self.list_xattrs(filepath)
        return "com.apple.quarantine" in attrs

    def remove_quarantine_attr(self, filepath: str) -> bool:
        """Remove the quarantine attribute from a file.

        Args:
            filepath: path to file

        Returns:
            True if successful, False otherwise
        """
        return self.remove_xattr(filepath, "com.apple.quarantine")

    def get_finder_info(self, filepath: str) -> Optional[str]:
        """Get Finder info extended attribute.

        Args:
            filepath: path to file

        Returns:
            Finder info value or None
        """
        return self.get_xattr(filepath, "com.apple.FinderInfo")

    def get_metadata_attrs(self, filepath: str) -> Dict[str, str]:
        """Get all com.apple.metadata.* attributes.

        Args:
            filepath: path to file

        Returns:
            Dictionary of metadata attributes
        """
        if not self.is_macos:
            return {}

        all_attrs = self.list_xattrs(filepath)
        metadata = {}

        for attr in all_attrs:
            if attr.startswith("com.apple.metadata."):
                value = self.get_xattr(filepath, attr)
                if value is not None:
                    metadata[attr] = value

        return metadata

    def copy_xattrs(self, source: str, dest: str) -> bool:
        """Copy all extended attributes from source to destination.

        Args:
            source: source file path
            dest: destination file path

        Returns:
            True if all attributes copied successfully, False otherwise
        """
        if not self.is_macos:
            return True  # No-op on non-macOS

        if not os.path.exists(source) or not os.path.exists(dest):
            return False

        attrs = self.list_xattrs(source)
        success = True

        for attr in attrs:
            value = self.get_xattr(source, attr)
            if value is not None:
                if not self.set_xattr(dest, attr, value):
                    success = False

        return success

    def get_xattr_summary(self, filepath: str) -> Dict[str, any]:
        """Get a summary of all extended attributes for a file.

        Args:
            filepath: path to file

        Returns:
            Dictionary with attribute summary
        """
        summary = {
            "filepath": filepath,
            "exists": os.path.exists(filepath),
            "has_xattrs": False,
            "xattr_count": 0,
            "has_quarantine": False,
            "has_finder_info": False,
            "has_metadata": False,
            "attributes": []
        }

        if not summary["exists"] or not self.is_macos:
            return summary

        attrs = self.list_xattrs(filepath)
        summary["has_xattrs"] = len(attrs) > 0
        summary["xattr_count"] = len(attrs)
        summary["attributes"] = attrs

        summary["has_quarantine"] = "com.apple.quarantine" in attrs
        summary["has_finder_info"] = "com.apple.FinderInfo" in attrs
        summary["has_metadata"] = any(attr.startswith("com.apple.metadata.") for attr in attrs)

        return summary
