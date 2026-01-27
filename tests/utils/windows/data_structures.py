"""Data structures for Windows E2E testing."""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TestEnvironment:
    """Windows test environment configuration and state."""

    def __init__(
        self,
        platform: str,
        powershell_version: str,
        python_version: str,
        git_version: str,
        is_ci: bool,
        temp_dir: Path,
        encoding: str = "utf-8",
        line_ending: str = "CRLF",
    ):
        self.platform = platform
        self.powershell_version = powershell_version
        self.python_version = python_version
        self.git_version = git_version
        self.is_ci = is_ci
        self.temp_dir = temp_dir
        self.encoding = encoding
        self.line_ending = line_ending


class PowerShellScriptResult:
    """Result of executing a PowerShell script."""

    def __init__(
        self,
        script_path: Path,
        exit_code: int,
        stdout: str,
        stderr: str,
        execution_time: float,
        args: List[str],
        environment_vars: Optional[Dict[str, str]] = None,
    ):
        self.script_path = script_path
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time = execution_time
        self.args = args
        self.environment_vars = environment_vars or {}


class TestArtifact:
    """Files and data generated during test execution."""

    def __init__(
        self,
        artifact_type: str,
        file_path: Path,
        test_case: str,
        created_at: datetime,
        size_bytes: int,
        description: str = "",
    ):
        self.artifact_type = artifact_type
        self.file_path = file_path
        self.test_case = test_case
        self.created_at = created_at
        self.size_bytes = size_bytes
        self.description = description


class E2EWorkflowResult:
    """Result of running a full end-to-end workflow test."""

    def __init__(
        self,
        workflow_name: str,
        commands_executed: List[str],
        success: bool,
        failure_point: Optional[str],
        generated_files: List[Path],
        execution_time: float,
        environment: TestEnvironment,
    ):
        self.workflow_name = workflow_name
        self.commands_executed = commands_executed
        self.success = success
        self.failure_point = failure_point
        self.generated_files = generated_files
        self.execution_time = execution_time
        self.environment = environment
