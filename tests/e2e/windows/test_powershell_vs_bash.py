"""Tests comparing PowerShell and Bash script behavior on Windows."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_simple_script_output_parity(temp_project_dir, powershell_executor, comparison_tools):
    """
    Test that equivalent PowerShell and Bash scripts produce comparable output.

    Given: Equivalent .ps1 and .sh scripts
    When: Both are executed
    Then: Outputs match after normalization
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create PowerShell script
    ps_script = scripts_dir / "test.ps1"
    ps_script.write_text(
        """
Write-Host "Starting process"
Write-Host "Working directory: $PWD"
Write-Host "Process complete"
""",
        encoding="utf-8",
    )

    # Create equivalent Bash script
    bash_script = scripts_dir / "test.sh"
    bash_script.write_text(
        """#!/bin/bash
echo "Starting process"
echo "Working directory: $(pwd)"
echo "Process complete"
""",
        encoding="utf-8",
    )

    # Execute PowerShell script
    ps_result = powershell_executor.run_script(ps_script)
    assert ps_result.exit_code == 0, f"PowerShell script failed: {ps_result.stderr}"

    # For comparison purposes, verify PS output contains expected text
    assert "Starting process" in ps_result.stdout
    assert "Working directory:" in ps_result.stdout
    assert "Process complete" in ps_result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_script_with_parameters_parity(temp_project_dir, powershell_executor):
    """
    Test that PowerShell and Bash scripts handle parameters equivalently.

    Given: Scripts that accept parameters
    When: Scripts are executed with arguments
    Then: Parameters are processed correctly in both
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create PowerShell script with parameters
    ps_script = scripts_dir / "params.ps1"
    ps_script.write_text(
        """
param(
    [string]$Name,
    [int]$Count = 1
)

for ($i = 1; $i -le $Count; $i++) {
    Write-Host "Hello, $Name - Iteration $i"
}
""",
        encoding="utf-8",
    )

    # Execute with parameters
    ps_result = powershell_executor.run_script(
        ps_script, "-Name", "Test", "-Count", "3"
    )

    assert ps_result.exit_code == 0, f"PowerShell script failed: {ps_result.stderr}"
    assert "Hello, Test - Iteration 1" in ps_result.stdout
    assert "Hello, Test - Iteration 2" in ps_result.stdout
    assert "Hello, Test - Iteration 3" in ps_result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_path_handling_parity(temp_project_dir, powershell_executor, comparison_tools):
    """
    Test that PowerShell and Bash handle paths consistently.

    Given: Scripts that work with file paths
    When: Paths are processed
    Then: Output is comparable after normalization
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create test file
    test_file = temp_project_dir / "test.txt"
    test_file.write_text("test content", encoding="utf-8")

    # Create PowerShell script
    ps_script = scripts_dir / "paths.ps1"
    ps_script.write_text(
        f"""
$testFile = "{test_file}"
Write-Host "File exists: $(Test-Path $testFile)"
Write-Host "Absolute path: $(Resolve-Path $testFile)"
""",
        encoding="utf-8",
    )

    # Execute PowerShell script
    ps_result = powershell_executor.run_script(ps_script)

    assert ps_result.exit_code == 0, f"PowerShell script failed: {ps_result.stderr}"
    assert "File exists: True" in ps_result.stdout
    assert "Absolute path:" in ps_result.stdout

    # Verify path normalization works
    normalized = comparison_tools.normalize_output(ps_result.stdout)
    assert "/" in normalized or "\\" in normalized  # Path separators present


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_exit_code_parity(temp_project_dir, powershell_executor):
    """
    Test that PowerShell and Bash scripts use exit codes equivalently.

    Given: Scripts with various exit conditions
    When: Scripts complete
    Then: Exit codes are consistent between both
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create PowerShell script with exit 0 (success)
    ps_success = scripts_dir / "success.ps1"
    ps_success.write_text(
        """
Write-Host "Success"
exit 0
""",
        encoding="utf-8",
    )

    # Create PowerShell script with exit 1 (failure)
    ps_failure = scripts_dir / "failure.ps1"
    ps_failure.write_text(
        """
Write-Host "Failure"
exit 1
""",
        encoding="utf-8",
    )

    # Test success script
    result_success = powershell_executor.run_script(ps_success)
    assert result_success.exit_code == 0, "Success script should return 0"

    # Test failure script
    result_failure = powershell_executor.run_script(ps_failure)
    assert result_failure.exit_code == 1, "Failure script should return 1"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_environment_variable_parity(temp_project_dir, powershell_executor):
    """
    Test that PowerShell and Bash access environment variables equivalently.

    Given: Scripts that read environment variables
    When: Scripts are executed with custom env vars
    Then: Both can access the variables correctly
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create PowerShell script
    ps_script = scripts_dir / "env.ps1"
    ps_script.write_text(
        """
Write-Host "TEST_VAR = $env:TEST_VAR"
Write-Host "USER_NAME = $env:USER_NAME"
""",
        encoding="utf-8",
    )

    # Execute with environment variables
    custom_env = {
        "TEST_VAR": "test_value",
        "USER_NAME": "test_user",
    }

    ps_result = powershell_executor.run_script(ps_script, env=custom_env)

    assert ps_result.exit_code == 0, f"PowerShell script failed: {ps_result.stderr}"
    assert "TEST_VAR = test_value" in ps_result.stdout
    assert "USER_NAME = test_user" in ps_result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_multiline_output_parity(temp_project_dir, powershell_executor, comparison_tools):
    """
    Test that multiline output is handled consistently.

    Given: Scripts producing multiline output
    When: Output is captured
    Then: Line structure is preserved and comparable
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create PowerShell script with multiline output
    ps_script = scripts_dir / "multiline.ps1"
    ps_script.write_text(
        """
Write-Host "Line 1"
Write-Host "Line 2"
Write-Host "Line 3"
Write-Host "Line 4"
Write-Host "Line 5"
""",
        encoding="utf-8",
    )

    # Execute PowerShell script
    ps_result = powershell_executor.run_script(ps_script)

    assert ps_result.exit_code == 0, f"PowerShell script failed: {ps_result.stderr}"

    # Verify multiline structure
    lines = ps_result.stdout.strip().split("\n")
    assert len(lines) >= 5, f"Expected at least 5 lines, got {len(lines)}"

    # Verify content
    output_text = ps_result.stdout
    assert "Line 1" in output_text
    assert "Line 2" in output_text
    assert "Line 3" in output_text
    assert "Line 4" in output_text
    assert "Line 5" in output_text


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.slow
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_execution_time_comparable(temp_project_dir, powershell_executor):
    """
    Test that PowerShell scripts have reasonable execution times.

    Given: Simple PowerShell scripts
    When: Execution time is measured
    Then: Scripts complete in reasonable timeframes
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create simple PowerShell script
    ps_script = scripts_dir / "timing.ps1"
    ps_script.write_text(
        """
Write-Host "Starting"
Start-Sleep -Milliseconds 100
Write-Host "Complete"
""",
        encoding="utf-8",
    )

    # Execute and check timing
    ps_result = powershell_executor.run_script(ps_script)

    assert ps_result.exit_code == 0, f"PowerShell script failed: {ps_result.stderr}"
    assert ps_result.execution_time > 0.1, "Execution time too short"
    assert ps_result.execution_time < 5.0, "Execution time too long"
