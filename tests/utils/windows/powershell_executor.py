"""PowerShell script execution utilities for Windows testing."""
import subprocess
import time
from pathlib import Path
from typing import Optional

from tests.utils.windows.data_structures import PowerShellScriptResult


class PowerShellExecutor:
    """Execute PowerShell scripts and commands with proper error handling."""

    def __init__(self, timeout: int = 30, encoding: str = "utf-8"):
        """
        Initialize PowerShell executor.

        Args:
            timeout: Maximum execution time in seconds (default: 30)
            encoding: Text encoding for output (default: utf-8)
        """
        self.timeout = timeout
        self.encoding = encoding
        self._verify_powershell_available()

    def _verify_powershell_available(self) -> None:
        """
        Verify PowerShell is available on the system.

        Raises:
            RuntimeError: If PowerShell is not available
        """
        try:
            result = subprocess.run(
                ["pwsh", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("PowerShell Core (pwsh) not available")
        except FileNotFoundError:
            raise RuntimeError(
                "PowerShell Core (pwsh) not found. Please install PowerShell 7.x"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("PowerShell verification timed out")

    def run_script(
        self,
        script_path: Path | str,
        *args,
        env: Optional[dict] = None,
        timeout: Optional[int] = None,
    ) -> PowerShellScriptResult:
        """
        Execute a PowerShell script file.

        Args:
            script_path: Path to the .ps1 script file
            *args: Arguments to pass to the script
            env: Environment variables to set (optional)
            timeout: Override default timeout (optional)

        Returns:
            PowerShellScriptResult with execution details

        Raises:
            FileNotFoundError: If script file doesn't exist
            subprocess.TimeoutExpired: If execution exceeds timeout
        """
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"PowerShell script not found: {script_path}")

        # Build command
        cmd = ["pwsh", "-File", str(script_path)] + list(args)

        # Merge custom env with system environment
        if env:
            import os
            merged_env = os.environ.copy()
            merged_env.update(env)
        else:
            merged_env = None

        # Execute with timing
        start_time = time.time()
        exec_timeout = timeout or self.timeout

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.encoding,
                timeout=exec_timeout,
                env=merged_env,
            )
            execution_time = time.time() - start_time

            return PowerShellScriptResult(
                script_path=script_path,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                args=list(args),
                environment_vars=env or {},
            )

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return PowerShellScriptResult(
                script_path=script_path,
                exit_code=-1,
                stdout=e.stdout.decode(self.encoding) if e.stdout else "",
                stderr=f"Timeout after {exec_timeout}s",
                execution_time=execution_time,
                args=list(args),
                environment_vars=env or {},
            )

    def run_command(
        self,
        command: str,
        env: Optional[dict] = None,
        timeout: Optional[int] = None,
    ) -> PowerShellScriptResult:
        """
        Execute a PowerShell command directly.

        Args:
            command: PowerShell command string to execute
            env: Environment variables to set (optional)
            timeout: Override default timeout (optional)

        Returns:
            PowerShellScriptResult with execution details
        """
        # Build command
        cmd = ["pwsh", "-Command", command]

        # Merge custom env with system environment
        if env:
            import os
            merged_env = os.environ.copy()
            merged_env.update(env)
        else:
            merged_env = None

        # Execute with timing
        start_time = time.time()
        exec_timeout = timeout or self.timeout

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.encoding,
                timeout=exec_timeout,
                env=merged_env,
            )
            execution_time = time.time() - start_time

            return PowerShellScriptResult(
                script_path=None,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                args=[],
                environment_vars=env or {},
            )

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return PowerShellScriptResult(
                script_path=None,
                exit_code=-1,
                stdout=e.stdout.decode(self.encoding) if e.stdout else "",
                stderr=f"Timeout after {exec_timeout}s",
                execution_time=execution_time,
                args=[],
                environment_vars=env or {},
            )

    def validate_script_syntax(self, script_path: Path | str) -> tuple[bool, str]:
        """
        Validate PowerShell script syntax without executing it.

        Args:
            script_path: Path to the .ps1 script file

        Returns:
            Tuple of (is_valid, error_message)
        """
        script_path = Path(script_path)
        if not script_path.exists():
            return False, f"Script not found: {script_path}"

        # Use PowerShell's script analyzer
        cmd = [
            "pwsh",
            "-Command",
            f"$null = [System.Management.Automation.PSParser]::Tokenize("
            f"(Get-Content -Path '{script_path}' -Raw), [ref]$null)",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.encoding,
                timeout=5,
            )

            if result.returncode == 0:
                return True, "Syntax valid"
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, "Syntax validation timed out"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_powershell_version(self) -> str:
        """
        Get PowerShell version string.

        Returns:
            Version string (e.g., "7.4.1")
        """
        try:
            result = subprocess.run(
                ["pwsh", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return "not available"

    def check_execution_policy(self) -> str:
        """
        Get current PowerShell execution policy.

        Returns:
            Execution policy string (e.g., "RemoteSigned", "Restricted")
        """
        try:
            result = subprocess.run(
                ["pwsh", "-Command", "Get-ExecutionPolicy"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return "not available"
