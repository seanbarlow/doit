# Test API Contracts: Windows E2E Testing

**Feature**: 049-e2e-windows-tests
**Phase**: 1 (Design & Contracts)
**Date**: 2026-01-26

## Overview

This document defines the interfaces, contracts, and patterns for the Windows and PowerShell end-to-end testing infrastructure. These contracts ensure consistency across test modules and provide clear guidelines for test development.

---

## Pytest Fixtures

### `windows_test_env`

**Scope**: session

**Purpose**: Provides a configured TestEnvironment instance for Windows-specific tests.

**Signature**:
```python
@pytest.fixture(scope="session")
def windows_test_env() -> TestEnvironment:
    """Create and configure test environment for Windows tests."""
    ...
```

**Returns**:
- `TestEnvironment` object with detected platform details

**Example Usage**:
```python
def test_windows_path_handling(windows_test_env):
    assert windows_test_env.platform == 'win32'
    assert 'PowerShell' in windows_test_env.powershell_version
```

---

### `temp_project_dir`

**Scope**: function

**Purpose**: Provides a temporary directory for creating test projects, automatically cleaned up after test.

**Signature**:
```python
@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory for testing."""
    ...
```

**Returns**:
- `Path` object pointing to temporary directory

**Guarantees**:
- Directory is empty at start of test
- Directory is deleted after test completes (unless test fails and artifact retention enabled)
- Unique for each test function

**Example Usage**:
```python
def test_doit_init(temp_project_dir):
    result = subprocess.run(['doit', 'init'], cwd=temp_project_dir)
    assert result.returncode == 0
    assert (temp_project_dir / '.doit').exists()
```

---

### `powershell_executor`

**Scope**: session

**Purpose**: Provides a PowerShell script executor with consistent configuration and output handling.

**Signature**:
```python
@pytest.fixture(scope="session")
def powershell_executor() -> PowerShellExecutor:
    """Create PowerShell script executor."""
    ...
```

**Returns**:
- `PowerShellExecutor` instance

**Methods**:
- `run_script(script_path, *args, **kwargs) -> PowerShellScriptResult`
- `run_command(command: str, **kwargs) -> PowerShellScriptResult`

**Example Usage**:
```python
def test_powershell_script(powershell_executor):
    result = powershell_executor.run_script(
        Path('.doit/scripts/powershell/create-feature.ps1'),
        'test-feature'
    )
    assert result.exit_code == 0
```

---

### `comparison_tools`

**Scope**: session

**Purpose**: Provides utilities for cross-platform output comparison and normalization.

**Signature**:
```python
@pytest.fixture(scope="session")
def comparison_tools() -> ComparisonTools:
    """Create output comparison utilities."""
    ...
```

**Returns**:
- `ComparisonTools` instance

**Methods**:
- `normalize_output(output: str) -> str`
- `normalize_path(path: str) -> str`
- `compare_outputs(win_output: str, linux_output: str) -> CrossPlatformComparisonResult`

**Example Usage**:
```python
def test_cross_platform_parity(comparison_tools):
    win_output = "C:\\path\\to\\file.txt\r\n"
    linux_output = "/path/to/file.txt\n"

    result = comparison_tools.compare_outputs(win_output, linux_output)
    assert result.matches
```

---

## Test Utility Interfaces

### PowerShellExecutor

**Purpose**: Execute PowerShell scripts with consistent configuration and error handling.

