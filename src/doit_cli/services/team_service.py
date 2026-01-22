"""Team management service.

This module provides the TeamService class for managing team
configuration, membership, and shared memory files.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from doit_cli.models.team_models import (
    SharedMemory,
    Team,
    TeamConfig,
    TeamMember,
    TeamPermission,
    TeamRole,
)
from doit_cli.services.git_utils import get_user_email
from doit_cli.services.team_config import (
    TeamConfigError,
    TeamConfigValidationError,
    TeamNotInitializedError,
    create_initial_config,
    ensure_state_directory,
    get_large_files_warning,
    is_valid_email,
    load_team_config,
    save_team_config,
    team_exists,
)


class MemberNotFoundError(TeamConfigError):
    """Team member not found."""

    pass


class MemberAlreadyExistsError(TeamConfigError):
    """Team member already exists."""

    pass


class PermissionDeniedError(TeamConfigError):
    """User lacks permission for operation."""

    pass


class TeamService:
    """Manages team configuration and membership.

    This service provides methods for:
    - Initializing team collaboration
    - Managing team members (add, remove, update)
    - Checking permissions
    - Managing shared memory files
    """

    def __init__(self, project_root: Path = None):
        """Initialize TeamService.

        Args:
            project_root: Project root directory. Defaults to cwd.
        """
        self.project_root = project_root or Path.cwd()
        self._config: Optional[TeamConfig] = None

    @property
    def config(self) -> TeamConfig:
        """Get the team configuration, loading if needed."""
        if self._config is None:
            self._config = load_team_config(self.project_root)
        return self._config

    def _save_config(self) -> None:
        """Save current configuration and update timestamp."""
        if self._config:
            self._config.team.updated_at = datetime.now()
            save_team_config(self._config, self.project_root)

    def is_initialized(self) -> bool:
        """Check if team collaboration is initialized."""
        return team_exists(self.project_root)

    def init_team(
        self,
        name: str = None,
        owner_email: str = None,
    ) -> TeamConfig:
        """Initialize team collaboration for the project.

        Args:
            name: Team name. Defaults to project folder name.
            owner_email: Owner email. Defaults to git user.email.

        Returns:
            Created TeamConfig

        Raises:
            TeamConfigValidationError: If already initialized or invalid input
        """
        if self.is_initialized():
            raise TeamConfigValidationError(
                "Team collaboration already initialized. "
                "Delete .doit/config/team.yaml to reinitialize."
            )

        # Default name to project folder
        if not name:
            name = self.project_root.name

        # Default owner to git user email
        if not owner_email:
            owner_email = get_user_email(self.project_root)
            if not owner_email:
                raise TeamConfigValidationError(
                    "Could not determine owner email. "
                    "Please specify with --owner or configure git user.email"
                )

        # Create configuration
        config = create_initial_config(
            team_name=name,
            owner_email=owner_email,
            project_root=self.project_root,
        )

        # Save configuration
        save_team_config(config, self.project_root)

        # Create state directory
        ensure_state_directory(self.project_root)

        self._config = config
        return config

    def get_team(self) -> Team:
        """Get the team metadata."""
        return self.config.team

    def add_member(
        self,
        email: str,
        role: TeamRole = TeamRole.MEMBER,
        permission: TeamPermission = TeamPermission.READ_WRITE,
        notifications: bool = True,
        display_name: str = None,
    ) -> TeamMember:
        """Add a member to the team.

        Args:
            email: Member's email address
            role: Member role (owner/member)
            permission: Access level (read-write/read-only)
            notifications: Whether to enable notifications
            display_name: Optional display name

        Returns:
            Created TeamMember

        Raises:
            MemberAlreadyExistsError: If member already exists
            TeamConfigValidationError: If email is invalid
            PermissionDeniedError: If current user is not owner
        """
        if not is_valid_email(email):
            raise TeamConfigValidationError(f"Invalid email format: {email}")

        if self.config.has_member(email):
            raise MemberAlreadyExistsError(f"Member already exists: {email}")

        # Get current user for added_by field
        current_user = self.get_current_user_email()

        # Create member
        member = TeamMember.create(
            email=email,
            role=role,
            permission=permission,
            notifications=notifications,
            display_name=display_name,
            added_by=current_user or self.config.team.owner_id,
        )

        self._config.members.append(member)
        self._save_config()

        return member

    def remove_member(self, email: str) -> None:
        """Remove a member from the team.

        Args:
            email: Member's email to remove

        Raises:
            MemberNotFoundError: If member not found
            TeamConfigValidationError: If trying to remove last owner
        """
        member = self.config.get_member(email)
        if not member:
            raise MemberNotFoundError(f"Member not found: {email}")

        # Check if removing last owner
        if member.is_owner:
            owners = self.config.get_owners()
            if len(owners) <= 1:
                raise TeamConfigValidationError(
                    "Cannot remove the last owner. "
                    "Transfer ownership first or delete the team."
                )

        self._config.members = [m for m in self._config.members if m.id != email]
        self._save_config()

    def update_member(
        self,
        email: str,
        role: TeamRole = None,
        permission: TeamPermission = None,
        notifications: bool = None,
        display_name: str = None,
    ) -> TeamMember:
        """Update member settings.

        Args:
            email: Member's email
            role: New role (if changing)
            permission: New permission (if changing)
            notifications: New notification setting (if changing)
            display_name: New display name (if changing)

        Returns:
            Updated TeamMember

        Raises:
            MemberNotFoundError: If member not found
        """
        member = self.config.get_member(email)
        if not member:
            raise MemberNotFoundError(f"Member not found: {email}")

        # Check if removing last owner role
        if role and role != TeamRole.OWNER and member.is_owner:
            owners = self.config.get_owners()
            if len(owners) <= 1:
                raise TeamConfigValidationError(
                    "Cannot change role of last owner"
                )

        # Update fields
        if role is not None:
            member.role = role
        if permission is not None:
            member.permission = permission
        if notifications is not None:
            member.notifications = notifications
        if display_name is not None:
            member.display_name = display_name

        self._save_config()
        return member

    def list_members(self) -> list[TeamMember]:
        """List all team members."""
        return self.config.members.copy()

    def get_member(self, email: str) -> Optional[TeamMember]:
        """Get a specific member by email."""
        return self.config.get_member(email)

    def get_current_user_email(self) -> Optional[str]:
        """Get the current user's email from git config."""
        return get_user_email(self.project_root)

    def get_current_user(self) -> Optional[TeamMember]:
        """Get the current user's team membership.

        Returns:
            TeamMember if current user is a member, None otherwise
        """
        email = self.get_current_user_email()
        if email:
            return self.config.get_member(email)
        return None

    def is_current_user_owner(self) -> bool:
        """Check if current user has owner role."""
        member = self.get_current_user()
        return member is not None and member.is_owner

    def check_permission(self, action: str) -> bool:
        """Check if current user has permission for an action.

        Args:
            action: Action to check ("read", "write", "manage")

        Returns:
            True if permitted, False otherwise
        """
        member = self.get_current_user()
        if not member:
            return False

        if action == "read":
            return True  # All members can read

        if action == "write":
            return member.can_write

        if action == "manage":
            return member.is_owner

        return False

    def require_permission(self, action: str, error_message: str = None) -> None:
        """Require a permission, raising if not met.

        Args:
            action: Action to check
            error_message: Custom error message

        Raises:
            PermissionDeniedError: If permission not met
        """
        if not self.check_permission(action):
            raise PermissionDeniedError(
                error_message or f"Permission denied: {action} requires higher access"
            )

    # Shared memory management

    def get_shared_files(self) -> list[SharedMemory]:
        """Get list of shared memory files."""
        return self.config.shared_files.copy()

    def add_shared_file(self, path: str, modified_by: str = None) -> SharedMemory:
        """Add a file to shared memory.

        Args:
            path: Relative path from .doit/memory/
            modified_by: Email of modifier (defaults to current user)

        Returns:
            Created SharedMemory entry
        """
        # Check if already shared
        for sf in self.config.shared_files:
            if sf.path == path:
                return sf  # Already shared

        # Create entry
        shared = SharedMemory.create(
            path=path,
            modified_by=modified_by or self.get_current_user_email() or "",
        )

        self._config.shared_files.append(shared)
        self._save_config()

        return shared

    def remove_shared_file(self, path: str) -> None:
        """Remove a file from shared memory."""
        self._config.shared_files = [
            sf for sf in self._config.shared_files if sf.path != path
        ]
        self._save_config()

    def get_large_file_warnings(self) -> list[str]:
        """Get warnings for large shared files."""
        return get_large_files_warning(self.config, self.project_root)

    def reload_config(self) -> None:
        """Reload configuration from disk."""
        self._config = None
        _ = self.config  # Trigger reload
