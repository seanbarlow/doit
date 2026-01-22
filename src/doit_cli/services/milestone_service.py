"""Milestone service for syncing roadmap priorities to GitHub milestones.

This service handles creating GitHub milestones for roadmap priorities (P1-P4),
assigning epics to their corresponding priority milestones, and managing milestone
lifecycle based on roadmap completion status.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from rich.console import Console

from ..models.milestone import Milestone
from ..models.priority import PRIORITIES, PRIORITY_LEVELS, get_priority
from ..models.sync_operation import (
    SyncOperation,
    SyncAction,
    SyncStatus,
)
from .github_service import GitHubService, GitHubServiceError


class MilestoneService:
    """Service for syncing roadmap priorities to GitHub milestones.

    This service orchestrates the creation of GitHub milestones from roadmap
    priorities and manages epic assignments to those milestones.
    """

    # Regex patterns from research.md
    PRIORITY_HEADER_RE = re.compile(r"^###\s+(P[1-4])")
    EPIC_REFERENCE_RE = re.compile(r"GitHub:\s*#(\d+)")
    CHECKBOX_RE = re.compile(r"^-\s+\[([ xX])\]")

    def __init__(self, github_service: GitHubService, dry_run: bool = False):
        """Initialize MilestoneService.

        Args:
            github_service: GitHubService instance for API operations
            dry_run: If True, preview changes without executing
        """
        self.github_service = github_service
        self.dry_run = dry_run
        self.console = Console()

        # Paths to roadmap files
        self.roadmap_path = Path(".doit/memory/roadmap.md")
        self.completed_roadmap_path = Path(".doit/memory/completed_roadmap.md")

    def detect_priority_sections(self) -> Dict[str, List[str]]:
        """Parse roadmap.md and identify P1-P4 priority sections.

        Returns:
            Dictionary mapping priority levels (P1-P4) to lists of roadmap items

        Raises:
            FileNotFoundError: If roadmap.md doesn't exist
        """
        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"Roadmap not found at {self.roadmap_path}")

        priority_sections: Dict[str, List[str]] = {level: [] for level in PRIORITY_LEVELS}
        current_priority: Optional[str] = None

        with open(self.roadmap_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()

                # Check for priority header
                match = self.PRIORITY_HEADER_RE.match(line)
                if match:
                    current_priority = match.group(1)
                    continue

                # If we're in a priority section and find an item
                if current_priority and line.strip().startswith("- "):
                    priority_sections[current_priority].append(line)

                # Reset current priority when we hit another section header
                if line.startswith("## ") or line.startswith("---"):
                    current_priority = None

        return priority_sections

    def create_missing_milestones(self, sync_op: SyncOperation) -> List[Milestone]:
        """Check existing milestones and create missing priority milestones.

        Args:
            sync_op: SyncOperation to track results

        Returns:
            List of all priority milestones (existing + newly created)

        Raises:
            GitHubServiceError: If GitHub API operations fail
        """
        # Get existing milestones
        existing_milestones = self.github_service.get_all_milestones(state="all")
        existing_titles = {ms.title for ms in existing_milestones}

        created_milestones = []
        all_milestones = list(existing_milestones)

        # Check each priority level
        for level in PRIORITY_LEVELS:
            priority = get_priority(level)
            expected_title = priority.milestone_title

            if expected_title in existing_titles:
                # Milestone already exists
                sync_op.add_result(
                    action=SyncAction.CREATE_MILESTONE,
                    target=expected_title,
                    status=SyncStatus.SKIPPED,
                    message=f"Milestone already exists"
                )
                self.console.print(f"  • [dim]{expected_title}[/dim] already exists")
            else:
                # Create milestone
                if self.dry_run:
                    sync_op.add_result(
                        action=SyncAction.CREATE_MILESTONE,
                        target=expected_title,
                        status=SyncStatus.SKIPPED,
                        message="Dry run - would create"
                    )
                    self.console.print(f"  ✓ [yellow]Would create:[/yellow] {expected_title}")
                else:
                    try:
                        milestone = self.github_service.create_milestone(
                            title=expected_title,
                            description=priority.milestone_description
                        )
                        created_milestones.append(milestone)
                        all_milestones.append(milestone)

                        sync_op.add_result(
                            action=SyncAction.CREATE_MILESTONE,
                            target=expected_title,
                            status=SyncStatus.SUCCESS,
                            message=f"Created milestone #{milestone.number}"
                        )
                        self.console.print(f"  ✓ [green]Created:[/green] {expected_title} (#{milestone.number})")
                    except GitHubServiceError as e:
                        sync_op.add_result(
                            action=SyncAction.CREATE_MILESTONE,
                            target=expected_title,
                            status=SyncStatus.ERROR,
                            message=str(e)
                        )
                        self.console.print(f"  ✗ [red]Error:[/red] Failed to create {expected_title}: {e}")

        return all_milestones

    def extract_epic_references(self) -> Dict[str, List[int]]:
        """Parse roadmap items and extract GitHub epic numbers by priority.

        Returns:
            Dictionary mapping priority levels to lists of epic numbers

        Raises:
            FileNotFoundError: If roadmap.md doesn't exist
        """
        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"Roadmap not found at {self.roadmap_path}")

        epic_by_priority: Dict[str, List[int]] = {level: [] for level in PRIORITY_LEVELS}
        current_priority: Optional[str] = None

        with open(self.roadmap_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()

                # Check for priority header
                match = self.PRIORITY_HEADER_RE.match(line)
                if match:
                    current_priority = match.group(1)
                    continue

                # If we're in a priority section, look for epic references
                if current_priority:
                    epic_match = self.EPIC_REFERENCE_RE.search(line)
                    if epic_match:
                        epic_number = int(epic_match.group(1))
                        epic_by_priority[current_priority].append(epic_number)

                # Reset current priority when we hit another section header
                if line.startswith("## ") or line.startswith("---"):
                    current_priority = None

        return epic_by_priority

    def assign_epics_to_milestones(
        self,
        epic_by_priority: Dict[str, List[int]],
        milestones: List[Milestone],
        sync_op: SyncOperation
    ) -> None:
        """Assign each epic to its corresponding priority milestone.

        Args:
            epic_by_priority: Dictionary mapping priorities to epic numbers
            milestones: List of available milestones
            sync_op: SyncOperation to track results

        Raises:
            GitHubServiceError: If GitHub API operations fail
        """
        # Build milestone lookup by title
        milestone_by_title = {ms.title: ms for ms in milestones}

        # Process each priority
        for priority_level, epic_numbers in epic_by_priority.items():
            if not epic_numbers:
                continue

            priority = get_priority(priority_level)
            milestone_title = priority.milestone_title

            # Find the milestone
            if milestone_title not in milestone_by_title:
                self.console.print(
                    f"  ⚠️  [yellow]Warning:[/yellow] Milestone '{milestone_title}' not found, skipping epic assignment"
                )
                continue

            # Assign each epic to the milestone
            for epic_number in epic_numbers:
                try:
                    # Check existing assignment
                    previous_milestone = self.check_existing_assignment(epic_number)

                    if previous_milestone == milestone_title:
                        # Already assigned correctly
                        sync_op.add_result(
                            action=SyncAction.ASSIGN_EPIC,
                            target=f"#{epic_number}",
                            status=SyncStatus.SKIPPED,
                            message=f"Already assigned to {milestone_title}"
                        )
                        self.console.print(f"  • [dim]#{epic_number}[/dim] already in {milestone_title}")
                    else:
                        # Assign or reassign
                        if self.dry_run:
                            sync_op.add_result(
                                action=SyncAction.ASSIGN_EPIC,
                                target=f"#{epic_number}",
                                status=SyncStatus.SKIPPED,
                                message=f"Dry run - would assign to {milestone_title}"
                            )
                            if previous_milestone:
                                self.console.print(
                                    f"  ✓ [yellow]Would reassign:[/yellow] #{epic_number} "
                                    f"from '{previous_milestone}' to '{milestone_title}'"
                                )
                            else:
                                self.console.print(f"  ✓ [yellow]Would assign:[/yellow] #{epic_number} to {milestone_title}")
                        else:
                            self._assign_epic_to_milestone(epic_number, milestone_title)

                            sync_op.add_result(
                                action=SyncAction.ASSIGN_EPIC,
                                target=f"#{epic_number}",
                                status=SyncStatus.SUCCESS,
                                message=f"Assigned to {milestone_title}"
                            )

                            if previous_milestone:
                                self.console.print(
                                    f"  ✓ [green]Reassigned:[/green] #{epic_number} "
                                    f"from '{previous_milestone}' to '{milestone_title}'"
                                )
                            else:
                                self.console.print(f"  ✓ [green]Assigned:[/green] #{epic_number} to {milestone_title}")

                except GitHubServiceError as e:
                    sync_op.add_result(
                        action=SyncAction.ASSIGN_EPIC,
                        target=f"#{epic_number}",
                        status=SyncStatus.ERROR,
                        message=str(e)
                    )
                    self.console.print(f"  ✗ [red]Error:[/red] Failed to assign #{epic_number}: {e}")

    def check_existing_assignment(self, epic_number: int) -> Optional[str]:
        """Check if epic is already assigned to a milestone.

        Args:
            epic_number: GitHub issue number

        Returns:
            Milestone title if assigned, None otherwise
        """
        try:
            import subprocess
            import json

            result = subprocess.run(
                ["gh", "issue", "view", str(epic_number), "--json", "milestone"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get("milestone"):
                    return data["milestone"]["title"]

            return None

        except Exception:
            # If we can't check, assume not assigned
            return None

    def _assign_epic_to_milestone(self, epic_number: int, milestone_title: str) -> None:
        """Assign epic to milestone using gh CLI.

        Args:
            epic_number: GitHub issue number
            milestone_title: Milestone title to assign to

        Raises:
            GitHubServiceError: If assignment fails
        """
        import subprocess

        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "edit",
                    str(epic_number),
                    "--milestone",
                    milestone_title,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                raise GitHubServiceError(f"Failed to assign epic: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise GitHubServiceError("GitHub CLI timeout")
        except Exception as e:
            raise GitHubServiceError(f"Failed to assign epic: {e}")

    def detect_completed_priorities(self) -> List[str]:
        """Check roadmap.md and completed_roadmap.md for empty priority sections.

        Returns:
            List of priority levels (e.g., ["P1", "P2"]) that are fully completed
        """
        completed_priorities = []

        # Get active items per priority
        priority_sections = self.detect_priority_sections()

        # Check each priority
        for level in PRIORITY_LEVELS:
            items = priority_sections.get(level, [])

            # Count uncompleted items (checkbox not marked)
            uncompleted = sum(
                1 for item in items
                if self.CHECKBOX_RE.match(item) and self.CHECKBOX_RE.match(item).group(1) == " "
            )

            # If no uncompleted items in active roadmap, check completed roadmap
            if uncompleted == 0 and len(items) > 0:
                # Priority section exists but all items are completed
                # Verify items exist in completed_roadmap.md
                if self._priority_in_completed_roadmap(level):
                    completed_priorities.append(level)

        return completed_priorities

    def _priority_in_completed_roadmap(self, priority_level: str) -> bool:
        """Check if a priority level has items in completed_roadmap.md.

        Args:
            priority_level: Priority level to check (e.g., "P1")

        Returns:
            True if items found in completed roadmap, False otherwise
        """
        if not self.completed_roadmap_path.exists():
            return False

        try:
            with open(self.completed_roadmap_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Look for priority label in completed roadmap
                # Format: "| Item | P2 | 2026-01-21 | ..."
                return f"| {priority_level} |" in content or f"({priority_level})" in content
        except Exception:
            return False

    def prompt_close_milestone(self, priority_level: str) -> bool:
        """Prompt user for confirmation before closing a milestone.

        Args:
            priority_level: Priority level (e.g., "P1")

        Returns:
            True if user confirms, False otherwise
        """
        from rich.prompt import Confirm

        priority = get_priority(priority_level)
        milestone_title = priority.milestone_title

        message = f"All {priority_level} items completed. Close milestone '{milestone_title}'?"
        return Confirm.ask(message, default=False)
