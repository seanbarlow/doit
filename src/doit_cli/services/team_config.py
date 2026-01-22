"""Team configuration loader and validator.

This module handles loading, saving, and validating team.yaml configuration.
"""

import re
from pathlib import Path
from typing import Optional

import yaml

from doit_cli.models.team_models import (
    SharedMemory,
    Team,
    TeamConfig,
    TeamMember,
    TeamPermission,
    TeamRole,
)


class TeamConfigError(Exception):
    """Base exception for team configuration errors."""

    pass


class TeamNotInitializedError(TeamConfigError):
    """Team collaboration not initialized."""

    pass


class TeamConfigValidationError(TeamConfigError):
    """Team configuration validation failed."""

    def __init__(self, message: str, errors: list[str] = None):
        super().__init__(message)
        self.errors = errors or []


# Email validation regex (RFC 5322 simplified)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# File size limits
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
WARN_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1MB


def get_config_path(project_root: Path = None) -> Path:
    """Get the path to team.yaml configuration file."""
    root = project_root or Path.cwd()
    return root / ".doit" / "config" / "team.yaml"


def get_state_dir(project_root: Path = None) -> Path:
    """Get the path to team state directory."""
    root = project_root or Path.cwd()
    return root / ".doit" / "state"


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email))


def validate_team_config(config: TeamConfig) -> list[str]:
    """Validate team configuration and return list of errors.

    Returns:
        List of validation error messages. Empty list means valid.
    """
    errors = []

    # Validate team name
    if not config.team.name:
        errors.append("Team name is required")
    elif len(config.team.name) > 100:
        errors.append("Team name must be 1-100 characters")

    # Validate team owner
    if not config.team.owner_id:
        errors.append("Team owner is required")
    elif not is_valid_email(config.team.owner_id):
        errors.append(f"Invalid email format for team owner: {config.team.owner_id}")

    # Validate members
    if not config.members:
        errors.append("Team must have at least one member")
    else:
        # Check for at least one owner
        owners = [m for m in config.members if m.role == TeamRole.OWNER]
        if not owners:
            errors.append("Team must have at least one owner")

        # Check member emails
        seen_emails = set()
        for member in config.members:
            if not is_valid_email(member.id):
                errors.append(f"Invalid email format for member: {member.id}")
            if member.id in seen_emails:
                errors.append(f"Duplicate member email: {member.id}")
            seen_emails.add(member.id)

    # Validate shared files
    for sf in config.shared_files:
        if sf.path.startswith("/"):
            errors.append(f"Shared file path must be relative: {sf.path}")
        if sf.size_bytes > MAX_FILE_SIZE_BYTES:
            errors.append(f"File {sf.path} exceeds maximum size (10MB)")

    return errors


def load_team_config(project_root: Path = None) -> TeamConfig:
    """Load team configuration from team.yaml.

    Args:
        project_root: Project root directory. Defaults to current working directory.

    Returns:
        TeamConfig object

    Raises:
        TeamNotInitializedError: If team.yaml doesn't exist
        TeamConfigValidationError: If configuration is invalid
    """
    config_path = get_config_path(project_root)

    if not config_path.exists():
        raise TeamNotInitializedError(
            "Team collaboration not initialized. Run 'doit team init' first."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise TeamConfigValidationError(f"Invalid YAML in team.yaml: {e}")

    if not data:
        raise TeamConfigValidationError("team.yaml is empty")

    try:
        config = TeamConfig.from_dict(data)
    except (KeyError, ValueError) as e:
        raise TeamConfigValidationError(f"Invalid team configuration: {e}")

    # Validate configuration
    errors = validate_team_config(config)
    if errors:
        raise TeamConfigValidationError(
            "Team configuration validation failed",
            errors=errors,
        )

    return config


def save_team_config(config: TeamConfig, project_root: Path = None) -> None:
    """Save team configuration to team.yaml.

    Args:
        config: TeamConfig object to save
        project_root: Project root directory. Defaults to current working directory.

    Raises:
        TeamConfigValidationError: If configuration is invalid
    """
    # Validate before saving
    errors = validate_team_config(config)
    if errors:
        raise TeamConfigValidationError(
            "Cannot save invalid team configuration",
            errors=errors,
        )

    config_path = get_config_path(project_root)

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict and save
    data = config.to_dict()

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def team_exists(project_root: Path = None) -> bool:
    """Check if team.yaml exists."""
    return get_config_path(project_root).exists()


def create_initial_config(
    team_name: str,
    owner_email: str,
    project_root: Path = None,
) -> TeamConfig:
    """Create initial team configuration.

    Args:
        team_name: Name for the team
        owner_email: Email of the team owner
        project_root: Project root directory

    Returns:
        Created TeamConfig object
    """
    # Validate inputs
    if not is_valid_email(owner_email):
        raise TeamConfigValidationError(f"Invalid email format: {owner_email}")

    # Create team
    team = Team.create(name=team_name, owner_email=owner_email)

    # Create owner as first member
    owner_member = TeamMember.create(
        email=owner_email,
        role=TeamRole.OWNER,
        permission=TeamPermission.READ_WRITE,
        added_by=owner_email,
        notifications=True,
    )

    # Create default shared files
    shared_files = [
        SharedMemory.create(path=path, modified_by=owner_email)
        for path in SharedMemory.DEFAULT_FILES
    ]

    # Create config
    config = TeamConfig(
        team=team,
        members=[owner_member],
        shared_files=shared_files,
    )

    return config


def ensure_state_directory(project_root: Path = None) -> Path:
    """Ensure team state directory exists and return its path."""
    state_dir = get_state_dir(project_root)
    state_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (state_dir / "conflicts").mkdir(exist_ok=True)

    return state_dir


def get_large_files_warning(config: TeamConfig, project_root: Path = None) -> list[str]:
    """Check for large shared files and return warnings.

    Returns:
        List of warning messages for files > 1MB
    """
    warnings = []
    root = project_root or Path.cwd()

    for sf in config.shared_files:
        file_path = root / sf.full_path
        if file_path.exists():
            size = file_path.stat().st_size
            if size > WARN_FILE_SIZE_BYTES:
                size_mb = size / (1024 * 1024)
                warnings.append(
                    f"Warning: {sf.path} is {size_mb:.1f}MB. "
                    f"Consider reducing file size for faster sync."
                )

    return warnings
