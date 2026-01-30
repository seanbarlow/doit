"""E2E tests for macOS environment variables and paths."""

import os
import tempfile
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_macos_tmpdir_structure(macos_test_env):
    """Test macOS TMPDIR structure."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    tmpdir = tempfile.gettempdir()
    assert tmpdir, "TMPDIR not available"
    assert os.path.exists(tmpdir), f"TMPDIR {tmpdir} doesn't exist"

    # macOS TMPDIR is typically in /var/folders/ or /private/tmp
    assert "/var" in tmpdir or "/tmp" in tmpdir


@pytest.mark.macos
@pytest.mark.e2e
def test_home_directory_path_handling(macos_test_env, macos_path_samples):
    """Test HOME directory path handling."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    home_dir = os.path.expanduser("~")
    assert home_dir, "HOME directory not found"
    assert os.path.exists(home_dir), f"HOME {home_dir} doesn't exist"

    # Verify HOME environment variable
    env_home = os.environ.get("HOME", "")
    assert env_home == home_dir


@pytest.mark.macos
@pytest.mark.e2e
def test_path_environment_variable(macos_test_env):
    """Test PATH environment variable."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    path = os.environ.get("PATH", "")
    assert path, "PATH environment variable not set"

    # Common macOS paths
    path_components = path.split(":")
    assert any("/usr/bin" in p for p in path_components)
    assert any("/bin" in p for p in path_components)


@pytest.mark.macos
@pytest.mark.e2e
def test_dyld_environment_variables(macos_test_env):
    """Test DYLD_* environment variables."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Check for common DYLD variables (may not be set)
    dyld_vars = [
        "DYLD_LIBRARY_PATH",
        "DYLD_FRAMEWORK_PATH",
        "DYLD_INSERT_LIBRARIES",
    ]

    # Just verify we can check for them
    for var in dyld_vars:
        value = os.environ.get(var)
        # Variable may or may not be set
        assert value is None or isinstance(value, str)


@pytest.mark.macos
@pytest.mark.e2e
def test_term_and_shell_configuration(macos_test_env):
    """Test TERM and shell configuration variables."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Check TERM
    term = os.environ.get("TERM", "")
    # TERM should be set in interactive shells
    assert term is not None  # May be empty in non-interactive

    # Check SHELL
    shell = os.environ.get("SHELL", "")
    assert shell, "SHELL not set"
    assert os.path.exists(shell), f"SHELL path {shell} doesn't exist"


@pytest.mark.macos
@pytest.mark.e2e
def test_lang_and_locale_settings(macos_test_env):
    """Test LANG and locale environment variables."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    lang = os.environ.get("LANG", "")
    # LANG may or may not be set, but if it is, should be valid
    if lang:
        assert "UTF-8" in lang or "utf8" in lang.lower(), \
            f"Unexpected LANG encoding: {lang}"
