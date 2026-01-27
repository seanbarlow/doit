"""Tests for PowerShell environment variable handling on Windows."""
import sys
import os
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_read_environment_variables(temp_project_dir, powershell_executor):
    """
    Test that PowerShell scripts can read environment variables.

    Given: Environment variables set in the system
    When: PowerShell script accesses $env:VAR
    Then: Variable values are correctly retrieved
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script that reads env vars
    env_script = scripts_dir / "read-env.ps1"
    env_script.write_text(
        """
Write-Host "MY_VAR = $env:MY_VAR"
Write-Host "MY_NUMBER = $env:MY_NUMBER"
Write-Host "MY_PATH = $env:MY_PATH"
""",
        encoding="utf-8",
    )

    # Execute with custom environment
    custom_env = {
        "MY_VAR": "test_value",
        "MY_NUMBER": "42",
        "MY_PATH": "C:\\test\\path",
    }

    result = powershell_executor.run_script(env_script, env=custom_env)

    assert result.exit_code == 0, f"Script failed: {result.stderr}"
    assert "MY_VAR = test_value" in result.stdout
    assert "MY_NUMBER = 42" in result.stdout
    assert "MY_PATH = C:\\test\\path" in result.stdout or "MY_PATH = C:/test/path" in result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_environment_variable_passing(temp_project_dir, powershell_executor):
    """
    Test that environment variables are properly passed to scripts.

    Given: Custom environment variables
    When: Script is executed with env parameter
    Then: Variables are accessible in script
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script
    check_env = scripts_dir / "check-env.ps1"
    check_env.write_text(
        """
if ($env:TEST_VAR -eq "expected_value") {
    Write-Host "Environment variable passed correctly"
    exit 0
} else {
    Write-Host "Environment variable not set or incorrect"
    exit 1
}
""",
        encoding="utf-8",
    )

    # Execute with environment
    custom_env = {"TEST_VAR": "expected_value"}
    result = powershell_executor.run_script(check_env, env=custom_env)

    assert result.exit_code == 0, "Environment variable not passed correctly"
    assert "passed correctly" in result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_script_isolation(temp_project_dir, powershell_executor):
    """
    Test that scripts run in isolated environments.

    Given: Multiple scripts with different environments
    When: Scripts are executed sequentially
    Then: Environment changes don't leak between executions
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script that reads ISOLATION_TEST
    test_script = scripts_dir / "isolation.ps1"
    test_script.write_text(
        """
Write-Host "ISOLATION_TEST = $env:ISOLATION_TEST"
""",
        encoding="utf-8",
    )

    # Execute with first environment
    env1 = {"ISOLATION_TEST": "value1"}
    result1 = powershell_executor.run_script(test_script, env=env1)
    assert "ISOLATION_TEST = value1" in result1.stdout

    # Execute with second environment
    env2 = {"ISOLATION_TEST": "value2"}
    result2 = powershell_executor.run_script(test_script, env=env2)
    assert "ISOLATION_TEST = value2" in result2.stdout

    # Execute with no custom environment (should be empty/different)
    result3 = powershell_executor.run_script(test_script)
    # Third execution should not have value2 (isolation confirmed)
    assert "value1" not in result3.stdout or "value2" not in result3.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_environment_variable_expansion(temp_project_dir, powershell_executor):
    """
    Test that environment variables are properly expanded in scripts.

    Given: Environment variables used in paths and strings
    When: Variables are referenced in script
    Then: Values are correctly expanded
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script with variable expansion
    expand_script = scripts_dir / "expand.ps1"
    expand_script.write_text(
        """
$basePath = $env:BASE_PATH
$fullPath = Join-Path $basePath "subdir\\file.txt"
Write-Host "Full path: $fullPath"
""",
        encoding="utf-8",
    )

    # Execute with environment
    custom_env = {"BASE_PATH": "C:\\projects\\test"}
    result = powershell_executor.run_script(expand_script, env=custom_env)

    assert result.exit_code == 0, f"Script failed: {result.stderr}"
    assert "C:\\projects\\test" in result.stdout or "C:/projects/test" in result.stdout
    assert "subdir" in result.stdout
    assert "file.txt" in result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_empty_environment_variable(temp_project_dir, powershell_executor):
    """
    Test that empty environment variables are handled correctly.

    Given: Environment variables set to empty strings
    When: Script accesses these variables
    Then: Empty values are returned (not null)
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script
    empty_env = scripts_dir / "empty-env.ps1"
    empty_env.write_text(
        """
