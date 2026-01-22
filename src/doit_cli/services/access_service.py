"""Access control service for team collaboration.

This module provides the AccessService class for managing
team member access levels and permission checks.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from doit_cli.models.team_models import TeamMember, TeamPermission, TeamRole
from doit_cli.services.git_utils import get_user_email
from doit_cli.services.team_config import (
    TeamNotInitializedError,
    load_team_config,
    team_exists,
)


class AccessAction(str, Enum):
    """Actions that can be checked for access."""

    READ = "read"
    WRITE = "write"
    PUSH = "push"
    PULL = "pull"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_SETTINGS = "manage_settings"
    DELETE_TEAM = "delete_team"


class AccessDeniedError(Exception):
    """Access denied for the requested action."""

    def __init__(self, action: str, required_permission: str = None, message: str = None):
        self.action = action
        self.required_permission = required_permission
        if message:
            super().__init__(message)
        else:
            super().__init__(
                f"Access denied for '{action}'. "
                f"Required: {required_permission or 'higher access level'}."
            )


@dataclass
class AccessContext:
    """Context for access checking with user and team info."""

    user_email: Optional[str]
    member: Optional[TeamMember]
    is_owner: bool
    can_write: bool

    @property
    def is_member(self) -> bool:
        """Check if user is a team member."""
        return self.member is not None

    @property
    def permission_level(self) -> str:
        """Get string description of permission level."""
        if not self.member:
            return "none"
        if self.is_owner:
            return "owner"
        if self.can_write:
            return "read-write"
        return "read-only"


class AccessService:
    """Manages access control for team operations.

    This service provides methods for:
    - Getting current user's access context
    - Checking permissions for specific actions
    - Enforcing permission requirements
    """

    # Map actions to required permission levels
    ACTION_REQUIREMENTS = {
        AccessAction.READ: "read",
        AccessAction.WRITE: "write",
        AccessAction.PUSH: "write",
        AccessAction.PULL: "read",
        AccessAction.MANAGE_MEMBERS: "owner",
        AccessAction.MANAGE_SETTINGS: "owner",
        AccessAction.DELETE_TEAM: "owner",
    }

    def __init__(self, project_root: Path = None):
        """Initialize AccessService.

        Args:
            project_root: Project root directory. Defaults to cwd.
        """
        self.project_root = project_root or Path.cwd()
        self._context: Optional[AccessContext] = None

    def is_team_initialized(self) -> bool:
        """Check if team collaboration is initialized."""
        return team_exists(self.project_root)

    def get_current_user_email(self) -> Optional[str]:
        """Get current user's email from Git config."""
        return get_user_email(self.project_root)

    def get_access_context(self, refresh: bool = False) -> AccessContext:
        """Get access context for current user.

        Args:
            refresh: Force refresh from disk

        Returns:
            AccessContext with user and permission info
        """
        if self._context is not None and not refresh:
            return self._context

        email = self.get_current_user_email()
        member = None
        is_owner = False
        can_write = False

        if email and self.is_team_initialized():
            try:
                config = load_team_config(self.project_root)
                member = config.get_member(email)
                if member:
                    is_owner = member.is_owner
                    can_write = member.can_write
            except TeamNotInitializedError:
                pass

        self._context = AccessContext(
            user_email=email,
            member=member,
            is_owner=is_owner,
            can_write=can_write,
        )
        return self._context

    def get_current_user(self) -> Optional[TeamMember]:
        """Get current user's team membership.

        Returns:
            TeamMember if user is a member, None otherwise
        """
        return self.get_access_context().member

    def can_perform(self, action: AccessAction) -> bool:
        """Check if current user can perform an action.

        Args:
            action: Action to check

        Returns:
            True if action is allowed
        """
        context = self.get_access_context()

        if not context.is_member:
            return False

        required = self.ACTION_REQUIREMENTS.get(action, "read")

        if required == "owner":
            return context.is_owner
        elif required == "write":
            return context.can_write
        else:
            return True  # read access for all members

    def require_permission(
        self,
        action: AccessAction,
        custom_message: str = None,
    ) -> None:
        """Require permission for an action.

        Args:
            action: Action to check
            custom_message: Custom error message

        Raises:
            AccessDeniedError: If permission denied
        """
        if not self.can_perform(action):
            required = self.ACTION_REQUIREMENTS.get(action, "unknown")
            raise AccessDeniedError(
                action=action.value,
                required_permission=required,
                message=custom_message,
            )

    def check_push_permission(self) -> bool:
        """Check if user can push changes.

        Returns:
            True if push is allowed
        """
        return self.can_perform(AccessAction.PUSH)

    def check_pull_permission(self) -> bool:
        """Check if user can pull changes.

        Returns:
            True if pull is allowed
        """
        return self.can_perform(AccessAction.PULL)

    def check_manage_permission(self) -> bool:
        """Check if user can manage team settings.

        Returns:
            True if management is allowed
        """
        return self.can_perform(AccessAction.MANAGE_SETTINGS)

    def require_push_permission(self) -> None:
        """Require push permission.

        Raises:
            AccessDeniedError: If not allowed to push
        """
        self.require_permission(
            AccessAction.PUSH,
            "You don't have permission to push changes. "
            "Contact the team owner to update your access level.",
        )

    def require_manage_permission(self) -> None:
        """Require management permission.

        Raises:
            AccessDeniedError: If not allowed to manage
        """
        self.require_permission(
            AccessAction.MANAGE_SETTINGS,
            "Only team owners can manage team settings.",
        )

    def get_permission_summary(self) -> dict:
        """Get summary of current user's permissions.

        Returns:
            Dictionary with permission details
        """
        context = self.get_access_context()

        return {
            "user_email": context.user_email,
            "is_member": context.is_member,
            "permission_level": context.permission_level,
            "actions": {
                action.value: self.can_perform(action)
                for action in AccessAction
            },
        }
