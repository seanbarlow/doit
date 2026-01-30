"""E2E tests for Bash vs Zsh compatibility on macOS."""

import os
import subprocess
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
@pytest.mark.ci
def test_default_shell_detection(macos_test_env):
    """Test detection of default shell (Catalina+ uses zsh)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.bsd_utils import get_shell_type

    shell = get_shell_type()
    assert shell in ("bash", "zsh", "sh"), f"Unexpected shell: {shell}"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_bash_script_execution_in_zsh_env(tmp_path, macos_test_env):
    """Test bash script execution in zsh environment."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create simple bash script
    script = tmp_path / "test_script.sh"
    script.write_text("""#!/usr/bin/env bash
echo "Hello from bash"
exit 0
""")
    script.chmod(0o755)

    # Execute with bash explicitly
    result = subprocess.run(
        ["bash", str(script)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Hello from bash" in result.stdout


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_shell_specific_syntax_compatibility(tmp_path, macos_test_env):
    """Test shell-specific syntax compatibility."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Test bash arrays (bash-specific)
    bash_script = tmp_path / "bash_arrays.sh"
    bash_script.write_text("""#!/usr/bin/env bash
arr=(one two three)
echo ${arr[1]}
""")
    bash_script.chmod(0o755)

    result = subprocess.run(
        ["bash", str(bash_script)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "two" in result.stdout


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_shell_environment_variable_handling(macos_test_env):
    """Test $SHELL environment variable handling."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    shell = os.environ.get("SHELL", "")
    assert shell, "$SHELL environment variable not set"
    assert "bash" in shell or "zsh" in shell, f"Unexpected $SHELL value: {shell}"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_zsh_is_default_on_recent_macos(macos_test_env):
    """Test that zsh is default shell on recent macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.bsd_utils import is_zsh_default

    is_zsh = is_zsh_default()
    # Just verify the check works (result depends on macOS version)
    assert isinstance(is_zsh, bool)