**Interface**:
```python
class PowerShellExecutor:
    def __init__(
        self,
        timeout: int = 30,
        encoding: str = 'utf-8',
        check: bool = False
    ):
        """
        Initialize PowerShell executor.

        Args:
            timeout: Maximum execution time in seconds
            encoding: Text encoding for output (default: utf-8)
            check: Whether to raise exception on non-zero exit code
        """
        ...

    def run_script(
        self,
        script_path: Path,
        *args: str,
        env: dict[str, str] | None = None,
        cwd: Path | None = None
    ) -> PowerShellScriptResult:
        """
        Execute a PowerShell script file.

        Args:
            script_path: Path to .ps1 file
            *args: Arguments to pass to script
            env: Environment variables to set (merges with os.environ)
            cwd: Working directory for execution

        Returns:
            PowerShellScriptResult with exit code, stdout, stderr

        Raises:
            TimeoutError: If execution exceeds timeout
            PowerShellExecutionError: If check=True and exit code != 0
        """
        ...

    def run_command(
        self,
        command: str,
        env: dict[str, str] | None = None,
        cwd: Path | None = None
    ) -> PowerShellScriptResult:
        """
        Execute a PowerShell command string.

        Args:
            command: PowerShell command to execute
            env: Environment variables to set
            cwd: Working directory for execution

        Returns:
            PowerShellScriptResult with exit code, stdout, stderr
        """
        ...
```

**Error Handling**:
- `TimeoutError`: Raised if script exceeds timeout
- `PowerShellExecutionError`: Raised if check=True and script fails
- `FileNotFoundError`: Raised if script_path doesn't exist
- `ValueError`: Raised if command is empty or invalid

---

### ComparisonTools

**Purpose**: Normalize and compare outputs across platforms.

**Interface**:
```python
class ComparisonTools:
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
        ...

    def normalize_path(self, path: str) -> str:
        """
        Normalize a path string for comparison.

        Args:
            path: Path string (may be Windows or Unix format)

        Returns:
            Path with forward slashes, no drive letter
        """
        ...

    def compare_outputs(
        self,
        windows_output: str,
        linux_output: str,
        strict: bool = False
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
        ...

    def extract_paths(self, text: str) -> list[str]:
        """
        Extract all path-like strings from text.

        Args:
            text: Text containing paths

        Returns:
            List of detected path strings
        """
        ...
```

---

### WindowsPathValidator

**Purpose**: Validate Windows path characteristics and constraints.

**Interface**:
```python
class WindowsPathValidator:
    RESERVED_NAMES: set[str] = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    MAX_PATH_LENGTH: int = 260

    def analyze_path(self, path: str | Path) -> WindowsPathInfo:
        """
        Analyze a path for Windows-specific characteristics.

        Args:
            path: Path to analyze

        Returns:
            WindowsPathInfo with analysis results
        """
        ...

    def is_reserved_name(self, filename: str) -> bool:
        """
        Check if filename is a Windows reserved name.

        Args:
            filename: Name to check (with or without extension)

        Returns:
            True if reserved, False otherwise
        """
        ...

    def exceeds_max_path(self, path: str | Path) -> bool:
        """
        Check if path exceeds Windows MAX_PATH limitation.

        Args:
            path: Path to check

        Returns:
            True if path length > 260 characters
        """
        ...
```

---

## Test Markers

### Platform Markers

**`@pytest.mark.windows`**
- **Purpose**: Mark tests that should only run on Windows
- **Auto-skip**: Skipped automatically on non-Windows platforms

**`@pytest.mark.unix`**
- **Purpose**: Mark tests that should only run on Unix-like systems
- **Auto-skip**: Skipped automatically on Windows

**`@pytest.mark.powershell`**
- **Purpose**: Mark tests that validate PowerShell scripts
- **Auto-skip**: Skipped if PowerShell 7.x not available

**Example**:
```python
@pytest.mark.windows
@pytest.mark.powershell
def test_powershell_script_windows_only():
    # This test runs only on Windows with PowerShell 7.x
    ...
```

### Test Type Markers

**`@pytest.mark.e2e`**
- **Purpose**: Mark end-to-end workflow tests
- **Usage**: Allows running only E2E tests with `pytest -m e2e`

**`@pytest.mark.slow`**
- **Purpose**: Mark slow tests (> 10 seconds)
- **Usage**: Can be skipped with `pytest -m "not slow"`

**`@pytest.mark.ci`**
- **Purpose**: Mark tests that should run in CI
- **Usage**: Used in GitHub Actions workflow

---

## Test Naming Conventions

### File Naming
- `test_{command}_workflow.py` - E2E tests for specific doit commands
- `test_powershell_*.py` - PowerShell script validation tests
- `test_cross_platform_*.py` - Cross-platform parity tests
- `conftest.py` - Fixtures and configuration

