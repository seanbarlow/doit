"""Pytest configuration and fixtures for macOS E2E tests."""

import os
import platform
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Import utility classes
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils" / "macos"))

from filesystem_utils import FilesystemValidator
from unicode_utils import test_unicode_sample_strings, create_nfd_filename, create_nfc_filename
from bsd_utils import BSDCommandWrapper
from xattr_utils import ExtendedAttributeHandler
from comparison_utils import ComparisonTools


@pytest.fixture(scope="session")
def macos_test_env() -> dict:
    """Provide macOS-specific test environment information.

    Returns:
        Dictionary with environment details
    """
    return {
        "is_macos": platform.system() == "Darwin",
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "home_dir": os.path.expanduser("~"),
        "tmpdir": tempfile.gettempdir(),
        "shell": os.environ.get("SHELL", ""),
    }


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary project directory for testing.

    Args:
        tmp_path: pytest's built-in tmp_path fixture

    Yields:
        Path to temporary project directory
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Change to project directory
    original_cwd = os.getcwd()
    os.chdir(project_dir)

    yield project_dir

    # Restore original working directory
    os.chdir(original_cwd)


@pytest.fixture
def case_sensitive_volume(macos_test_env: dict) -> dict:
    """Detect or provide information about case-sensitive volume testing.

    Note: Creating case-sensitive volumes requires admin privileges,
    so this fixture only detects the current volume's case-sensitivity.

    Args:
        macos_test_env: macOS environment fixture

    Returns:
        Dictionary with case-sensitivity information
    """
    if not macos_test_env["is_macos"]:
        return {
            "is_case_sensitive": True,  # Assume case-sensitive on non-macOS
            "can_test_case_sensitive": False,
            "filesystem_type": "unknown",
        }

    validator = FilesystemValidator()
    fs_type = validator.detect_volume_type()
    is_case_sensitive = validator.is_case_sensitive()

    return {
        "is_case_sensitive": is_case_sensitive,
        "can_test_case_sensitive": True,
        "filesystem_type": fs_type or "unknown",
        "apfs_features": validator.check_apfs_features() if fs_type == "apfs" else {},
    }


@pytest.fixture
def unicode_test_files(tmp_path: Path, macos_test_env: dict) -> dict:
    """Create test files with various Unicode normalizations.

    Args:
        tmp_path: pytest's built-in tmp_path fixture
        macos_test_env: macOS environment fixture

    Returns:
        Dictionary mapping test names to file paths
    """
    if not macos_test_env["is_macos"]:
        # On non-macOS, just create simple test files
        test_file = tmp_path / "test_unicode.txt"
        test_file.touch()
        return {"simple": str(test_file)}

    unicode_dir = tmp_path / "unicode_tests"
    unicode_dir.mkdir(exist_ok=True)

    test_files = {}
    samples = test_unicode_sample_strings()

    # Create files with NFD normalization (macOS default)
    for name, sample in samples.items():
        nfd_file = create_nfd_filename(str(unicode_dir), f"test_{name}_nfd.txt")
        test_files[f"{name}_nfd"] = str(nfd_file)

        # Also create NFC version for comparison
        nfc_file = create_nfc_filename(str(unicode_dir), f"test_{name}_nfc.txt")
        test_files[f"{name}_nfc"] = str(nfc_file)

    return test_files


@pytest.fixture
def bsd_command_wrapper(macos_test_env: dict) -> BSDCommandWrapper:
    """Provide BSD command wrapper for testing.

    Args:
        macos_test_env: macOS environment fixture

    Returns:
        BSDCommandWrapper instance
    """
    return BSDCommandWrapper()


@pytest.fixture
def xattr_handler(macos_test_env: dict) -> ExtendedAttributeHandler:
    """Provide extended attribute handler for testing.

    Args:
        macos_test_env: macOS environment fixture

    Returns:
        ExtendedAttributeHandler instance
    """
    return ExtendedAttributeHandler()


@pytest.fixture
def comparison_tools() -> ComparisonTools:
    """Provide comparison tools for cross-platform testing.

    Returns:
        ComparisonTools instance
    """
    return ComparisonTools()


