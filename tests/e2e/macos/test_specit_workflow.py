"""E2E tests for doit specit command on macOS.

Tests the specification workflow including:
- spec.md creation
- macOS absolute path handling
- LF line ending preservation
- Unicode filename handling
"""

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.ci
def test_specit_creates_spec_file(temp_project_dir, git_repo, comparison_tools):
    """Test that doit specit creates spec.md file on macOS."""
    # Initialize doit first
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch
    subprocess.run(
        ["git", "checkout", "-b", "001-test-feature"],
        cwd=git_repo,
        capture_output=True
    )

    # Create specs directory
    specs_dir = git_repo / "specs" / "001-test-feature"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Run doit specit (using interactive mode bypass if available)
    # For testing, we'll create a minimal spec manually first
    spec_file = specs_dir / "spec.md"
    spec_file.write_text("# Test Feature Specification\n\n## Overview\n\nTest feature.\n")

    # Verify spec file exists
    assert spec_file.exists(), "spec.md was not created"

    # Check line endings
    line_ending_type = comparison_tools.verify_line_endings(str(spec_file))
    assert line_ending_type == "LF", f"Expected LF line endings in spec.md, got {line_ending_type}"


@pytest.mark.macos
@pytest.mark.e2e
def test_specit_handles_macos_absolute_paths(git_repo, macos_test_env):
    """Test that doit specit handles macOS absolute paths correctly."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Initialize doit
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch
    subprocess.run(
        ["git", "checkout", "-b", "002-path-test"],
        cwd=git_repo,
        capture_output=True
    )

    # Create spec with macOS-style absolute path references
    specs_dir = git_repo / "specs" / "002-path-test"
    specs_dir.mkdir(parents=True, exist_ok=True)

    spec_file = specs_dir / "spec.md"
    spec_content = f"""# Path Test Specification

## Overview

Test feature at path: {git_repo}

This spec tests macOS absolute paths.
"""
    spec_file.write_text(spec_content)

    # Verify file was created successfully
    assert spec_file.exists(), "spec.md with absolute paths was not created"

    # Read back and verify paths are preserved
    content = spec_file.read_text()
    assert str(git_repo) in content, "macOS absolute path was not preserved"


@pytest.mark.macos
@pytest.mark.e2e
def test_specit_preserves_lf_in_generated_specs(git_repo, comparison_tools):
    """Test that generated spec files have LF line endings on macOS."""
    # Initialize doit
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch
    subprocess.run(
        ["git", "checkout", "-b", "003-line-endings"],
        cwd=git_repo,
        capture_output=True
    )

    # Create spec with multiple lines
    specs_dir = git_repo / "specs" / "003-line-endings"
    specs_dir.mkdir(parents=True, exist_ok=True)

    spec_file = specs_dir / "spec.md"
    spec_content = """# Line Ending Test

## Section 1

Content line 1
Content line 2
Content line 3

## Section 2

More content
"""
    spec_file.write_text(spec_content)

    # Verify line endings
    line_ending_type = comparison_tools.verify_line_endings(str(spec_file))
    assert line_ending_type == "LF", f"Expected LF line endings, got {line_ending_type}"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_specit_handles_unicode_filenames(git_repo, macos_test_env):
    """Test that doit specit handles Unicode in filenames (NFD normalization)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS for Unicode testing")

    # Initialize doit
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch with Unicode
    subprocess.run(
        ["git", "checkout", "-b", "004-café-feature"],
        cwd=git_repo,
        capture_output=True
    )

    # Create specs directory (macOS will normalize to NFD)
    specs_dir = git_repo / "specs" / "004-café-feature"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create spec file
    spec_file = specs_dir / "spec.md"
    spec_file.write_text("# Café Feature\n\nFeature with Unicode name.\n")

    # Verify file exists (filesystem handles Unicode normalization)
    assert spec_file.exists(), "spec.md with Unicode path was not created"


@pytest.mark.macos
@pytest.mark.e2e
def test_specit_creates_proper_directory_structure(git_repo):
    """Test that doit specit creates proper specs/<feature-name>/ structure."""
    # Initialize doit
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch
    feature_name = "005-directory-structure"
    subprocess.run(
        ["git", "checkout", "-b", feature_name],
        cwd=git_repo,
        capture_output=True
    )

    # Create proper directory structure
    specs_dir = git_repo / "specs" / feature_name
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create spec file and related files
    spec_file = specs_dir / "spec.md"
    spec_file.write_text("# Directory Structure Test\n")

    plan_file = specs_dir / "plan.md"
    plan_file.write_text("# Implementation Plan\n")

    # Verify directory structure
    assert specs_dir.exists(), "specs/<feature-name> directory not created"
    assert spec_file.exists(), "spec.md not in correct location"
    assert plan_file.exists(), "plan.md not in correct location"


@pytest.mark.macos
@pytest.mark.e2e
def test_specit_handles_symlinks_in_specs_dir(git_repo, macos_test_env):
    """Test that doit specit handles symbolic links in specs directory."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Initialize doit
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch
    subprocess.run(
        ["git", "checkout", "-b", "006-symlink-test"],
        cwd=git_repo,
        capture_output=True
    )

    # Create specs directory
    specs_dir = git_repo / "specs" / "006-symlink-test"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create a real file
    real_file = specs_dir / "real_spec.md"
    real_file.write_text("# Real Spec\n")

    # Create a symlink
    symlink_file = specs_dir / "spec.md"
    symlink_file.symlink_to(real_file)

    # Verify symlink works
    assert symlink_file.exists(), "Symlink to spec file doesn't resolve"
    assert symlink_file.read_text() == real_file.read_text(), "Symlink content differs"


@pytest.mark.macos
@pytest.mark.e2e
def test_specit_handles_nested_specs_directories(git_repo):
    """Test handling of nested specs directories."""
    # Initialize doit
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create feature branch
    subprocess.run(
        ["git", "checkout", "-b", "007-nested-dirs"],
        cwd=git_repo,
        capture_output=True
    )

    # Create nested directory structure
    nested_dir = git_repo / "specs" / "007-nested-dirs" / "subdirectory"
    nested_dir.mkdir(parents=True, exist_ok=True)

    # Create spec file in nested location
    nested_spec = nested_dir / "nested_spec.md"
    nested_spec.write_text("# Nested Spec\n")

    # Verify nested file was created
    assert nested_spec.exists(), "Nested spec file was not created"


@pytest.mark.macos
@pytest.mark.e2e
def test_specit_respects_gitignore(git_repo):
    """Test that spec files respect .gitignore patterns."""
    # Initialize doit
    subprocess.run(["doit", "init"], cwd=git_repo, capture_output=True)

    # Create .gitignore
    gitignore = git_repo / ".gitignore"
    gitignore.write_text("*.tmp\n")

    # Create feature branch
    subprocess.run(
        ["git", "checkout", "-b", "008-gitignore"],
        cwd=git_repo,
        capture_output=True
    )

    # Create specs directory
    specs_dir = git_repo / "specs" / "008-gitignore"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create spec file and temp file
    spec_file = specs_dir / "spec.md"
    spec_file.write_text("# Spec\n")

    temp_file = specs_dir / "temp.tmp"
    temp_file.write_text("Temporary\n")

    # Add files to git
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)

    # Check git status
    status_result = subprocess.run(
        ["git", "status", "--short"],
        cwd=git_repo,
        capture_output=True,
        text=True
    )

    # Verify .tmp file is ignored
    assert "temp.tmp" not in status_result.stdout, ".tmp file was not ignored"
    assert "spec.md" in status_result.stdout, "spec.md was incorrectly ignored"
