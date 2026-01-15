"""Data models for GitHub Copilot prompt synchronization."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class SyncStatusEnum(str, Enum):
    """Synchronization status between command and prompt."""

    SYNCHRONIZED = "synchronized"
    OUT_OF_SYNC = "out_of_sync"
    MISSING = "missing"


class OperationType(str, Enum):
    """Type of file operation during sync."""

    CREATED = "created"
    UPDATED = "updated"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class CommandTemplate:
    """Represents a doit command template file in .doit/templates/commands/."""

    name: str
    path: Path
    modified_at: datetime
    description: str = ""
    content: str = field(default="", repr=False)

    @property
    def prompt_filename(self) -> str:
        """Generate the corresponding prompt filename."""
        # doit.checkin.md -> doit.checkin.prompt.md
        return f"{self.name}.prompt.md"

    @classmethod
    def from_path(cls, path: Path) -> "CommandTemplate":
        """Create a CommandTemplate from a file path."""
        content = path.read_text(encoding="utf-8")
        modified_at = datetime.fromtimestamp(path.stat().st_mtime)

        # Extract name from filename: doit.checkin.md -> doit.checkin
        name = path.stem  # removes .md extension

        # Extract description from YAML frontmatter
        description = ""
        if content.startswith("---"):
            try:
                end_idx = content.index("---", 3)
                frontmatter = content[3:end_idx].strip()
                for line in frontmatter.split("\n"):
                    if line.startswith("description:"):
                        description = line.replace("description:", "").strip()
                        # Remove quotes if present
                        description = description.strip("\"'")
                        break
            except ValueError:
                pass  # No closing ---

        return cls(
            name=name,
            path=path,
            modified_at=modified_at,
            description=description,
            content=content,
        )


@dataclass
class PromptFile:
    """Represents a generated GitHub Copilot prompt file in .github/prompts/."""

    name: str
    path: Path
    generated_at: datetime
    content: str = field(default="", repr=False)

    @classmethod
    def from_path(cls, path: Path) -> "PromptFile":
        """Create a PromptFile from an existing file path."""
        content = path.read_text(encoding="utf-8")
        generated_at = datetime.fromtimestamp(path.stat().st_mtime)

        # Extract name from filename: doit.checkin.prompt.md -> doit.checkin.prompt
        name = path.name.replace(".md", "")

        return cls(
            name=name,
            path=path,
            generated_at=generated_at,
            content=content,
        )


@dataclass
class SyncStatus:
    """Represents the synchronization state between a command and its prompt."""

    command_name: str
    status: SyncStatusEnum
    checked_at: datetime
    reason: str = ""


@dataclass
class FileOperation:
    """Represents a single file operation during sync."""

    file_path: str
    operation_type: OperationType
    success: bool
    message: str = ""


@dataclass
class SyncResult:
    """Represents the result of a synchronization operation."""

    total_commands: int = 0
    synced: int = 0
    skipped: int = 0
    failed: int = 0
    operations: list[FileOperation] = field(default_factory=list)

    def add_operation(self, operation: FileOperation) -> None:
        """Add a file operation to the result."""
        self.operations.append(operation)
        if operation.operation_type == OperationType.CREATED:
            self.synced += 1
        elif operation.operation_type == OperationType.UPDATED:
            self.synced += 1
        elif operation.operation_type == OperationType.SKIPPED:
            self.skipped += 1
        elif operation.operation_type == OperationType.FAILED:
            self.failed += 1

    @property
    def success(self) -> bool:
        """Check if sync completed without failures."""
        return self.failed == 0