@pytest.fixture
def sample_project_structure(tmp_path: Path) -> Path:
    """Create a sample project structure for testing doit commands.

    Args:
        tmp_path: pytest's built-in tmp_path fixture

    Returns:
        Path to sample project root
    """
    project_root = tmp_path / "sample_project"
    project_root.mkdir(exist_ok=True)

    # Create basic doit structure
    doit_dir = project_root / ".doit"
    doit_dir.mkdir(exist_ok=True)

    memory_dir = doit_dir / "memory"
    memory_dir.mkdir(exist_ok=True)

    templates_dir = doit_dir / "templates"
    templates_dir.mkdir(exist_ok=True)

    scripts_dir = doit_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Create specs directory
    specs_dir = project_root / "specs"
    specs_dir.mkdir(exist_ok=True)

    return project_root


@pytest.fixture
def git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary git repository for testing.

    Args:
        tmp_path: pytest's built-in tmp_path fixture

    Yields:
        Path to git repository root
    """
    repo_dir = tmp_path / "git_repo"
    repo_dir.mkdir(exist_ok=True)

    # Initialize git repo
    import subprocess
    original_cwd = os.getcwd()
    os.chdir(repo_dir)

    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)

        yield repo_dir

    finally:
        os.chdir(original_cwd)


@pytest.fixture
def macos_path_samples(macos_test_env: dict) -> dict:
    """Provide sample macOS-specific paths for testing.

    Args:
        macos_test_env: macOS environment fixture

    Returns:
        Dictionary of sample paths
    """
    if not macos_test_env["is_macos"]:
        return {}

    return {
        "home": os.path.expanduser("~"),
        "library": os.path.expanduser("~/Library"),
        "application_support": os.path.expanduser("~/Library/Application Support"),
        "tmpdir": tempfile.gettempdir(),
        "private_tmp": "/private/tmp",
        "applications": "/Applications",
        "volumes": "/Volumes",
    }


@pytest.fixture
def skip_if_not_macos(macos_test_env: dict):
    """Skip test if not running on macOS.

    Args:
        macos_test_env: macOS environment fixture
    """
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")


@pytest.fixture
def skip_if_not_case_sensitive(case_sensitive_volume: dict):
    """Skip test if filesystem is not case-sensitive.

    Args:
        case_sensitive_volume: case-sensitive volume fixture
    """
    if not case_sensitive_volume["is_case_sensitive"]:
        pytest.skip("Test requires case-sensitive filesystem")


@pytest.fixture
def skip_if_not_apfs(case_sensitive_volume: dict):
    """Skip test if filesystem is not APFS.

    Args:
        case_sensitive_volume: case-sensitive volume fixture
    """
    if case_sensitive_volume["filesystem_type"] != "apfs":
        pytest.skip("Test requires APFS filesystem")


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "macos: mark test as requiring macOS"
    )
    config.addinivalue_line(
        "markers", "filesystem: mark test as filesystem-specific"
    )
    config.addinivalue_line(
        "markers", "bsd: mark test as BSD utility compatibility test"
    )
    config.addinivalue_line(
        "markers", "unicode: mark test as Unicode handling test"
    )
    config.addinivalue_line(
        "markers", "case_sensitive: mark test as requiring case-sensitive filesystem"
    )
    config.addinivalue_line(
        "markers", "apfs: mark test as requiring APFS filesystem"
    )


# Auto-skip tests based on markers
def pytest_runtest_setup(item):
    """Auto-skip tests based on platform markers."""
    # Skip macOS tests on non-macOS platforms
    if "macos" in item.keywords:
        if platform.system() != "Darwin":
            pytest.skip("Test requires macOS")

    # Skip case-sensitive tests on case-insensitive filesystems
    if "case_sensitive" in item.keywords:
        validator = FilesystemValidator()
        if not validator.is_case_sensitive():
            pytest.skip("Test requires case-sensitive filesystem")

    # Skip APFS tests on non-APFS filesystems
    if "apfs" in item.keywords:
        validator = FilesystemValidator()
        if validator.detect_volume_type() != "apfs":
            pytest.skip("Test requires APFS filesystem")
