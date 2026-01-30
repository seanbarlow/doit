"""E2E tests for doit bash script compatibility on macOS."""

import subprocess
from pathlib import Path
import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
@pytest.mark.ci
def test_setup_plan_script_on_macos(git_repo, macos_test_env):
    """Test setup-plan.sh script execution on macOS."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Check if setup-plan.sh exists in repo
    script_path = Path(".doit/scripts/bash/setup-plan.sh")
    repo_script = git_repo / script_path

    if not repo_script.exists():
        pytest.skip(f"Script not found: {script_path}")

    # Execute script
    result = subprocess.run(
        ["bash", str(repo_script), "--help"],
        cwd=git_repo,
        capture_output=True,
        text=True,
        timeout=10
    )

    # Script should at least respond to --help
    assert result.returncode in (0, 1), f"Script failed: {result.stderr}"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_bash_scripts_execute_without_errors(git_repo, macos_test_env):
    """Test that bash scripts execute without syntax errors."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Look for bash scripts in .doit/scripts/bash/
    scripts_dir = git_repo / ".doit" / "scripts" / "bash"

    if not scripts_dir.exists():
        pytest.skip("Scripts directory not found")

    # Test each .sh file with bash -n (syntax check)
    for script in scripts_dir.glob("*.sh"):
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0, \
            f"Syntax error in {script.name}: {result.stderr}"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_common_sh_script_execution(tmp_path, macos_test_env):
    """Test execution of common shell script patterns."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.bsd_utils import run_bash_script

    # Create test script with common patterns
    test_script = tmp_path / "common_patterns.sh"
    test_script.write_text("""#!/usr/bin/env bash
set -e

# Test variable expansion
VAR="test_value"
echo "Variable: $VAR"

# Test command substitution
RESULT=$(echo "command substitution")
echo "$RESULT"

# Test conditional
if [ -d "$HOME" ]; then
    echo "HOME exists"
fi

# Test function
test_func() {
    echo "Function works"
}
test_func

exit 0
""")
    test_script.chmod(0o755)

    # Run script
    success, stdout, stderr = run_bash_script(str(test_script))

    assert success, f"Script failed: {stderr}"
    assert "Variable: test_value" in stdout
    assert "command substitution" in stdout
    assert "HOME exists" in stdout
    assert "Function works" in stdout


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.bsd
def test_script_with_bsd_utilities(tmp_path, macos_test_env):
    """Test script using BSD utilities."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create script using BSD commands
    test_script = tmp_path / "bsd_script.sh"
    test_script.write_text("""#!/usr/bin/env bash
set -e

# Create test file
echo "test content" > /tmp/bsd_test.txt

# Use BSD sed (with required backup extension)
sed -i '' 's/test/modified/' /tmp/bsd_test.txt

# Use BSD grep
grep "modified" /tmp/bsd_test.txt

# Cleanup
rm -f /tmp/bsd_test.txt

exit 0
""")
    test_script.chmod(0o755)

    from tests.utils.macos.bsd_utils import run_bash_script
    success, stdout, stderr = run_bash_script(str(test_script))

    assert success, f"BSD script failed: {stderr}"
    assert "modified" in stdout
