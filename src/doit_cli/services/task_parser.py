"""Parser for extracting tasks and cross-references from tasks.md files."""

import hashlib
import re
from pathlib import Path
from typing import Optional

from ..models.crossref_models import Task, TaskReference


class TaskParser:
    """Parses tasks.md files to extract tasks and their requirement references.

    This parser extracts task items with checkbox format and identifies
    [FR-XXX] cross-references within task descriptions.
    """

    # Pattern to match task lines: - [ ] or - [x] or - [X] followed by description
    # Captures: group(1) = checkbox state (space, x, or X), group(2) = description
    TASK_PATTERN = re.compile(
        r"^\s*-\s*\[(?P<state>[ xX])\]\s*(?P<description>.+)$",
        re.MULTILINE,
    )

    # Pattern to extract [FR-XXX] or [FR-001, FR-002] references
    # Matches single or comma-separated FR references
    REFERENCE_PATTERN = re.compile(
        r"\[(?P<refs>FR-\d{3}(?:,\s*FR-\d{3})*)\]"
    )

    # Pattern to extract individual FR-XXX from comma-separated list
    FR_PATTERN = re.compile(r"FR-\d{3}")

    def __init__(self, tasks_path: Optional[Path] = None) -> None:
        """Initialize parser with optional tasks file path.

        Args:
            tasks_path: Path to tasks.md file. Can be set later via parse().
        """
        self.tasks_path = tasks_path

    def parse(self, tasks_path: Optional[Path] = None) -> list[Task]:
        """Parse tasks.md and extract all tasks with their references.

        Args:
            tasks_path: Path to tasks.md file. Overrides constructor path.

        Returns:
            List of Task objects in file order.

        Raises:
            FileNotFoundError: If tasks file doesn't exist.
            ValueError: If no tasks path provided.
        """
        path = tasks_path or self.tasks_path
        if path is None:
            raise ValueError("No tasks path provided")

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Tasks file not found: {path}")

        content = path.read_text(encoding="utf-8")
        return self.parse_content(content, str(path))

    def parse_content(self, content: str, tasks_file: str) -> list[Task]:
        """Parse content string and extract tasks.

        Args:
            content: Full content of tasks.md file.
            tasks_file: Path to associate with extracted tasks.

        Returns:
            List of Task objects in file order.
        """
        tasks: list[Task] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            match = self.TASK_PATTERN.match(line)
            if match:
                state = match.group("state")
                description = match.group("description").strip()
                completed = state.lower() == "x"

                # Extract FR references from description
                references = self._extract_references(description)

                # Generate unique ID from normalized description
                task_id = self._generate_task_id(description)

                task = Task(
                    id=task_id,
                    tasks_file=tasks_file,
                    description=self._clean_description(description),
                    completed=completed,
                    line_number=line_num,
                    references=references,
                )
                tasks.append(task)

        return tasks

    def _extract_references(self, description: str) -> list[TaskReference]:
        """Extract FR-XXX references from task description.

        Handles both single references [FR-001] and multiple [FR-001, FR-003].

        Args:
            description: Task description text.

        Returns:
            List of TaskReference objects in order found.
        """
        references: list[TaskReference] = []
        position = 0

        # Find all reference patterns in the description
        for match in self.REFERENCE_PATTERN.finditer(description):
            refs_str = match.group("refs")
            # Extract individual FR-XXX IDs
            for fr_match in self.FR_PATTERN.finditer(refs_str):
                ref = TaskReference(
                    requirement_id=fr_match.group(),
                    position=position,
                )
                references.append(ref)
                position += 1

        return references

    def _clean_description(self, description: str) -> str:
        """Remove FR reference brackets from description for clean display.

        Args:
            description: Raw task description with [FR-XXX] references.

        Returns:
            Description with [FR-XXX] patterns removed.
        """
        # Remove [FR-XXX] or [FR-001, FR-002] patterns
        cleaned = self.REFERENCE_PATTERN.sub("", description)
        # Clean up extra whitespace
        return " ".join(cleaned.split()).strip()

    def _generate_task_id(self, description: str) -> str:
        """Generate unique ID from task description.

        Uses first 8 characters of MD5 hash of normalized description.

        Args:
            description: Task description text.

        Returns:
            8-character hex ID.
        """
        # Normalize: lowercase, remove extra whitespace, remove FR refs
        normalized = self._clean_description(description).lower()
        normalized = " ".join(normalized.split())
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    def get_tasks_for_requirement(
        self, requirement_id: str, tasks_path: Optional[Path] = None
    ) -> list[Task]:
        """Get all tasks that reference a specific requirement.

        Args:
            requirement_id: The FR-XXX ID to search for.
            tasks_path: Path to tasks.md file.

        Returns:
            List of tasks that reference the requirement.
        """
        tasks = self.parse(tasks_path)
        return [t for t in tasks if requirement_id in t.requirement_ids]

    def get_all_referenced_ids(self, tasks_path: Optional[Path] = None) -> set[str]:
        """Get set of all requirement IDs referenced in tasks.

        Args:
            tasks_path: Path to tasks.md file.

        Returns:
            Set of FR-XXX IDs referenced by at least one task.
        """
        tasks = self.parse(tasks_path)
        all_ids: set[str] = set()
        for task in tasks:
            all_ids.update(task.requirement_ids)
        return all_ids

    def preserve_references(
        self,
        old_tasks: list[Task],
        new_tasks: list[Task],
        similarity_threshold: float = 0.7,
    ) -> list[Task]:
        """Preserve cross-references from old tasks when regenerating tasks.md.

        Matches new tasks to old tasks by description similarity and transfers
        [FR-XXX] references to maintain traceability through regeneration.

        Args:
            old_tasks: Tasks from previous version of tasks.md with references.
            new_tasks: Newly generated tasks that may lack references.
            similarity_threshold: Minimum similarity score (0-1) for matching.

        Returns:
            New tasks with references preserved from matching old tasks.
        """
        from dataclasses import replace as dataclass_replace

        result: list[Task] = []
        used_old_tasks: set[str] = set()

        for new_task in new_tasks:
            best_match: Optional[Task] = None
            best_score = 0.0

            for old_task in old_tasks:
                # Skip already matched old tasks
                if old_task.id in used_old_tasks:
                    continue

                score = self._calculate_similarity(
                    new_task.description, old_task.description
                )
                if score > best_score and score >= similarity_threshold:
                    best_score = score
                    best_match = old_task

            if best_match and best_match.references:
                # Preserve references from the matched old task
                used_old_tasks.add(best_match.id)
                preserved_task = dataclass_replace(
                    new_task, references=list(best_match.references)
                )
                result.append(preserved_task)
            else:
                result.append(new_task)

        return result

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity between two task descriptions.

        Uses Jaccard similarity on word sets after normalization.

        Args:
            text1: First description text.
            text2: Second description text.

        Returns:
            Similarity score between 0.0 (no match) and 1.0 (identical).
        """
        words1 = set(self._normalize_for_matching(text1).split())
        words2 = set(self._normalize_for_matching(text2).split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def _normalize_for_matching(self, text: str) -> str:
        """Normalize description for similarity comparison.

        Removes task IDs, reference markers, and normalizes whitespace/case.

        Args:
            text: Task description text.

        Returns:
            Normalized text suitable for comparison.
        """
        # Remove task IDs (T001, T002, etc.)
        normalized = re.sub(r"\bT\d{3}\b", "", text)
        # Remove parallel markers [P]
        normalized = re.sub(r"\[P\]", "", normalized)
        # Remove user story markers [US1], [US2], etc.
        normalized = re.sub(r"\[US\d+\]", "", normalized)
        # Remove FR references
        normalized = self.REFERENCE_PATTERN.sub("", normalized)
        # Lowercase and normalize whitespace
        normalized = normalized.lower()
        normalized = " ".join(normalized.split())
        return normalized

    def apply_references_to_content(
        self,
        content: str,
        reference_map: dict[str, list[TaskReference]],
    ) -> str:
        """Apply preserved references to regenerated tasks.md content.

        Args:
            content: New tasks.md content without references.
            reference_map: Map of task description -> references to apply.

        Returns:
            Content with [FR-XXX] references inserted where applicable.
        """
        lines = content.split("\n")
        result_lines: list[str] = []

        for line in lines:
            match = self.TASK_PATTERN.match(line)
            if match:
                description = match.group("description").strip()
                cleaned = self._clean_description(description)
                normalized = self._normalize_for_matching(cleaned)

                # Look for matching references
                refs_to_add: list[TaskReference] = []
                for key, refs in reference_map.items():
                    if self._calculate_similarity(normalized, key) >= 0.7:
                        refs_to_add = refs
                        break

                if refs_to_add and not self.REFERENCE_PATTERN.search(line):
                    # Format references to add
                    ref_ids = [r.requirement_id for r in refs_to_add]
                    ref_str = f"[{', '.join(ref_ids)}]"
                    # Insert before end of line
                    line = f"{line.rstrip()} {ref_str}"

            result_lines.append(line)

        return "\n".join(result_lines)

    def build_reference_map(self, tasks: list[Task]) -> dict[str, list[TaskReference]]:
        """Build a map of normalized descriptions to their references.

        Args:
            tasks: List of tasks with references.

        Returns:
            Dict mapping normalized description to TaskReference list.
        """
        ref_map: dict[str, list[TaskReference]] = {}
        for task in tasks:
            if task.references:
                key = self._normalize_for_matching(task.description)
                ref_map[key] = list(task.references)
        return ref_map
