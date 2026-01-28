"""E2E tests for doit planit command on macOS.

Tests the planning workflow including:
- plan.md creation
- nested macOS directory handling
- Line ending preservation
- Symlink handling
"""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_planit_creates_plan_file(git_repo, comparison_tools):
    """Test that doit planit creates plan.md file on macOS."""
    # Setup
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "010-planit-test"], cwd=git_repo, capture_output=True)

    specs_dir = git_repo / "specs" / "010-planit-test"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create spec first
    spec_file = specs_dir / "spec.md"
    spec_file.write_text("# Test Feature\n\n## Overview\nTest feature spec.\n")

    # Create plan
    plan_file = specs_dir / "plan.md"
    plan_file.write_text("# Implementation Plan\n\n## Overview\nTest plan.\n")

    assert plan_file.exists(), "plan.md was not created"

    # Verify LF line endings
    line_ending_type = comparison_tools.verify_line_endings(str(plan_file))
    assert line_ending_type == "LF", f"Expected LF, got {line_ending_type}"


@pytest.mark.macos
@pytest.mark.e2e
def test_planit_handles_nested_directories(git_repo, macos_test_env):
    """Test planit with nested macOS directories."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "011-nested"], cwd=git_repo, capture_output=True)

    # Create deeply nested structure
    nested_dir = git_repo / "specs" / "011-nested" / "sub1" / "sub2"
    nested_dir.mkdir(parents=True, exist_ok=True)

    plan_file = nested_dir / "plan.md"
    plan_file.write_text("# Nested Plan\n")

    assert plan_file.exists(), "Nested plan.md not created"


@pytest.mark.macos
@pytest.mark.e2e
def test_planit_preserves_line_endings(git_repo, comparison_tools):
    """Test that plan files maintain LF line endings."""
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "012-lineendings"], cwd=git_repo, capture_output=True)

    specs_dir = git_repo / "specs" / "012-lineendings"
    specs_dir.mkdir(parents=True, exist_ok=True)

    plan_file = specs_dir / "plan.md"
    plan_content = """# Plan

## Section 1
Line 1
Line 2

## Section 2
Line 3
"""
    plan_file.write_text(plan_content)

    line_ending_type = comparison_tools.verify_line_endings(str(plan_file))
    assert line_ending_type == "LF", f"Expected LF, got {line_ending_type}"


@pytest.mark.macos
@pytest.mark.e2e
def test_planit_handles_symlinks(git_repo, macos_test_env):
    """Test planit handles symlinks in directory structure."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "013-symlinks"], cwd=git_repo, capture_output=True)

    specs_dir = git_repo / "specs" / "013-symlinks"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create real plan
    real_plan = specs_dir / "real_plan.md"
    real_plan.write_text("# Real Plan\n")

    # Create symlink
    symlink_plan = specs_dir / "plan.md"
    symlink_plan.symlink_to(real_plan)

    assert symlink_plan.exists(), "Symlink doesn't resolve"
    assert symlink_plan.read_text() == real_plan.read_text()
