"""Spec file parser for reading and updating YAML frontmatter.

This module provides utilities for parsing spec files, extracting frontmatter metadata,
and atomically updating frontmatter fields while preserving file content.
"""

import re
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple


class SpecFrontmatter:
    """Represents parsed YAML frontmatter from a spec file."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize frontmatter from parsed YAML data.

        Args:
            data: Dictionary of frontmatter fields
        """
        self.data = data
        self.feature_name = data.get("Feature", "")
        self.branch_name = data.get("Branch", "")
        self.created_date = data.get("Created", "")
        self.status = data.get("Status", "")
        self.epic_number = self._extract_epic_number(data.get("Epic"))
        self.epic_url = data.get("Epic URL")
        self.priority = data.get("Priority")

    @staticmethod
    def _extract_epic_number(epic_field: str | None) -> int | None:
        """Extract epic number from Epic field.

        The Epic field can be:
        - A markdown link: "[#123](url)"
        - Just a number: "#123" or "123"
        - None if not present

        Args:
            epic_field: Value of the Epic field

        Returns:
            Epic number as integer, or None
        """
        if not epic_field:
            return None

        # Extract from markdown link: [#123](url)
        if "[#" in epic_field and "](" in epic_field:
            try:
                start = epic_field.index("[#") + 2
                end = epic_field.index("]", start)
                return int(epic_field[start:end])
            except (ValueError, IndexError):
                return None

        # Extract from plain number: #123 or 123
        epic_str = epic_field.strip().lstrip("#")
        try:
            return int(epic_str)
        except ValueError:
            return None

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert frontmatter to YAML-compatible dictionary.

        Returns:
            Dictionary ready for YAML serialization
        """
        result = dict(self.data)  # Preserve all existing fields

        # Update known fields
        if self.feature_name:
            result["Feature"] = self.feature_name
        if self.branch_name:
            result["Branch"] = self.branch_name
        if self.created_date:
            result["Created"] = self.created_date
        if self.status:
            result["Status"] = self.status

        # Handle epic fields
        if self.epic_number and self.epic_url:
            result["Epic"] = f"[#{self.epic_number}]({self.epic_url})"
            result["Epic URL"] = self.epic_url
        elif "Epic" in result:
            # Remove epic fields if they were cleared
            if self.epic_number is None:
                result.pop("Epic", None)
                result.pop("Epic URL", None)

        # Handle priority
        if self.priority:
            result["Priority"] = self.priority
        elif self.priority is None and "Priority" in result:
            result.pop("Priority", None)

        return result


def parse_spec_file(spec_path: Path) -> Tuple[SpecFrontmatter, str]:
    """Parse spec file into frontmatter and content.

    Args:
        spec_path: Path to spec.md file

    Returns:
        Tuple of (SpecFrontmatter, content)

    Raises:
        FileNotFoundError: If spec file doesn't exist
        ValueError: If frontmatter is malformed
    """
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")

    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter (between --- markers)
    if not content.startswith("---"):
        raise ValueError(f"Spec file missing frontmatter: {spec_path}")

    try:
        # Find end of frontmatter
        end_marker = content.index("---", 3)
        frontmatter_text = content[3:end_marker].strip()
        body = content[end_marker + 3:].lstrip("\n")

        # Parse YAML
        frontmatter_data = yaml.safe_load(frontmatter_text) or {}
        frontmatter = SpecFrontmatter(frontmatter_data)

        return (frontmatter, body)

    except (ValueError, yaml.YAMLError) as e:
        raise ValueError(f"Malformed frontmatter in {spec_path}: {e}")


def update_spec_frontmatter(
    spec_path: Path,
    updates: Dict[str, Any]
) -> None:
    """Update specific fields in spec frontmatter.

    This method atomically updates the spec file by:
    1. Reading current content
    2. Parsing frontmatter
    3. Applying updates
    4. Writing to temp file
    5. Atomic rename to original path

    Args:
        spec_path: Path to spec.md file
        updates: Dictionary of fields to update

    Raises:
        FileNotFoundError: If spec file doesn't exist
        ValueError: If frontmatter is malformed
    """
    # Parse current spec
    frontmatter, body = parse_spec_file(spec_path)

    # Apply updates
    for key, value in updates.items():
        # Special handling for Epic field - parse to extract number
        if key == "Epic" and value:
            # Extract epic number from markdown link format: [#123](url)
            epic_match = re.search(r"\[#(\d+)\]", str(value))
            if epic_match:
                frontmatter.epic_number = int(epic_match.group(1))
            frontmatter.data[key] = value
        # Standard attribute mapping
        elif hasattr(frontmatter, key.lower().replace(" ", "_")):
            setattr(frontmatter, key.lower().replace(" ", "_"), value)
            frontmatter.data[key] = value
        else:
            # Just update data dict for unknown fields
            frontmatter.data[key] = value

    # Write atomically
    write_spec_file(spec_path, frontmatter, body)


def add_epic_reference(
    spec_path: Path,
    epic_number: int,
    epic_url: str,
    priority: str | None = None
) -> None:
    """Add or update epic reference in spec frontmatter.

    Args:
        spec_path: Path to spec.md file
        epic_number: GitHub issue number
        epic_url: Full GitHub issue URL
        priority: Optional priority (P1, P2, P3, P4)

    Raises:
        FileNotFoundError: If spec file doesn't exist
        ValueError: If epic data is invalid
    """
    if epic_number <= 0:
        raise ValueError(f"Invalid epic number: {epic_number}")
    if not epic_url or not epic_url.startswith("http"):
        raise ValueError(f"Invalid epic URL: {epic_url}")

    updates = {
        "Epic": f"[#{epic_number}]({epic_url})",
        "Epic URL": epic_url
    }

    if priority:
        if priority not in ["P1", "P2", "P3", "P4"]:
            raise ValueError(f"Invalid priority: {priority}")
        updates["Priority"] = priority

    update_spec_frontmatter(spec_path, updates)


def remove_epic_reference(spec_path: Path) -> None:
    """Remove epic reference from spec frontmatter.

    Args:
        spec_path: Path to spec.md file

    Raises:
        FileNotFoundError: If spec file doesn't exist
    """
    frontmatter, body = parse_spec_file(spec_path)

    # Clear epic fields
    frontmatter.epic_number = None
    frontmatter.epic_url = None
    frontmatter.data.pop("Epic", None)
    frontmatter.data.pop("Epic URL", None)

    write_spec_file(spec_path, frontmatter, body)


def get_epic_reference(spec_path: Path) -> Tuple[int, str] | None:
    """Extract epic reference from spec frontmatter.

    Args:
        spec_path: Path to spec.md file

    Returns:
        Tuple of (epic_number, epic_url) if present, None otherwise

    Raises:
        FileNotFoundError: If spec file doesn't exist
    """
    frontmatter, _ = parse_spec_file(spec_path)

    if frontmatter.epic_number and frontmatter.epic_url:
        return (frontmatter.epic_number, frontmatter.epic_url)
    return None


def write_spec_file(
    spec_path: Path,
    frontmatter: SpecFrontmatter,
    content: str
) -> None:
    """Write spec file with frontmatter and content atomically.

    Uses atomic file operations (write to temp + rename) to prevent
    corruption if process is interrupted.

    Args:
        spec_path: Path to spec.md file
        frontmatter: Frontmatter data
        content: Markdown content (after frontmatter)

    Raises:
        OSError: If file write fails
    """
    # Serialize frontmatter to YAML
    frontmatter_dict = frontmatter.to_yaml_dict()
    frontmatter_yaml = yaml.dump(
        frontmatter_dict,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )

    # Construct full file content
    full_content = f"---\n{frontmatter_yaml}---\n\n{content}"

    # Write atomically using temp file + rename
    spec_dir = spec_path.parent
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=spec_dir,
        delete=False,
        suffix=".tmp"
    ) as tmp:
        tmp.write(full_content)
        tmp_path = Path(tmp.name)

    # Atomic rename
    tmp_path.replace(spec_path)
