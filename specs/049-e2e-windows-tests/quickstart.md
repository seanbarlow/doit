# Quickstart: Windows E2E Testing

**Feature**: 049-e2e-windows-tests
**Audience**: Developers contributing to Windows testing infrastructure
**Time to Complete**: 15-20 minutes

## Overview

This guide will help you set up your Windows development environment, run the Windows E2E test suite, and write your first Windows-specific test.

---

## Prerequisites

### Required Software

1. **Windows 10 or Windows 11**
   - Version 1809 or later recommended
   - Developer Mode optional but helpful for symlink tests

2. **Python 3.11+**
   ```powershell
   python --version  # Should show 3.11.0 or higher
   ```
   If not installed: [Download Python](https://www.python.org/downloads/)

3. **PowerShell 7.x**
   ```powershell
   pwsh -v  # Should show 7.0 or higher
   ```
   If not installed:
   ```powershell
   winget install --id Microsoft.PowerShell --source winget
   ```

4. **Git for Windows**
   ```powershell
   git --version  # Should show git version
   ```
   If not installed: [Download Git](https://git-scm.com/download/win)

5. **doit Toolkit** (development installation)
   ```powershell
   git clone https://github.com/your-org/doit.git
   cd doit
   pip install -e ".[dev]"
   ```

---

## First-Time Setup

### 1. Verify Environment

Run the environment verification script:

```powershell
pytest tests/e2e/windows/test_environment.py -v
```

Expected output:
```
tests/e2e/windows/test_environment.py::test_powershell_available PASSED
tests/e2e/windows/test_environment.py::test_python_version PASSED
tests/e2e/windows/test_environment.py::test_git_available PASSED
```

If any tests fail, review the Prerequisites section.

### 2. Configure PowerShell Execution Policy (If Needed)

If you encounter "script execution is disabled" errors:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Verify:
```powershell
Get-ExecutionPolicy -List
```

### 3. Run Sample Test

Run a single test to verify setup:

```powershell
pytest tests/e2e/windows/test_init_workflow.py::test_init_creates_doit_directory -v
```

Expected output:
```
tests/e2e/windows/test_init_workflow.py::test_init_creates_doit_directory PASSED
```

---

## Running Tests

### Run All Windows E2E Tests

```powershell
pytest tests/e2e/windows/ -v
```

### Run Specific Test Categories

**PowerShell Script Tests Only:**
```powershell
pytest tests/e2e/windows/ -m powershell -v
```

**Cross-Platform Parity Tests Only:**
```powershell
pytest tests/e2e/windows/test_cross_platform_parity.py -v
```

**Fast Tests Only (Skip Slow):**
```powershell
pytest tests/e2e/windows/ -m "not slow" -v
```

### Run with Verbose Output

```powershell
pytest tests/e2e/windows/ -vv --tb=long
```

### Generate HTML Report

```powershell
pytest tests/e2e/windows/ --html=tests/reports/windows_e2e_report.html --self-contained-html
```

View report: Open `tests/reports/windows_e2e_report.html` in your browser.

---

## Writing Your First Windows Test

### Example: Testing a doit Command on Windows

Create a new test file: `tests/e2e/windows/test_my_feature.py`

```python
import pytest
from pathlib import Path
import subprocess

@pytest.mark.windows
@pytest.mark.e2e
def test_my_doit_command(temp_project_dir, windows_test_env):
    """
    Test that 'doit my-command' works correctly on Windows.

    Args:
        temp_project_dir: Pytest fixture providing temporary directory
        windows_test_env: Pytest fixture providing Windows environment info
    """
    # Arrange: Set up test conditions
    assert windows_test_env.platform == 'win32', "Test must run on Windows"

    # Act: Execute the command
    result = subprocess.run(
        ['doit', 'my-command', '--option', 'value'],
        cwd=temp_project_dir,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    # Assert: Verify expected outcomes
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert 'Success' in result.stdout, "Expected success message not found"

    # Verify created files (use pathlib for cross-platform compatibility)
    expected_file = temp_project_dir / '.doit' / 'memory' / 'my_file.md'
    assert expected_file.exists(), f"Expected file not created: {expected_file}"

    # Verify file contents
    content = expected_file.read_text(encoding='utf-8')
    assert 'Expected content' in content
```

### Run Your Test

```powershell
pytest tests/e2e/windows/test_my_feature.py::test_my_doit_command -v
```

---

## Common Patterns

### Pattern 1: Testing PowerShell Scripts

```python
@pytest.mark.windows
@pytest.mark.powershell
def test_powershell_script(powershell_executor):
    """Test that a PowerShell script executes correctly."""
    result = powershell_executor.run_script(
        Path('.doit/scripts/powershell/my_script.ps1'),
        'arg1', 'arg2'
    )

    assert result.exit_code == 0
    assert 'Expected output' in result.stdout
    assert result.stderr == ''
```

### Pattern 2: Cross-Platform Comparison

```python
@pytest.mark.e2e
def test_cross_platform_parity_my_command(comparison_tools):
    """Test that command produces same output on Windows and Linux."""
    # Run on current platform (Windows in this case)
    win_result = subprocess.run(['doit', 'my-command'], capture_output=True, text=True)

    # Load Linux reference output (from CI or pre-recorded)
    linux_output = Path('tests/fixtures/expected_outputs/my_command_linux.txt').read_text()

    # Compare
    comparison = comparison_tools.compare_outputs(win_result.stdout, linux_output)
    assert comparison.matches, f"Outputs differ: {comparison.discrepancies}"
```

### Pattern 3: Windows Path Validation

```python
@pytest.mark.windows
def test_windows_path_handling():
    """Test Windows-specific path scenarios."""
    from tests.utils.windows.path_utils import WindowsPathValidator

    validator = WindowsPathValidator()

    # Test reserved name detection
    assert validator.is_reserved_name('CON')
    assert validator.is_reserved_name('con.txt')
    assert not validator.is_reserved_name('config.txt')

    # Test path length validation
    short_path = r'C:\short\path\file.txt'
    assert not validator.exceeds_max_path(short_path)

    very_long_path = r'C:\' + 'a' * 300 + r'\file.txt'
    assert validator.exceeds_max_path(very_long_path)
```

---

## Debugging Failed Tests

### View Test Output

```powershell
pytest tests/e2e/windows/test_my_feature.py -v -s
```
The `-s` flag shows print statements and stdout.

### Drop into Debugger on Failure

```powershell
pytest tests/e2e/windows/test_my_feature.py --pdb
```

### Keep Test Artifacts

By default, temporary directories are cleaned up. To inspect artifacts:

```powershell
pytest tests/e2e/windows/test_my_feature.py --basetemp=./test_artifacts
```

Artifacts will be in `./test_artifacts/`.

### Run Only Failed Tests

After a test run, re-run only failures:

```powershell
pytest --lf  # "last failed"
```

---

## CI Integration

### GitHub Actions Workflow

The Windows E2E tests run automatically in GitHub Actions on every pull request.

**View Workflow**: `.github/workflows/windows-e2e-tests.yml`

**Manual Trigger**:
1. Go to Actions tab in GitHub
2. Select "Windows E2E Tests" workflow
3. Click "Run workflow"

### Download CI Artifacts

When tests fail in CI:
1. Navigate to the failed workflow run
2. Scroll to "Artifacts" section
3. Download "windows-test-results"
4. Extract and review logs, reports, generated files

---

## Best Practices

### 1. Always Use pathlib for Paths

**Good**:
```python
from pathlib import Path

file_path = temp_dir / '.doit' / 'memory' / 'constitution.md'
content = file_path.read_text(encoding='utf-8')
```

**Avoid**:
```python
# Don't concatenate strings with os.path.join or manual slashes
file_path = temp_dir + '\\.doit\\memory\\constitution.md'  # ❌
```

### 2. Always Specify Text Encoding

**Good**:
```python
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
content = file_path.read_text(encoding='utf-8')
```

**Avoid**:
```python
result = subprocess.run(cmd, capture_output=True, text=True)  # ❌ Uses default encoding
```

### 3. Use Markers Appropriately

```python
@pytest.mark.windows  # Skipped on non-Windows
@pytest.mark.e2e      # Categorized as E2E test
@pytest.mark.slow     # Can be skipped with -m "not slow"
def test_full_workflow():
    ...
```

### 4. Write Descriptive Assertions

**Good**:
```python
assert expected_file.exists(), \
    f"Expected file not created: {expected_file}\nFiles in dir: {list(temp_dir.iterdir())}"
```

**Avoid**:
```python
assert expected_file.exists()  # ❌ No context on failure
```

### 5. Clean Up Resources

Fixtures handle cleanup automatically, but for explicit resources:

```python
def test_with_resource():
    resource = create_resource()
    try:
        # Test code
        assert resource.works()
    finally:
        resource.cleanup()
```

---

## Troubleshooting

### Issue: "pwsh: command not found"

**Solution**: Install PowerShell 7.x
```powershell
winget install --id Microsoft.PowerShell --source winget
```

Restart your terminal after installation.

### Issue: "Script execution is disabled"

**Solution**: Set execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Tests fail with encoding errors

**Solution**: Ensure UTF-8 encoding is specified:
```python
result = subprocess.run(cmd, encoding='utf-8', errors='replace')
```

### Issue: Path length errors on Windows

**Solution**: Enable long path support:
1. Run as Administrator:
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
                    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```
2. Restart your machine

Or use shorter temp directory:
```powershell
pytest tests/e2e/windows/ --basetemp=C:\tmp
```

### Issue: Tests hang or timeout

**Solution**: Run with shorter timeout:
```python
result = subprocess.run(cmd, timeout=30)
```

Check for infinite loops or waiting for input.

---

## Next Steps

### Learn More

- **Full Specification**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **API Contracts**: [contracts/test-api.md](contracts/test-api.md)
- **Data Models**: [data-model.md](data-model.md)

### Contribute

1. Read the spec and plan to understand requirements
2. Pick an unimplemented test case from the spec
3. Write the test following patterns in this guide
4. Run tests locally and ensure they pass
5. Submit a pull request

### Get Help

- **Ask Questions**: Open a GitHub discussion
- **Report Bugs**: Create an issue with the `windows` label
- **Review Examples**: Check existing tests in `tests/e2e/windows/`

---

## Quick Reference

### Common Commands

```powershell
# Run all Windows E2E tests
pytest tests/e2e/windows/ -v

# Run specific test
pytest tests/e2e/windows/test_file.py::test_name -v

# Run with markers
pytest tests/e2e/windows/ -m "powershell and not slow" -v

# Generate HTML report
pytest tests/e2e/windows/ --html=report.html --self-contained-html

# Debug on failure
pytest tests/e2e/windows/ --pdb

# Keep test artifacts
pytest tests/e2e/windows/ --basetemp=./artifacts
```

### Key Files

- `tests/e2e/windows/conftest.py` - Fixtures and configuration
- `tests/utils/windows/` - Reusable utilities
- `tests/fixtures/windows/` - Test data and sample projects
- `.github/workflows/windows-e2e-tests.yml` - CI configuration

---

**Happy Testing!** 🎉

For questions or issues, refer to the [spec.md](spec.md) or open a GitHub issue.