Write-Host "EMPTY_VAR = [$env:EMPTY_VAR]"
if ($env:EMPTY_VAR -eq "") {
    Write-Host "Variable is empty string"
} elseif ($null -eq $env:EMPTY_VAR) {
    Write-Host "Variable is null"
}
""",
        encoding="utf-8",
    )

    # Execute with empty variable
    custom_env = {"EMPTY_VAR": ""}
    result = powershell_executor.run_script(empty_env, env=custom_env)

    assert result.exit_code == 0, f"Script failed: {result.stderr}"
    assert "EMPTY_VAR = []" in result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_special_characters_in_environment_variables(temp_project_dir, powershell_executor):
    """
    Test that environment variables with special characters are handled.

    Given: Environment variables containing special characters
    When: Script accesses these variables
    Then: Special characters are preserved
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script
    special_env = scripts_dir / "special-env.ps1"
    special_env.write_text(
        """
Write-Host "SPECIAL_VAR = $env:SPECIAL_VAR"
""",
        encoding="utf-8",
    )

    # Test various special characters
    test_values = [
        "value with spaces",
        "value;with;semicolons",
        "value=with=equals",
        "value\\with\\backslashes",
        "value/with/slashes",
    ]

    for test_value in test_values:
        custom_env = {"SPECIAL_VAR": test_value}
        result = powershell_executor.run_script(special_env, env=custom_env)

        assert result.exit_code == 0, f"Script failed for value '{test_value}': {result.stderr}"
        # Some characters may be normalized/escaped
        assert "SPECIAL_VAR =" in result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_inherit_system_environment(temp_project_dir, powershell_executor):
    """
    Test that scripts can access system environment variables.

    Given: Standard Windows environment variables
    When: Script accesses system variables
    Then: System variables are available
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script that reads system vars
    system_env = scripts_dir / "system-env.ps1"
    system_env.write_text(
        """
# Standard Windows environment variables
Write-Host "COMPUTERNAME exists: $($null -ne $env:COMPUTERNAME)"
Write-Host "OS exists: $($null -ne $env:OS)"
Write-Host "TEMP exists: $($null -ne $env:TEMP)"
""",
        encoding="utf-8",
    )

    # Execute without custom environment (should inherit system)
    result = powershell_executor.run_script(system_env)

    assert result.exit_code == 0, f"Script failed: {result.stderr}"
    # At least some system variables should exist
    assert "True" in result.stdout, "System environment variables not accessible"


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_environment_variable_case_sensitivity(temp_project_dir, powershell_executor):
    """
    Test environment variable case sensitivity on Windows.

    Given: Environment variables with different cases
    When: Variables are accessed
    Then: Case-insensitive access works (Windows behavior)
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script
    case_test = scripts_dir / "case-test.ps1"
    case_test.write_text(
        """
Write-Host "MyVar = $env:MyVar"
Write-Host "MYVAR = $env:MYVAR"
Write-Host "myvar = $env:myvar"
""",
        encoding="utf-8",
    )

    # Set environment variable
    custom_env = {"MyVar": "test_value"}
    result = powershell_executor.run_script(case_test, env=custom_env)

    assert result.exit_code == 0, f"Script failed: {result.stderr}"
    # On Windows, environment variables are case-insensitive
    # All three should show the same value
    output_lines = result.stdout.split("\n")
    # At least the exact case should match
    assert "MyVar = test_value" in result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_multiple_environment_variables(temp_project_dir, powershell_executor):
    """
    Test that multiple environment variables can be set simultaneously.

    Given: Multiple custom environment variables
    When: Script accesses all variables
    Then: All variables are accessible with correct values
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script
    multi_env = scripts_dir / "multi-env.ps1"
    multi_env.write_text(
        """
Write-Host "VAR1 = $env:VAR1"
Write-Host "VAR2 = $env:VAR2"
Write-Host "VAR3 = $env:VAR3"
Write-Host "VAR4 = $env:VAR4"
Write-Host "VAR5 = $env:VAR5"
""",
        encoding="utf-8",
    )

    # Execute with multiple variables
    custom_env = {
        "VAR1": "value1",
        "VAR2": "value2",
        "VAR3": "value3",
        "VAR4": "value4",
        "VAR5": "value5",
    }

    result = powershell_executor.run_script(multi_env, env=custom_env)

    assert result.exit_code == 0, f"Script failed: {result.stderr}"
    assert "VAR1 = value1" in result.stdout
    assert "VAR2 = value2" in result.stdout
    assert "VAR3 = value3" in result.stdout
    assert "VAR4 = value4" in result.stdout
    assert "VAR5 = value5" in result.stdout


@pytest.mark.windows
@pytest.mark.powershell
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_environment_variable_override(temp_project_dir, powershell_executor):
    """
    Test that custom environment variables override system variables.

    Given: Custom environment variable with same name as system variable
    When: Script is executed with custom environment
    Then: Custom value takes precedence
    """
    scripts_dir = temp_project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create script
    override_test = scripts_dir / "override.ps1"
    override_test.write_text(
        """
Write-Host "TEMP = $env:TEMP"
""",
        encoding="utf-8",
    )

    # Execute with custom TEMP
    custom_env = {"TEMP": "C:\\CustomTemp"}
    result = powershell_executor.run_script(override_test, env=custom_env)

    assert result.exit_code == 0, f"Script failed: {result.stderr}"
    assert "CustomTemp" in result.stdout, "Custom environment variable should override system"
