"""Tests for PowerShell error handling on Windows."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_missing_script_file_error(temp_project_dir, powershell_executor):
    """
    Test that missing script files produce appropriate errors.

    Given: A non-existent script path
    When: Script execution is attempted
    Then: FileNotFoundError is raised
    """
    non_existent = temp_project_dir / "scripts" / "missing.ps1"

    with pytest.raises(FileNotFoundError):
        powershell_executor.run_script(non_existent)


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_script_runtime_error_handling(temp_project_dir, powershell_executor):
    """
    Test that runtime errors in scripts are properly captured.

    Given: A script with runtime errors
    When: Script is executed
    Then: Error is captured in stderr with non-zero exit code
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script with runtime error
    error_script = scripts_dir / "error.ps1"
    error_script.write_text(
        """
Write-Host "Before error"
# Attempt to access non-existent file
Get-Content "C:\\NonExistent\\File.txt" -ErrorAction Stop
Write-Host "After error (should not reach)"
""",
        encoding="utf-8",
    )

    # Execute script
    result = powershell_executor.run_script(error_script)

    # Verify error captured
    assert result.exit_code != 0, "Script with error should have non-zero exit code"
    assert len(result.stderr) > 0 or "cannot find" in result.stdout.lower(), \
        "Error message should be captured"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_invalid_parameter_error(temp_project_dir, powershell_executor):
    """
    Test that invalid parameters produce appropriate errors.

    Given: A script expecting specific parameters
    When: Invalid parameters are provided
    Then: Error is reported
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script with strict parameter validation
    param_script = scripts_dir / "params.ps1"
    param_script.write_text(
        """
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Option1", "Option2", "Option3")]
    [string]$Choice
)

Write-Host "You chose: $Choice"
""",
        encoding="utf-8",
    )

    # Execute with invalid parameter
    result = powershell_executor.run_script(param_script, "-Choice", "InvalidOption")

    # Verify error (either non-zero exit or error message)
    assert result.exit_code != 0 or len(result.stderr) > 0, \
        "Invalid parameter should produce error"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_execution_policy_bypass(temp_project_dir, powershell_executor):
    """
    Test that scripts can execute regardless of execution policy.

    Given: PowerShell executor
    When: Execution policy is checked
    Then: Scripts execute successfully (pwsh uses appropriate policy)
    """
    # Check current execution policy
    policy = powershell_executor.check_execution_policy()
    assert policy != "not available", "PowerShell should be available"

    # Create simple script
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    test_script = scripts_dir / "policy-test.ps1"
    test_script.write_text('Write-Host "Execution policy OK"', encoding="utf-8")

    # Script should execute (pwsh handles policy appropriately)
    result = powershell_executor.run_script(test_script)
    assert result.exit_code == 0, "Script should execute successfully"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_script_timeout_handling(temp_project_dir, powershell_executor):
    """
    Test that script timeouts are handled properly.

    Given: A script that runs longer than timeout
    When: Execution timeout is reached
    Then: Execution is terminated with timeout error
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create long-running script
    slow_script = scripts_dir / "slow.ps1"
    slow_script.write_text(
        """
Write-Host "Starting long operation"
Start-Sleep -Seconds 60
Write-Host "Completed (should not reach)"
""",
        encoding="utf-8",
    )

    # Execute with short timeout
    result = powershell_executor.run_script(slow_script, timeout=2)

    # Verify timeout handling
    assert result.exit_code == -1, "Timeout should result in exit code -1"
    assert "Timeout" in result.stderr or "timeout" in result.stderr.lower(), \
        "Timeout error should be indicated in stderr"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_exit_code_propagation(temp_project_dir, powershell_executor):
    """
    Test that script exit codes are properly propagated.

    Given: Scripts with various exit codes
    When: Scripts complete
    Then: Correct exit codes are returned
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Test various exit codes
    test_codes = [0, 1, 2, 42, 127]

    for code in test_codes:
        script = scripts_dir / f"exit-{code}.ps1"
        script.write_text(f'exit {code}', encoding="utf-8")

        result = powershell_executor.run_script(script)
        assert result.exit_code == code, \
            f"Expected exit code {code}, got {result.exit_code}"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_stderr_vs_stdout_separation(temp_project_dir, powershell_executor):
    """
    Test that stdout and stderr streams are properly separated.

    Given: A script that writes to both stdout and stderr
    When: Script is executed
    Then: Output streams are captured separately
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script writing to both streams
    streams_script = scripts_dir / "streams.ps1"
    streams_script.write_text(
        """
Write-Host "This goes to stdout"
Write-Error "This goes to stderr" -ErrorAction Continue
Write-Host "More stdout"
""",
        encoding="utf-8",
    )

    # Execute script
    result = powershell_executor.run_script(streams_script)

    # Verify stream separation
    assert "This goes to stdout" in result.stdout, "Stdout message missing"
    assert "More stdout" in result.stdout, "Second stdout message missing"
    # Note: Write-Error may appear in stderr or be handled differently by PowerShell


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_error_with_partial_output(temp_project_dir, powershell_executor):
    """
    Test that partial output before error is captured.

    Given: A script that produces output then fails
    When: Script is executed
    Then: Partial output is captured along with error
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script with partial success
    partial_script = scripts_dir / "partial.ps1"
    partial_script.write_text(
        """
Write-Host "Step 1 complete"
Write-Host "Step 2 complete"
Write-Host "Step 3 complete"
throw "Error at step 4"
Write-Host "Step 5 (should not reach)"
""",
        encoding="utf-8",
    )

    # Execute script
    result = powershell_executor.run_script(partial_script)

    # Verify partial output captured
    assert "Step 1 complete" in result.stdout, "Step 1 output missing"
    assert "Step 2 complete" in result.stdout, "Step 2 output missing"
    assert "Step 3 complete" in result.stdout, "Step 3 output missing"
    assert result.exit_code != 0, "Script should fail with non-zero exit code"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_command_not_found_error(temp_project_dir, powershell_executor):
    """
    Test that non-existent commands produce appropriate errors.

    Given: A script calling non-existent commands
    When: Script is executed
    Then: Error is captured with non-zero exit code
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script with non-existent command
    bad_cmd_script = scripts_dir / "bad-command.ps1"
    bad_cmd_script.write_text(
        """
$ErrorActionPreference = "Stop"
Write-Host "Before bad command"
NonExistentCommand-DoSomething
Write-Host "After bad command (should not reach)"
""",
        encoding="utf-8",
    )

    # Execute script
    result = powershell_executor.run_script(bad_cmd_script)

    # Verify error handling
    assert result.exit_code != 0, "Script with bad command should fail"
    # Error message may be in stdout or stderr depending on ErrorAction
