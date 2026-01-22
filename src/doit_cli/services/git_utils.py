"""Git utilities for team collaboration synchronization.

This module provides wrapper functions for Git subprocess operations
used in team memory file synchronization.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class GitError(Exception):
    """Base exception for Git operations."""

    def __init__(self, message: str, returncode: int = None, stderr: str = None):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


class GitNotAvailableError(GitError):
    """Git is not available on the system."""

    pass


class GitNotARepoError(GitError):
    """Current directory is not a Git repository."""

    pass


class GitRemoteError(GitError):
    """Error with Git remote operations."""

    pass


class GitConflictError(GitError):
    """Git merge conflict detected."""

    def __init__(self, message: str, conflicting_files: list[str] = None):
        super().__init__(message)
        self.conflicting_files = conflicting_files or []


@dataclass
class GitStatus:
    """Represents the status of the Git repository."""

    is_clean: bool
    modified_files: list[str]
    untracked_files: list[str]
    staged_files: list[str]
    ahead: int = 0
    behind: int = 0
    current_branch: str = ""
    has_remote: bool = True


@dataclass
class GitCommandResult:
    """Result of a Git command execution."""

    success: bool
    stdout: str
    stderr: str
    returncode: int


def run_git_command(
    args: list[str],
    cwd: Path = None,
    capture_output: bool = True,
    check: bool = False,
) -> GitCommandResult:
    """Execute a Git command and return the result.

    Args:
        args: Git command arguments (without 'git' prefix)
        cwd: Working directory for the command
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise exception on non-zero return code

    Returns:
        GitCommandResult with command output

    Raises:
        GitError: If check=True and command fails
    """
    cmd = ["git"] + args

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=capture_output,
            text=True,
            timeout=60,  # 60 second timeout
        )

        cmd_result = GitCommandResult(
            success=result.returncode == 0,
            stdout=result.stdout.strip() if result.stdout else "",
            stderr=result.stderr.strip() if result.stderr else "",
            returncode=result.returncode,
        )

        if check and not cmd_result.success:
            raise GitError(
                f"Git command failed: {' '.join(cmd)}",
                returncode=result.returncode,
                stderr=cmd_result.stderr,
            )

        return cmd_result

    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out after 60 seconds")
    except FileNotFoundError:
        raise GitNotAvailableError(
            "Git is not installed or not available in PATH"
        )


def is_git_available() -> bool:
    """Check if Git is available on the system."""
    try:
        result = run_git_command(["--version"])
        return result.success
    except GitNotAvailableError:
        return False


def is_git_repo(path: Path = None) -> bool:
    """Check if the given path is a Git repository."""
    try:
        result = run_git_command(["rev-parse", "--git-dir"], cwd=path)
        return result.success
    except GitError:
        return False


def get_current_branch(cwd: Path = None) -> str:
    """Get the current Git branch name."""
    result = run_git_command(["branch", "--show-current"], cwd=cwd, check=True)
    return result.stdout


def get_remote_url(remote: str = "origin", cwd: Path = None) -> Optional[str]:
    """Get the URL of a Git remote."""
    result = run_git_command(["remote", "get-url", remote], cwd=cwd)
    return result.stdout if result.success else None


def has_remote(remote: str = "origin", cwd: Path = None) -> bool:
    """Check if a remote exists."""
    result = run_git_command(["remote", "get-url", remote], cwd=cwd)
    return result.success


def get_user_email(cwd: Path = None) -> Optional[str]:
    """Get the Git user email from configuration."""
    result = run_git_command(["config", "user.email"], cwd=cwd)
    return result.stdout if result.success else None


def get_user_name(cwd: Path = None) -> Optional[str]:
    """Get the Git user name from configuration."""
    result = run_git_command(["config", "user.name"], cwd=cwd)
    return result.stdout if result.success else None


def get_status(cwd: Path = None) -> GitStatus:
    """Get the current Git status.

    Returns:
        GitStatus object with repository state
    """
    # Get porcelain status
    result = run_git_command(["status", "--porcelain"], cwd=cwd, check=True)

    modified = []
    untracked = []
    staged = []

    for line in result.stdout.split("\n"):
        if not line:
            continue

        status = line[:2]
        filepath = line[3:]

        # Index status (first char)
        if status[0] in "MADRC":
            staged.append(filepath)

        # Working tree status (second char)
        if status[1] == "M":
            modified.append(filepath)
        elif status[1] == "?":
            untracked.append(filepath)

    # Check ahead/behind remote
    ahead = 0
    behind = 0
    branch = get_current_branch(cwd)

    if has_remote(cwd=cwd):
        rev_result = run_git_command(
            ["rev-list", "--left-right", "--count", f"HEAD...origin/{branch}"],
            cwd=cwd,
        )
        if rev_result.success and rev_result.stdout:
            parts = rev_result.stdout.split()
            if len(parts) == 2:
                ahead = int(parts[0])
                behind = int(parts[1])

    return GitStatus(
        is_clean=not (modified or untracked or staged),
        modified_files=modified,
        untracked_files=untracked,
        staged_files=staged,
        ahead=ahead,
        behind=behind,
        current_branch=branch,
        has_remote=has_remote(cwd=cwd),
    )


def fetch(remote: str = "origin", cwd: Path = None) -> GitCommandResult:
    """Fetch from remote repository."""
    return run_git_command(["fetch", remote], cwd=cwd, check=True)


def pull(
    remote: str = "origin",
    branch: str = None,
    cwd: Path = None,
    no_commit: bool = False,
) -> GitCommandResult:
    """Pull from remote repository.

    Args:
        remote: Remote name
        branch: Branch to pull (defaults to current branch)
        cwd: Working directory
        no_commit: If True, don't auto-commit merge

    Returns:
        GitCommandResult

    Raises:
        GitConflictError: If merge conflicts occur
    """
    args = ["pull", remote]
    if branch:
        args.append(branch)
    if no_commit:
        args.append("--no-commit")

    result = run_git_command(args, cwd=cwd)

    if not result.success:
        if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
            # Get conflicting files
            conflicts = get_conflicting_files(cwd)
            raise GitConflictError(
                "Merge conflict detected during pull",
                conflicting_files=conflicts,
            )
        raise GitError(
            f"Pull failed: {result.stderr}",
            returncode=result.returncode,
        )

    return result


def push(
    remote: str = "origin",
    branch: str = None,
    cwd: Path = None,
    set_upstream: bool = False,
) -> GitCommandResult:
    """Push to remote repository.

    Args:
        remote: Remote name
        branch: Branch to push (defaults to current branch)
        cwd: Working directory
        set_upstream: Whether to set upstream tracking

    Returns:
        GitCommandResult
    """
    args = ["push"]
    if set_upstream:
        args.extend(["-u", remote])
    else:
        args.append(remote)

    if branch:
        args.append(branch)

    return run_git_command(args, cwd=cwd, check=True)


def add(files: list[str], cwd: Path = None) -> GitCommandResult:
    """Stage files for commit.

    Args:
        files: List of file paths to stage
        cwd: Working directory

    Returns:
        GitCommandResult
    """
    return run_git_command(["add"] + files, cwd=cwd, check=True)


def commit(message: str, cwd: Path = None) -> GitCommandResult:
    """Create a commit with the given message.

    Args:
        message: Commit message
        cwd: Working directory

    Returns:
        GitCommandResult
    """
    return run_git_command(["commit", "-m", message], cwd=cwd, check=True)


def get_conflicting_files(cwd: Path = None) -> list[str]:
    """Get list of files with merge conflicts."""
    result = run_git_command(
        ["diff", "--name-only", "--diff-filter=U"],
        cwd=cwd,
    )
    if result.success and result.stdout:
        return result.stdout.split("\n")
    return []


def checkout_ours(files: list[str], cwd: Path = None) -> GitCommandResult:
    """Resolve conflicts by keeping local version."""
    return run_git_command(["checkout", "--ours"] + files, cwd=cwd, check=True)


def checkout_theirs(files: list[str], cwd: Path = None) -> GitCommandResult:
    """Resolve conflicts by keeping remote version."""
    return run_git_command(["checkout", "--theirs"] + files, cwd=cwd, check=True)


def get_file_at_ref(
    filepath: str,
    ref: str = "HEAD",
    cwd: Path = None,
) -> Optional[str]:
    """Get file content at a specific Git ref.

    Args:
        filepath: Path to the file
        ref: Git ref (commit, branch, HEAD, etc.)
        cwd: Working directory

    Returns:
        File content as string, or None if not found
    """
    result = run_git_command(["show", f"{ref}:{filepath}"], cwd=cwd)
    return result.stdout if result.success else None


def get_latest_commit_hash(ref: str = "HEAD", cwd: Path = None) -> Optional[str]:
    """Get the commit hash for a ref."""
    result = run_git_command(["rev-parse", ref], cwd=cwd)
    return result.stdout if result.success else None


def get_commit_message(commit_hash: str, cwd: Path = None) -> Optional[str]:
    """Get the commit message for a commit."""
    result = run_git_command(
        ["log", "-1", "--pretty=%B", commit_hash],
        cwd=cwd,
    )
    return result.stdout if result.success else None


def get_file_last_modified_by(filepath: str, cwd: Path = None) -> Optional[str]:
    """Get email of last person who modified a file."""
    result = run_git_command(
        ["log", "-1", "--pretty=%ae", "--", filepath],
        cwd=cwd,
    )
    return result.stdout if result.success else None


def abort_merge(cwd: Path = None) -> GitCommandResult:
    """Abort an in-progress merge."""
    return run_git_command(["merge", "--abort"], cwd=cwd)


def is_online(remote: str = "origin", cwd: Path = None) -> bool:
    """Check if remote is reachable.

    Uses git ls-remote with a timeout to check connectivity.
    """
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--exit-code", "-q", remote],
            cwd=cwd or Path.cwd(),
            capture_output=True,
            timeout=10,  # 10 second timeout for network check
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False
