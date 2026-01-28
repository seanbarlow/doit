"""BSD command compatibility utilities for macOS testing.

macOS uses BSD versions of common Unix utilities (sed, grep, awk, find)
which have different behavior from GNU versions commonly found on Linux.
This module provides wrappers to handle these differences.
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


class BSDCommandWrapper:
    """Wrapper for BSD commands with compatibility handling."""

    def __init__(self):
        """Initialize BSD command wrapper and detect available utilities."""
        self.is_macos = platform.system() == "Darwin"
        self.gnu_prefix = self._detect_gnu_prefix()

    def _detect_gnu_prefix(self) -> Optional[str]:
        """Detect if GNU utilities are installed (e.g., via Homebrew).

        Returns:
            Prefix for GNU commands ("g" if installed, None otherwise)
        """
        if not self.is_macos:
            return None

        # Check if GNU sed is available
        if shutil.which("gsed"):
            return "g"

        return None

    def has_gnu_utils(self) -> bool:
        """Check if GNU utilities are available on the system.

        Returns:
            True if GNU utils are installed, False otherwise
        """
        return self.gnu_prefix is not None

    def sed_inplace(
        self,
        pattern: str,
        replacement: str,
        filepath: str,
        use_gnu: bool = False
    ) -> Tuple[bool, str]:
        """Execute sed in-place replacement, handling BSD vs GNU differences.

        BSD sed requires an extension argument for -i, GNU sed does not.

        Args:
            pattern: sed pattern to match
            replacement: replacement text
            filepath: file to modify
            use_gnu: prefer GNU sed if available

        Returns:
            Tuple of (success, output/error message)
        """
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"

        try:
            # Choose command based on preference and availability
            if use_gnu and self.has_gnu_utils():
                cmd = ["gsed", "-i", f"s/{pattern}/{replacement}/g", filepath]
            elif self.is_macos:
                # BSD sed requires backup extension (use '' for no backup)
                cmd = ["sed", "-i", "", f"s/{pattern}/{replacement}/g", filepath]
            else:
                # GNU sed on Linux
                cmd = ["sed", "-i", f"s/{pattern}/{replacement}/g", filepath]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, "Success"
            else:
                return False, result.stderr

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            return False, str(e)

    def grep_extended(
        self,
        pattern: str,
        filepath: str,
        use_gnu: bool = False
    ) -> Tuple[bool, List[str]]:
        """Execute grep with extended regex, handling BSD vs GNU differences.

        Args:
            pattern: regex pattern to search for
            filepath: file to search in
            use_gnu: prefer GNU grep if available

        Returns:
            Tuple of (success, list of matching lines)
        """
        if not os.path.exists(filepath):
            return False, [f"File not found: {filepath}"]

        try:
            # Choose command based on preference and availability
            if use_gnu and self.has_gnu_utils():
                cmd = ["ggrep", "-E", pattern, filepath]
            else:
                # Both BSD and GNU grep support -E
                cmd = ["grep", "-E", pattern, filepath]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            # grep returns 1 if no matches found (not an error)
            if result.returncode in (0, 1):
                lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
                return True, lines
            else:
                return False, [result.stderr]

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            return False, [str(e)]

    def awk_posix(
        self,
        script: str,
        filepath: str,
        use_gnu: bool = False
    ) -> Tuple[bool, str]:
        """Execute awk in POSIX mode, handling BSD vs GNU differences.

        Args:
            script: awk script to execute
            filepath: file to process
            use_gnu: prefer GNU awk if available

        Returns:
            Tuple of (success, output)
        """
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"

        try:
            # Choose command based on preference and availability
            if use_gnu and self.has_gnu_utils():
                cmd = ["gawk", script, filepath]
            else:
                # BSD awk
                cmd = ["awk", script, filepath]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            return False, str(e)

    def find_bsd(
        self,
        directory: str,
        name_pattern: Optional[str] = None,
        type_filter: Optional[str] = None,
        use_gnu: bool = False
    ) -> Tuple[bool, List[str]]:
        """Execute find command, handling BSD vs GNU differences.

        Args:
            directory: directory to search in
            name_pattern: optional name pattern to match
            type_filter: optional type filter (f, d, l, etc.)
            use_gnu: prefer GNU find if available

        Returns:
            Tuple of (success, list of found paths)
        """
        if not os.path.exists(directory):
            return False, [f"Directory not found: {directory}"]

        try:
            # Build command
            if use_gnu and self.has_gnu_utils():
                cmd = ["gfind", directory]
            else:
                cmd = ["find", directory]

            # Add type filter
            if type_filter:
                cmd.extend(["-type", type_filter])

            # Add name pattern
            if name_pattern:
                cmd.extend(["-name", name_pattern])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                paths = result.stdout.strip().split("\n") if result.stdout.strip() else []
                return True, paths
            else:
                return False, [result.stderr]

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            return False, [str(e)]

    def detect_command_version(self, command: str) -> str:
        """Detect whether a command is BSD or GNU version.

        Args:
            command: command name (sed, grep, awk, find)

        Returns:
            "BSD", "GNU", or "UNKNOWN"
        """
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = (result.stdout + result.stderr).lower()

            if "gnu" in output:
                return "GNU"
            elif "bsd" in output or (result.returncode != 0 and self.is_macos):
                # BSD commands often don't support --version
                return "BSD"

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass

        return "UNKNOWN"

    def get_command_info(self) -> dict:
        """Get information about available commands on the system.

        Returns:
            Dictionary mapping command names to their type (BSD/GNU)
        """
        commands = ["sed", "grep", "awk", "find"]
        info = {}

        for cmd in commands:
            info[cmd] = self.detect_command_version(cmd)

            # Also check for GNU version
            gnu_cmd = f"g{cmd}"
            if shutil.which(gnu_cmd):
                info[gnu_cmd] = self.detect_command_version(gnu_cmd)

        return info

    def test_bsd_compatibility(self) -> dict:
        """Run compatibility tests for BSD commands.

        Returns:
            Dictionary of test results
        """
        results = {
            "is_macos": self.is_macos,
            "has_gnu_utils": self.has_gnu_utils(),
            "command_info": self.get_command_info(),
        }

        return results


def get_shell_type() -> str:
    """Detect the current shell type.

    Returns:
        Shell name (bash, zsh, sh, etc.)
    """
    shell = os.environ.get("SHELL", "")
    return os.path.basename(shell) if shell else "unknown"


def is_zsh_default() -> bool:
    """Check if zsh is the default shell (macOS Catalina+).

    Returns:
        True if zsh is default, False otherwise
    """
    return get_shell_type() == "zsh"


def run_bash_script(script_path: str, args: Optional[List[str]] = None) -> Tuple[bool, str, str]:
    """Run a bash script, ensuring bash interpreter is used.

    Args:
        script_path: path to bash script
        args: optional command-line arguments

    Returns:
        Tuple of (success, stdout, stderr)
    """
    if not os.path.exists(script_path):
        return False, "", f"Script not found: {script_path}"

    cmd = ["bash", script_path]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        return result.returncode == 0, result.stdout, result.stderr

    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
        return False, "", str(e)
