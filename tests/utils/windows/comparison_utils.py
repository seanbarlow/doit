"""Output comparison utilities for cross-platform testing."""
import re
from pathlib import Path, PurePosixPath
from typing import List
from .line_ending_utils import normalize_line_endings


class Discrepancy:
    """Represents a difference found during comparison."""

    def __init__(
        self, location: str, windows_value: str, linux_value: str, severity: str, description: str
    ):
        self.location = location
        self.windows_value = windows_value
        self.linux_value = linux_value
        self.severity = severity  # 'critical' | 'warning' | 'info'
        self.description = description


class CrossPlatformComparisonResult:
    """Result of comparing Windows and Linux test outputs."""

    def __init__(
        self,
        test_name: str,
        windows_output: str,
        linux_output: str,
        matches: bool,
        discrepancies: List[Discrepancy],
        normalization_applied: List[str],
    ):
        self.test_name = test_name
        self.windows_output = windows_output
        self.linux_output = linux_output
        self.matches = matches
        self.discrepancies = discrepancies
        self.normalization_applied = normalization_applied


class ComparisonTools:
    """Utilities for normalizing and comparing outputs across platforms."""

    def normalize_output(self, output: str) -> str:
        """
        Normalize output for cross-platform comparison.

        Normalization steps:
        1. Convert CRLF to LF
        2. Normalize path separators to forward slash
        3. Remove trailing whitespace
        4. Strip ANSI color codes

        Args:
            output: Raw output string

        Returns:
            Normalized output string
        """
        # Normalize line endings
        normalized = normalize_line_endings(output, "LF")

        # Remove ANSI color codes
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        normalized = ansi_escape.sub("", normalized)

        # Remove trailing whitespace from each line
        lines = normalized.split("\n")
        lines = [line.rstrip() for line in lines]
        normalized = "\n".join(lines)

        # Normalize common path patterns (e.g., C:\path\to\file -> /path/to/file)
        # This is a simplified approach - more sophisticated regex could be used
        normalized = re.sub(r"[A-Z]:\\", "/", normalized)
        normalized = normalized.replace("\\", "/")

        return normalized

    def normalize_path(self, path: str) -> str:
        """
        Normalize a path string for comparison.

        Args:
            path: Path string (may be Windows or Unix format)

        Returns:
            Path with forward slashes, no drive letter
        """
        # Replace backslashes with forward slashes
        normalized = path.replace("\\", "/")

        # Remove drive letter if present (e.g., C:/)
        if len(normalized) >= 2 and normalized[1] == ":":
            normalized = normalized[2:]

        return normalized

    def compare_outputs(
        self, windows_output: str, linux_output: str, strict: bool = False
    ) -> CrossPlatformComparisonResult:
        """
        Compare outputs from Windows and Linux test runs.

        Args:
            windows_output: Output from Windows test
            linux_output: Output from Linux test
            strict: If True, require exact match after normalization

        Returns:
            CrossPlatformComparisonResult with match status and discrepancies
        """
        normalizations = []

        # Normalize both outputs
        norm_windows = self.normalize_output(windows_output)
        norm_linux = self.normalize_output(linux_output)
        normalizations.extend(["line_endings", "paths", "ansi_codes", "trailing_whitespace"])

        discrepancies = []

        # Compare line by line
        windows_lines = norm_windows.split("\n")
        linux_lines = norm_linux.split("\n")

        if len(windows_lines) != len(linux_lines):
            discrepancies.append(
                Discrepancy(
                    location="line_count",
                    windows_value=str(len(windows_lines)),
                    linux_value=str(len(linux_lines)),
                    severity="warning",
                    description=f"Different number of lines: {len(windows_lines)} vs {len(linux_lines)}",
                )
            )

        # Compare common lines
        for i, (win_line, linux_line) in enumerate(zip(windows_lines, linux_lines), 1):
            if win_line != linux_line:
                # Check if it's a path difference we should tolerate
                win_paths = self.extract_paths(win_line)
                linux_paths = self.extract_paths(linux_line)

                if win_paths and linux_paths:
                    # Path difference - less critical unless strict mode
                    severity = "critical" if strict else "info"
                else:
                    severity = "critical"

                discrepancies.append(
                    Discrepancy(
                        location=f"line_{i}",
                        windows_value=win_line[:100],  # Truncate for readability
                        linux_value=linux_line[:100],
                        severity=severity,
                        description=f"Line {i} differs",
                    )
                )

        # Determine if outputs match
        matches = len(discrepancies) == 0
        if not strict:
            # In non-strict mode, ignore 'info' severity discrepancies
            critical_discrepancies = [d for d in discrepancies if d.severity != "info"]
            matches = len(critical_discrepancies) == 0

        return CrossPlatformComparisonResult(
            test_name="comparison",
            windows_output=norm_windows,
            linux_output=norm_linux,
            matches=matches,
            discrepancies=discrepancies,
            normalization_applied=normalizations,
        )

    def extract_paths(self, text: str) -> List[str]:
        """
        Extract all path-like strings from text.

        Args:
            text: Text containing paths

        Returns:
            List of detected path strings
        """
        # Simple heuristic: look for strings with path separators
        path_pattern = r"(?:[A-Z]:\\|/)?(?:[\w\-\.]+[/\\])+[\w\-\.]+"
        matches = re.findall(path_pattern, text)
        return matches
