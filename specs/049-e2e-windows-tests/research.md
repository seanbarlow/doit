# Research: End-to-End Testing for Windows and PowerShell

**Feature**: 049-e2e-windows-tests
**Phase**: 0 (Research & Resolution)
**Date**: 2026-01-26

## Overview

This document captures research findings and technical decisions for implementing comprehensive end-to-end testing infrastructure for Windows and PowerShell environments in the doit toolkit.

## Research Areas

### 1. Pytest Windows-Specific Configuration

#### Decision: Use pytest markers and platform detection

**Rationale**:
- Pytest supports platform markers (`@pytest.mark.skipif`) for conditional test execution
- `sys.platform` provides reliable platform detection ('win32' for Windows)
- Allows same test suite to run on all platforms with selective execution

**Implementation Approach**:
```python
# In conftest.py
import pytest
import sys

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "windows: mark test to run only on Windows"
    )
    config.addinivalue_line(
        "markers", "unix: mark test to run only on Unix-like systems"
    )

# In pyproject.toml
[tool.pytest.ini_options]
markers = [
    "windows: tests that run only on Windows",
    "unix: tests that run only on Unix-like systems",
    "e2e: end-to-end tests",
    "powershell: PowerShell script validation tests"
]
```

**Alternatives Considered**:
- **tox with platform-specific environments**: More complex, slower CI execution
- **Separate test directories**: Causes code duplication and maintenance overhead
- **Custom pytest plugin**: Over-engineering for this use case

**References**:
- pytest documentation: https://docs.pytest.org/en/stable/how-to/mark.html
- Platform detection: https://docs.python.org/3/library/sys.html#sys.platform

---

### 2. PowerShell Script Testing Patterns

#### Decision: Use subprocess module with careful output handling

**Rationale**:
- subprocess.run() provides reliable PowerShell script execution from Python
- Capturing stdout/stderr as text enables output comparison
- Return codes validate error handling behavior
- Works consistently on Windows 10 and Windows 11

**Implementation Approach**:
```python
import subprocess
from pathlib import Path

def run_powershell_script(script_path: Path, *args) -> tuple[int, str, str]:
    """Execute a PowerShell script and return exit code, stdout, stderr."""
    cmd = ["pwsh", "-File", str(script_path)] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.returncode, result.stdout, result.stderr
```

**Key Considerations**:
- Use `pwsh` (PowerShell 7.x) not `powershell` (Windows PowerShell 5.1)
- Handle encoding explicitly (UTF-8) for consistent output comparison
- Use `errors='replace'` to prevent encoding exceptions
- Timeout handling for long-running scripts

**Alternatives Considered**:
- **Invoke-Command via Python COM**: Windows-only, more complex
- **PowerShell Module for Python**: External dependency, overkill
- **Direct .ps1 execution**: Shell injection risks, less portable

**References**:
- subprocess documentation: https://docs.python.org/3/library/subprocess.html
- PowerShell 7.x documentation: https://learn.microsoft.com/en-us/powershell/

---

### 3. Cross-Platform Test Parity

#### Decision: Normalize paths and line endings for comparison

