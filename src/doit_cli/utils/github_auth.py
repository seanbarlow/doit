"""GitHub authentication and configuration detection utility.

This module provides functions to detect GitHub repository configuration and
verify that the GitHub CLI (gh) is available and authenticated.
"""

import shutil
import subprocess
from typing import Optional, Tuple


def has_github_remote() -> bool:
    """Check if the current directory is a git repository with a GitHub remote.

    Returns:
        True if a GitHub remote is configured, False otherwise

    Examples:
        >>> has_github_remote()  # In a GitHub repo
        True
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return False

        remote_url = result.stdout.strip()
        return "github.com" in remote_url
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def has_gh_cli() -> bool:
    """Check if GitHub CLI (gh) is installed and available.

    Returns:
        True if gh CLI is available in PATH, False otherwise

    Examples:
        >>> has_gh_cli()
        True  # If gh CLI is installed
    """
    return shutil.which("gh") is not None


def is_gh_authenticated() -> bool:
    """Check if GitHub CLI is authenticated.

    Returns:
        True if gh CLI is authenticated, False otherwise

    Examples:
        >>> is_gh_authenticated()
        True  # If gh auth login has been run successfully
    """
    if not has_gh_cli():
        return False

    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # gh auth status returns 0 if authenticated
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_github_config_status() -> Tuple[bool, str]:
    """Get comprehensive GitHub configuration status.

    Returns:
        Tuple of (is_configured, status_message) where is_configured indicates
        whether GitHub integration is fully available, and status_message
        provides details for debugging.

    Examples:
        >>> is_configured, message = get_github_config_status()
        >>> if is_configured:
        ...     print("GitHub integration available")
        ... else:
        ...     print(f"GitHub unavailable: {message}")
    """
    if not has_github_remote():
        return False, "No GitHub remote configured (origin must point to github.com)"

    if not has_gh_cli():
        return False, "GitHub CLI (gh) not installed - install from https://cli.github.com"

    if not is_gh_authenticated():
        return False, "GitHub CLI not authenticated - run: gh auth login"

    return True, "GitHub integration available"


def get_repository_name() -> Optional[str]:
    """Get the repository name from the GitHub remote URL.

    Returns:
        Repository name in format "owner/repo" or None if not available

    Examples:
        >>> get_repository_name()
        'seanbarlow/doit'
    """
    if not has_github_remote():
        return None

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None

        remote_url = result.stdout.strip()

        # Parse repository name from URL (handles both HTTPS and SSH)
        # HTTPS: https://github.com/owner/repo.git
        # SSH: git@github.com:owner/repo.git
        if "github.com/" in remote_url:
            parts = remote_url.split("github.com/")[1]
        elif "github.com:" in remote_url:
            parts = remote_url.split("github.com:")[1]
        else:
            return None

        # Remove .git suffix if present
        repo_name = parts.replace(".git", "")
        return repo_name

    except (subprocess.TimeoutExpired, FileNotFoundError, IndexError):
        return None