### Test Function Naming
- `test_{scenario}_{expected_outcome}` - General pattern
- `test_{command}_success_case` - Success path tests
- `test_{command}_error_{error_type}` - Error handling tests
- `test_parity_{feature}` - Cross-platform parity tests

**Examples**:
- `test_init_creates_doit_directory`
- `test_specit_error_invalid_description`
- `test_parity_generated_spec_files`

---

## Assertion Patterns

### Standard Assertions

**File Existence**:
```python
assert (project_dir / '.doit' / 'memory' / 'constitution.md').exists(), \
    "Constitution file should be created"
```

**Exit Code**:
```python
assert result.returncode == 0, f"Command failed: {result.stderr}"
```

**Output Content**:
```python
assert 'Success' in result.stdout, "Success message not found in output"
assert result.stderr == '', f"Unexpected stderr: {result.stderr}"
```

### Custom Assertions

**Path Normalization**:
```python
def assert_paths_equal(actual: str, expected: str):
    """Assert paths are equal after normalization."""
    assert normalize_path(actual) == normalize_path(expected), \
        f"Paths differ: {actual} != {expected}"
```

**Output Similarity**:
```python
def assert_outputs_similar(actual: str, expected: str, tolerance: float = 0.1):
    """Assert outputs are similar within tolerance."""
    similarity = calculate_similarity(actual, expected)
    assert similarity >= (1 - tolerance), \
        f"Outputs too different: {similarity:.2%} similarity"
```

---

## CI Integration Contract

### GitHub Actions Workflow

**Trigger Events**:
- Pull request to `main` or `develop` branches
- Push to `main` or `develop` branches

**Required Steps**:
1. Checkout code
2. Set up Python 3.11+
3. Verify PowerShell 7.x availability
4. Install dependencies
5. Run tests with `pytest tests/e2e/windows/`
6. Upload artifacts on failure

**Artifact Upload**:
- **Always uploaded**: Test reports (JUnit XML, HTML)
- **On failure**: Test logs, generated files, screenshots (if applicable)

**Success Criteria**:
- All tests pass (exit code 0)
- Execution time < 10 minutes
- No timeout errors

---

## Versioning and Compatibility

### PowerShell Version Requirements
- **Minimum**: PowerShell 7.0
- **Recommended**: PowerShell 7.3+
- **Not Supported**: Windows PowerShell 5.1

### Windows Version Requirements
- **Supported**: Windows 10 (version 1809+), Windows 11
- **CI**: windows-latest runner (currently Windows Server 2022)

### Python Version Requirements
- **Minimum**: Python 3.11
- **Tested**: Python 3.11, 3.12

---

## Error Handling Contract

### Expected Exceptions

**`PowerShellExecutionError`**:
```python
class PowerShellExecutionError(Exception):
    def __init__(self, result: PowerShellScriptResult):
        self.result = result
        message = f"PowerShell script failed: {result.stderr}"
        super().__init__(message)
```

**`CrossPlatformParityError`**:
```python
class CrossPlatformParityError(Exception):
    def __init__(self, comparison: CrossPlatformComparisonResult):
        self.comparison = comparison
        message = f"Outputs differ: {len(comparison.discrepancies)} discrepancies"
        super().__init__(message)
```

### Error Message Format

All error messages should include:
1. **Context**: What was being tested
2. **Expected**: What should have happened
3. **Actual**: What actually happened
4. **Diagnostic Info**: Relevant details (paths, commands, outputs)

**Example**:
```
test_init_creates_constitution FAILED

Context: Testing 'doit init' command on Windows
Expected: .doit/memory/constitution.md file created
Actual: File not found
Command: doit init --project-name test-project
Working Dir: C:\Temp\pytest-123\test-init-0
Exit Code: 0
Stdout: [...]
Stderr: [empty]
```

---

## Notes

These contracts are designed to:
- **Ensure consistency** across all test modules
- **Simplify test authoring** with well-defined fixtures and utilities
- **Enable debugging** with clear error messages and artifact collection
- **Support CI/CD** with reliable automation and reporting