**Rationale**:
- Path separators differ (`\` vs `/`) but semantic meaning is identical
- Line endings differ (CRLF vs LF) but content is equivalent
- Timestamps and absolute paths should be normalized before comparison
- Allows detecting real behavioral differences while ignoring cosmetic ones

**Implementation Approach**:
```python
from pathlib import Path, PurePosixPath

def normalize_path_for_comparison(path_str: str) -> str:
    """Convert any path to forward-slash format for comparison."""
    return str(PurePosixPath(Path(path_str)))

def normalize_line_endings(text: str) -> str:
    """Convert all line endings to LF for comparison."""
    return text.replace('\r\n', '\n').replace('\r', '\n')

def normalize_output_for_comparison(output: str) -> str:
    """Normalize output for cross-platform comparison."""
    # Normalize line endings
    normalized = normalize_line_endings(output)

    # Normalize common path patterns (e.g., C:\path\to\file -> /path/to/file)
    # Implementation: regex to detect and normalize paths in output

    # Remove timestamps if present
    # Implementation: regex to strip ISO timestamps

    return normalized
```

**Tolerance Policy**:
- **Paths**: Always normalize to forward slashes
- **Line endings**: Always normalize to LF
- **Timestamps**: Strip from comparison
- **Exit codes**: Must match exactly
- **Error messages**: Core message must match (platform-specific details tolerated)

**Alternatives Considered**:
- **Strict byte-for-byte comparison**: Too brittle, false negatives
- **Ignore all differences**: Too loose, misses real bugs
- **Manual test duplication**: Maintenance burden, inconsistency

**References**:
- pathlib documentation: https://docs.python.org/3/library/pathlib.html
- PEP 519 (OS Path Protocol): https://www.python.org/dev/peps/pep-0519/

---

### 4. GitHub Actions Windows Runner

#### Decision: Use windows-latest runner with PowerShell 7.x

**Rationale**:
- `windows-latest` currently maps to Windows Server 2022
- PowerShell 7.x is pre-installed on GitHub-hosted Windows runners
- Python 3.11+ is pre-installed
- Git for Windows is pre-installed
- Free tier provides sufficient minutes for E2E tests

**Implementation Approach**:
```yaml
name: Windows E2E Tests

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  test-windows:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Verify PowerShell version
        run: pwsh -Command '$PSVersionTable'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run Windows E2E tests
        run: pytest tests/e2e/windows/ -v --tb=short

      - name: Upload test artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: windows-test-results
          path: |
            tests/e2e/windows/reports/
            tests/e2e/windows/logs/
```

**Pre-installed Tools** (windows-latest):
- PowerShell 7.x
- Python 3.11
- Git for Windows
- Visual Studio Build Tools
- Windows SDK

**Performance Characteristics**:
- Average test execution: 3-5 minutes (estimated)
- Workflow overhead: ~1-2 minutes (checkout, setup)
- Total workflow time: Target < 10 minutes

**Alternatives Considered**:
- **windows-2019**: Older OS, less representative of user environments
- **Self-hosted runner**: More control but maintenance burden
- **Azure Pipelines**: Additional service dependency

**References**:
- GitHub Actions Windows runners: https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners
- Pre-installed software: https://github.com/actions/runner-images/blob/main/images/win/Windows2022-Readme.md

---

### 5. Windows-Specific Edge Cases

#### Decision: Comprehensive edge case test coverage with explicit handling

**Rationale**:
- Windows has platform-specific limitations that can cause subtle bugs
- Proactive testing prevents production issues
- Explicit error messages improve developer experience

**Edge Cases and Handling**:

##### 5.1. Path Length Limitations
- **Issue**: Windows has a 260-character MAX_PATH limit (unless long path support enabled)
- **Handling**:
  - Test suite validates behavior with paths near 260 characters
  - Document limitation in user-facing error messages
  - Use relative paths where possible to reduce length
  - Detect and warn when approaching limit

##### 5.2. Reserved Filenames
- **Issue**: Windows reserves filenames: CON, PRN, AUX, NUL, COM1-9, LPT1-9
- **Handling**:
  - Test suite validates rejection of reserved names
  - Provide clear error messages when user attempts to use reserved names
  - File/directory creation functions check against reserved list

##### 5.3. Case-Insensitive Filesystem
- **Issue**: Windows filesystem is case-insensitive but case-preserving
- **Handling**:
  - Test suite validates that `file.md` and `File.md` are treated as same file
  - Document behavior for users coming from case-sensitive systems
  - Normalize paths in internal comparisons

##### 5.4. PowerShell Execution Policies
- **Issue**: PowerShell may block script execution if policy is Restricted
- **Handling**:
  - Test suite validates behavior under different execution policies
  - Provide clear error message if script execution blocked
  - Document recommended execution policy setting (RemoteSigned or Unrestricted)

##### 5.5. File Permissions (No chmod)
- **Issue**: Windows doesn't have Unix-style chmod permissions
- **Handling**:
  - Test suite skips permission-related assertions on Windows
  - Use platform-agnostic permission checks where possible
  - Document platform differences in permission handling

##### 5.6. Line Ending Handling
- **Issue**: Windows uses CRLF (`\r\n`), Unix uses LF (`\n`)
- **Handling**:
  - Test suite validates correct line ending preservation in generated files
  - Normalize line endings during cross-platform comparisons
  - Git configured to handle line endings automatically (core.autocrlf)

##### 5.7. Symbolic Links
- **Issue**: Windows symbolic links require administrator privileges (or Developer Mode)
- **Handling**:
  - Test suite gracefully skips symlink tests if privileges insufficient
  - Document privilege requirements for symlink functionality
  - Provide alternative functionality where symlinks would be used

##### 5.8. Path Separator Handling
- **Issue**: Windows uses backslash (`\`), Unix uses forward slash (`/`)
- **Handling**:
  - Always use `pathlib.Path` for path operations (handles separators automatically)
  - Normalize to forward slashes for display/comparison
  - Test suite validates both separators work in user input

**Implementation Pattern**:
```python
# Example: Reserved filename check
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

def is_windows_reserved_name(name: str) -> bool:
    """Check if filename is reserved on Windows."""
    if sys.platform != 'win32':
        return False
    return name.upper().split('.')[0] in WINDOWS_RESERVED_NAMES
```

**References**:
- Windows filename restrictions: https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
- MAX_PATH limitation: https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation
- PowerShell execution policies: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies

---

## Summary of Decisions

| Area | Decision | Impact |
|------|----------|--------|
| Test Configuration | Pytest markers with platform detection | Enables selective test execution across platforms |
| PowerShell Testing | subprocess.run() with explicit encoding | Reliable script execution and output capture |
| Parity Testing | Normalize paths and line endings | Detect real bugs while ignoring cosmetic differences |
| CI/CD | GitHub Actions windows-latest runner | Free, pre-configured, representative environment |
| Edge Cases | Comprehensive coverage with explicit handling | Prevents production issues, better UX |

## Open Questions

None. All research areas resolved with clear implementation paths.

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create [data-model.md](data-model.md) for test data structures
- Create [contracts/test-api.md](contracts/test-api.md) for testing interfaces
- Create [quickstart.md](quickstart.md) for developer onboarding
