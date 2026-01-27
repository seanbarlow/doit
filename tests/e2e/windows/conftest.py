"""Pytest configuration and fixtures for Windows E2E tests."""
import os
import sys
import subprocess
from pathlib import Path
from typing import Generator

import pytest

# Import utility classes
sys.path.insert(0, str(Path(__file__).parents[3]))
from tests.utils.windows.data_structures import TestEnvironment, PowerShellScriptResult
from tests.utils.windows.comparison_utils import ComparisonTools
from tests.utils.windows.path_utils import WindowsPathValidator


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "windows: tests that run only on Windows")
    config.addinivalue_line("markers", "unix: tests that run only on Unix-like systems")
    config.addinivalue_line("markers", "powershell: PowerShell script validation tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "slow: tests that take longer than 10 seconds")
    config.addinivalue_line("markers", "ci: tests that should run in CI")


@pytest.fixture(scope="session")
def windows_test_env(tmp_path_factory) -> TestEnvironment:
    """
    Create and configure test environment for Windows tests.

    Returns:
        TestEnvironment object with detected platform details
    """
    # Detect platform
    platform = sys.platform

    # Get PowerShell version
    try:
        ps_result = subprocess.run(
            ["pwsh", "-Command", "$PSVersionTable.PSVersion.ToString()"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        powershell_version = ps_result.stdout.strip() if ps_result.returncode == 0 else "unknown"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        powershell_version = "not available"

    # Get Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # Get Git version
    try:
        git_result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, timeout=5
        )
        git_version = git_result.stdout.strip() if git_result.returncode == 0 else "unknown"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        git_version = "not available"

    # Check if running in CI
    is_ci = os.getenv("CI", "false").lower() == "true" or os.getenv("GITHUB_ACTIONS") == "true"

    # Create temp directory for session
    temp_dir = tmp_path_factory.mktemp("windows_e2e_tests")

    # Detect line ending
    line_ending = "CRLF" if sys.platform == "win32" else "LF"

    return TestEnvironment(
        platform=platform,
        powershell_version=powershell_version,
        python_version=python_version,
        git_version=git_version,
        is_ci=is_ci,
        temp_dir=temp_dir,
        encoding="utf-8",
        line_ending=line_ending,
    )


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Create a temporary project directory for testing.

    Args:
        tmp_path: Pytest's tmp_path fixture

    Yields:
        Path object pointing to temporary directory

    Cleanup:
        Directory is deleted after test completes (unless test fails and artifact retention enabled)
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(parents=True, exist_ok=True)

    yield project_dir

    # Cleanup is automatic via tmp_path


@pytest.fixture(scope="session")
def powershell_executor():
    """
    Create PowerShell script executor.

    Returns:
        PowerShellExecutor instance (simplified version for this fixture)
    """

    class SimplePowerShellExecutor:
        """Simplified PowerShell executor for testing."""

        def __init__(self, timeout: int = 30):
            self.timeout = timeout

        def run_script(self, script_path: Path, *args, **kwargs) -> PowerShellScriptResult:
            """Execute a PowerShell script."""
            import time

            # Validate script exists
            script_path = Path(script_path)
            if not script_path.exists():
                raise FileNotFoundError(f"PowerShell script not found: {script_path}")

            cmd = ["pwsh", "-File", str(script_path)] + list(args)
            start_time = time.time()

            # Merge custom env with system environment
            env = kwargs.get("env", None)
            if env:
                import os
                merged_env = os.environ.copy()
                merged_env.update(env)
            else:
                merged_env = None

            # Get timeout from kwargs or use default
            exec_timeout = kwargs.get("timeout", self.timeout)

            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, encoding="utf-8", timeout=exec_timeout, env=merged_env
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
                    stdout=e.stdout if e.stdout else "",
                    stderr=f"Timeout after {exec_timeout}s",
                    execution_time=execution_time,
                    args=list(args),
                    environment_vars=env or {},
                )

        def check_execution_policy(self) -> str:
            """Get current PowerShell execution policy."""
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

        def validate_script_syntax(self, script_path: Path) -> tuple[bool, str]:
            """Validate PowerShell script syntax without executing it."""
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

    return SimplePowerShellExecutor()


@pytest.fixture(scope="session")
def comparison_tools() -> ComparisonTools:
    """
    Create output comparison utilities.

    Returns:
        ComparisonTools instance
    """
    return ComparisonTools()


@pytest.fixture(scope="session")
def path_validator() -> WindowsPathValidator:
    """
    Create Windows path validator.

    Returns:
        WindowsPathValidator instance
    """
    return WindowsPathValidator()


# ============================================================================
# Test Reporting Hooks for CI/CD Integration
# ============================================================================

def pytest_report_header(config):
    """
    Add Windows-specific platform information to test report header.

    This hook runs at the start of the test session and provides
    platform details in the test output.
    """
    import platform

    header_lines = [
        "",
        "=" * 70,
        "Windows E2E Test Environment",
        "=" * 70,
        f"Platform: {sys.platform}",
        f"OS: {platform.system()} {platform.release()} ({platform.version()})",
        f"Architecture: {platform.machine()}",
        f"Python: {sys.version.split()[0]}",
        f"CI Environment: {'Yes' if os.getenv('CI') else 'No'}",
    ]

    # Add PowerShell version if available
    try:
        ps_result = subprocess.run(
            ["pwsh", "-Command", "$PSVersionTable.PSVersion.ToString()"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if ps_result.returncode == 0:
            header_lines.append(f"PowerShell: {ps_result.stdout.strip()}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        header_lines.append("PowerShell: Not available")

    header_lines.append("=" * 70)
    header_lines.append("")

    return header_lines


def pytest_runtest_setup(item):
    """
    Add platform-specific markers and metadata before each test runs.

    This hook runs before each test item and can be used to add
    metadata or skip tests based on platform.
    """
    # Add platform info to test item
    item.user_properties.append(("platform", sys.platform))
    item.user_properties.append(("is_ci", os.getenv("CI", "false")))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Enhance test reports with Windows-specific diagnostics.

    This hook wraps around test execution and can add additional
    information to test reports, especially for failures.
    """
    import time
    import platform

    # Get the standard test report
    outcome = yield
    report = outcome.get_result()

    # Add execution time tracking
    if call.when == "call":
        item.user_properties.append(("duration", f"{call.duration:.3f}s"))

    # Add failure diagnostics for Windows
    if report.failed and call.when == "call":
        # Collect Windows-specific diagnostic information
        diagnostics = [
            "",
            "=" * 70,
            "Windows Test Failure Diagnostics",
            "=" * 70,
            f"Test: {item.nodeid}",
            f"Platform: {platform.system()} {platform.release()}",
            f"Python: {sys.version.split()[0]}",
            f"Working Directory: {os.getcwd()}",
            f"Temp Directory: {os.environ.get('TEMP', 'Not set')}",
        ]

        # Add PowerShell info for PowerShell-related tests
        if "powershell" in item.keywords:
            try:
                ps_result = subprocess.run(
                    ["pwsh", "-Command", "Get-ExecutionPolicy"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if ps_result.returncode == 0:
                    diagnostics.append(f"PowerShell Execution Policy: {ps_result.stdout.strip()}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                diagnostics.append("PowerShell: Not available or timed out")

        # Add path handling info for path-related tests
        if any(marker in item.keywords for marker in ["path", "windows_path"]):
            diagnostics.extend(
                [
                    f"Path Separator: {os.sep}",
                    f"Alternate Separator: {os.altsep}",
                    f"Line Separator: {repr(os.linesep)}",
                ]
            )

        diagnostics.append("=" * 70)
        diagnostics.append("")

        # Append diagnostics to report
        report.sections.append(("Windows Diagnostics", "\n".join(diagnostics)))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add Windows-specific summary information at the end of test run.

    This hook runs after all tests complete and adds a summary
    section to the terminal output.
    """
    # Check if we're in CI
    is_ci = os.getenv("CI", "false").lower() == "true"

    terminalreporter.write_sep("=", "Windows E2E Test Summary")

    # Platform information
    terminalreporter.write_line(f"Platform: {sys.platform}")
    terminalreporter.write_line(f"CI Environment: {'Yes' if is_ci else 'No'}")

    # Test statistics
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))
    total = passed + failed + skipped

    terminalreporter.write_line(f"Total Tests: {total}")
    terminalreporter.write_line(f"Passed: {passed}")
    terminalreporter.write_line(f"Failed: {failed}")
    terminalreporter.write_line(f"Skipped: {skipped}")

    # Add recommendations for CI
    if is_ci and failed > 0:
        terminalreporter.write_sep("!", "CI Failure Recommendations", red=True)
        terminalreporter.write_line(
            "Some tests failed in CI. Check the following:"
        )
        terminalreporter.write_line("- Review Windows Diagnostics sections above")
        terminalreporter.write_line("- Verify PowerShell 7.x is available")
        terminalreporter.write_line("- Check file permissions and paths")
        terminalreporter.write_line("- Ensure temp directories are accessible")


@pytest.fixture(autouse=True, scope="session")
def log_test_environment(request):
    """
    Log test environment details at the start of the session.

    This autouse fixture runs once per session and logs environment
    information that's useful for debugging test failures.
    """
    import platform

    print("\n" + "=" * 70)
    print("Test Environment Information")
    print("=" * 70)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python: {sys.version}")
    print(f"CI: {os.getenv('CI', 'false')}")
    print(f"GitHub Actions: {os.getenv('GITHUB_ACTIONS', 'false')}")
    print("=" * 70)
    print()
