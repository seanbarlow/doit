"""Cross-platform output comparison utilities for macOS testing.

Provides tools to normalize and compare outputs across platforms (macOS, Windows, Linux)
accounting for platform-specific differences like path separators, line endings,
and Unicode normalization.
"""

import os
import platform
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from .unicode_utils import normalize_nfc, normalize_nfd, compare_normalized
except ImportError:
    # Fallback for when module is imported via sys.path.insert
    from unicode_utils import normalize_nfc, normalize_nfd, compare_normalized


class ComparisonTools:
    """Tools for comparing outputs across platforms."""

    def __init__(self):
        """Initialize comparison tools."""
        self.is_macos = platform.system() == "Darwin"
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"

    def normalize_output(
        self,
        output: str,
        normalize_paths: bool = True,
        normalize_line_endings: bool = True,
        normalize_unicode: bool = True,
        target_platform: Optional[str] = None
    ) -> str:
        """Normalize output for cross-platform comparison.

        Args:
            output: output string to normalize
            normalize_paths: convert path separators to forward slashes
            normalize_line_endings: convert all line endings to LF
            normalize_unicode: normalize Unicode to NFC
            target_platform: target platform for normalization (None = current)

        Returns:
            Normalized output string
        """
        result = output

        # Normalize line endings
        if normalize_line_endings:
            result = result.replace("\r\n", "\n").replace("\r", "\n")

        # Normalize paths
        if normalize_paths:
            result = self.normalize_path(result, target_platform)

        # Normalize Unicode
        if normalize_unicode:
            # Default to NFC (Windows/Linux standard) for cross-platform comparison
            result = normalize_nfc(result)

        return result

    def normalize_path(self, path_or_text: str, target_platform: Optional[str] = None) -> str:
        """Normalize path separators in text.

        Args:
            path_or_text: path or text containing paths
            target_platform: target platform (None = forward slashes for cross-platform)

        Returns:
            Text with normalized path separators
        """
        # Replace backslashes with forward slashes for cross-platform comparison
        if target_platform is None or target_platform.lower() in ("posix", "linux", "macos"):
            return path_or_text.replace("\\", "/")
        elif target_platform.lower() == "windows":
            return path_or_text.replace("/", "\\")

        return path_or_text

    def compare_outputs(
        self,
        output1: str,
        output2: str,
        normalize: bool = True,
        ignore_whitespace: bool = False
    ) -> Tuple[bool, List[str]]:
        """Compare two outputs, optionally normalizing them first.

        Args:
            output1: first output string
            output2: second output string
            normalize: whether to normalize before comparing
            ignore_whitespace: whether to ignore whitespace differences

        Returns:
            Tuple of (are_equal, list_of_differences)
        """
        if normalize:
            output1 = self.normalize_output(output1)
            output2 = self.normalize_output(output2)

        if ignore_whitespace:
            output1 = " ".join(output1.split())
            output2 = " ".join(output2.split())

        if output1 == output2:
            return True, []

        # Find differences
        differences = []
        lines1 = output1.split("\n")
        lines2 = output2.split("\n")

        if len(lines1) != len(lines2):
            differences.append(f"Different line counts: {len(lines1)} vs {len(lines2)}")

        max_lines = max(len(lines1), len(lines2))
        for i in range(max_lines):
            line1 = lines1[i] if i < len(lines1) else ""
            line2 = lines2[i] if i < len(lines2) else ""

            if line1 != line2:
                differences.append(f"Line {i+1}: '{line1}' vs '{line2}'")

        return False, differences[:10]  # Limit to first 10 differences

    def handle_unicode_differences(
        self,
        text1: str,
        text2: str,
        auto_normalize: bool = True
    ) -> Tuple[bool, str]:
        """Handle Unicode normalization differences between texts.

        Args:
            text1: first text
            text2: second text
            auto_normalize: automatically normalize to same form

        Returns:
            Tuple of (are_equal_after_normalization, explanation)
        """
        # Try direct comparison first
        if text1 == text2:
            return True, "Texts are identical"

        # Try NFC normalization
        if compare_normalized(text1, text2, "NFC"):
            return True, "Texts are equal after NFC normalization"

        # Try NFD normalization
        if compare_normalized(text1, text2, "NFD"):
            return True, "Texts are equal after NFD normalization"

        return False, "Texts differ even after Unicode normalization"

    def extract_paths_from_output(self, output: str) -> List[str]:
        """Extract file paths from output text.

        Args:
            output: output text to parse

        Returns:
            List of extracted paths
        """
        # Common path patterns
        patterns = [
            r'[A-Za-z]:[/\\][^\s:]+',  # Windows absolute paths
            r'/[^\s:]+',  # Unix absolute paths
            r'\./[^\s:]+',  # Relative paths starting with ./
            r'[^\s/\\:]+/[^\s:]+',  # Paths with at least one /
        ]

        paths = []
        for pattern in patterns:
            matches = re.findall(pattern, output)
            paths.extend(matches)

        # Deduplicate and clean
        unique_paths = []
        seen = set()
        for path in paths:
            # Clean up trailing punctuation
            cleaned = path.rstrip(".,;:!?)")
            if cleaned and cleaned not in seen:
                unique_paths.append(cleaned)
                seen.add(cleaned)

        return unique_paths

    def compare_file_contents(
        self,
        filepath1: str,
        filepath2: str,
        normalize: bool = True
    ) -> Tuple[bool, List[str]]:
        """Compare contents of two files.

        Args:
            filepath1: first file path
            filepath2: second file path
            normalize: whether to normalize before comparing

        Returns:
            Tuple of (are_equal, list_of_differences)
        """
        if not os.path.exists(filepath1):
            return False, [f"File not found: {filepath1}"]

        if not os.path.exists(filepath2):
            return False, [f"File not found: {filepath2}"]

        try:
            with open(filepath1, "r", encoding="utf-8") as f1:
                content1 = f1.read()

            with open(filepath2, "r", encoding="utf-8") as f2:
                content2 = f2.read()

            return self.compare_outputs(content1, content2, normalize=normalize)

        except (IOError, UnicodeDecodeError) as e:
            return False, [f"Error reading files: {str(e)}"]

    def verify_line_endings(self, filepath: str) -> str:
        """Detect line ending type in a file.

        Args:
            filepath: file to check

        Returns:
            "LF", "CRLF", "CR", "MIXED", or "NONE"
        """
        if not os.path.exists(filepath):
            return "NONE"

        try:
            with open(filepath, "rb") as f:
                content = f.read()

            has_crlf = b"\r\n" in content
            has_lf = b"\n" in content
            has_cr = b"\r" in content

            if has_crlf and not (has_lf or has_cr):
                return "CRLF"
            elif has_lf and not has_crlf:
                # Check for standalone CR
                if has_cr:
                    return "MIXED"
                return "LF"
            elif has_cr and not (has_crlf or has_lf):
                return "CR"
            elif has_crlf or has_lf or has_cr:
                return "MIXED"

            return "NONE"

        except (IOError, OSError):
            return "NONE"

    def get_platform_info(self) -> Dict[str, any]:
        """Get information about the current platform for comparison.

        Returns:
            Dictionary with platform information
        """
        return {
            "system": platform.system(),
            "is_macos": self.is_macos,
            "is_windows": self.is_windows,
            "is_linux": self.is_linux,
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "default_encoding": "utf-8",
            "path_separator": os.path.sep,
            "line_ending": "CRLF" if self.is_windows else "LF",
            "unicode_normalization": "NFD" if self.is_macos else "NFC",
        }

    def create_comparison_report(
        self,
        name: str,
        output1: str,
        output2: str,
        platform1: str = "current",
        platform2: str = "expected"
    ) -> str:
        """Create a detailed comparison report.

        Args:
            name: name of the comparison
            output1: first output
            output2: second output
            platform1: label for first output
            platform2: label for second output

        Returns:
            Formatted comparison report
        """
        are_equal, differences = self.compare_outputs(output1, output2)

        report = [
            f"# Comparison Report: {name}",
            f"",
            f"**Platform 1**: {platform1}",
            f"**Platform 2**: {platform2}",
            f"**Result**: {'✓ MATCH' if are_equal else '✗ MISMATCH'}",
            f"",
        ]

        if not are_equal:
            report.append("## Differences Found")
            report.append("")
            for i, diff in enumerate(differences, 1):
                report.append(f"{i}. {diff}")
            report.append("")

        report.append("## Platform Information")
        report.append("")
        info = self.get_platform_info()
        for key, value in info.items():
            report.append(f"- **{key}**: {value}")

        return "\n".join(report)
