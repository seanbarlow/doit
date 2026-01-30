"""Template model representing a bundled command template."""

from dataclasses import dataclass, field
from pathlib import Path
import hashlib

from .agent import Agent


# List of all doit command names (without extension/prefix)
DOIT_COMMANDS = [
    "checkin",
    "constitution",
    "documentit",
    "fixit",
    "implementit",
    "planit",
    "researchit",
    "reviewit",
    "roadmapit",
    "scaffoldit",
    "specit",
    "taskit",
    "testit",
]


@dataclass
class Template:
    """Represents a bundled command template."""

    name: str
    agent: Agent
    source_path: Path
    content: str = field(default="", repr=False)

    @property
    def content_hash(self) -> str:
        """SHA-256 hash of template content (first 12 chars)."""
        return hashlib.sha256(self.content.encode()).hexdigest()[:12]

    @property
    def target_filename(self) -> str:
        """Filename for the generated command file."""
        if self.agent == Agent.CLAUDE:
            return f"doit.{self.name}.md"
        else:  # COPILOT
            return f"doit.{self.name}.prompt.md"

    @classmethod
    def from_file(cls, path: Path, agent: Agent) -> "Template":
        """Create a Template from a file path."""
        content = path.read_text(encoding="utf-8")

        # Extract command name from filename
        filename = path.name
        if agent == Agent.CLAUDE:
            # doit.specit.md -> specit
            name = filename.replace("doit.", "").replace(".md", "")
        else:  # COPILOT
            # doit.specit.prompt.md -> specit
            name = filename.replace("doit.", "").replace(".prompt.md", "")

        return cls(name=name, agent=agent, source_path=path, content=content)

    def matches_target(self, target_path: Path) -> bool:
        """Check if target file exists and matches this template's content."""
        if not target_path.exists():
            return False

        target_content = target_path.read_text(encoding="utf-8")
        target_hash = hashlib.sha256(target_content.encode()).hexdigest()[:12]
        return target_hash == self.content_hash


def get_required_templates() -> list[str]:
    """Return list of required template names."""
    return DOIT_COMMANDS.copy()
