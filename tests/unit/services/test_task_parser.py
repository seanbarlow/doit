"""Tests for TaskParser service."""

import pytest
from pathlib import Path

from doit_cli.services.task_parser import TaskParser


class TestTaskParser:
    """Tests for TaskParser."""

    def test_parse_single_task(self, tmp_path: Path) -> None:
        """Test parsing a tasks file with a single task."""
        tasks_content = """# Tasks

- [ ] Implement the feature
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 1
        assert tasks[0].completed is False
        assert "Implement the feature" in tasks[0].description

    def test_parse_completed_task(self, tmp_path: Path) -> None:
        """Test parsing a completed task."""
        tasks_content = """- [x] Completed task
- [X] Also completed"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 2
        assert all(t.completed for t in tasks)

    def test_parse_task_with_single_reference(self, tmp_path: Path) -> None:
        """Test parsing a task with a single FR reference."""
        tasks_content = """- [ ] Implement the parser [FR-001]"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 1
        assert len(tasks[0].references) == 1
        assert tasks[0].references[0].requirement_id == "FR-001"
        assert tasks[0].requirement_ids == ["FR-001"]

    def test_parse_task_with_multiple_references(self, tmp_path: Path) -> None:
        """Test parsing a task with multiple FR references."""
        tasks_content = """- [ ] Implement coverage [FR-001, FR-003]"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 1
        assert len(tasks[0].references) == 2
        assert tasks[0].requirement_ids == ["FR-001", "FR-003"]
        # Check positions
        assert tasks[0].references[0].position == 0
        assert tasks[0].references[1].position == 1

    def test_parse_task_references_preserved_order(self, tmp_path: Path) -> None:
        """Test that reference order is preserved."""
        tasks_content = """- [ ] Task [FR-005, FR-001, FR-003]"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert tasks[0].requirement_ids == ["FR-005", "FR-001", "FR-003"]

    def test_parse_task_without_references(self, tmp_path: Path) -> None:
        """Test parsing a task without any FR references."""
        tasks_content = """- [ ] Setup project structure"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 1
        assert len(tasks[0].references) == 0
        assert tasks[0].requirement_ids == []

    def test_parse_mixed_tasks(self, tmp_path: Path) -> None:
        """Test parsing tasks with and without references."""
        tasks_content = """# Tasks

- [ ] T001 Setup [FR-001]
- [x] T002 Completed task
- [ ] T003 Multi-ref [FR-002, FR-003]
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 3
        assert tasks[0].requirement_ids == ["FR-001"]
        assert tasks[1].requirement_ids == []
        assert tasks[1].completed is True
        assert tasks[2].requirement_ids == ["FR-002", "FR-003"]

    def test_clean_description_removes_references(self, tmp_path: Path) -> None:
        """Test that description is cleaned of FR references."""
        tasks_content = """- [ ] Implement the parser [FR-001]"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert "[FR-001]" not in tasks[0].description
        assert "Implement the parser" in tasks[0].description

    def test_clean_description_removes_multiple_references(
        self, tmp_path: Path
    ) -> None:
        """Test that multiple FR references are cleaned."""
        tasks_content = """- [ ] Task [FR-001, FR-002] more text [FR-003]"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert "[FR-" not in tasks[0].description
        assert "Task" in tasks[0].description
        assert "more text" in tasks[0].description

    def test_parse_preserves_line_numbers(self, tmp_path: Path) -> None:
        """Test that line numbers are correctly captured."""
        tasks_content = """# Tasks

## Phase 1

- [ ] First task

- [ ] Second task
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert tasks[0].line_number == 5
        assert tasks[1].line_number == 7

    def test_parse_ignores_non_task_lines(self, tmp_path: Path) -> None:
        """Test that non-task lines are ignored."""
        tasks_content = """# Tasks

Regular paragraph text.

- Not a checkbox
* [ ] Wrong bullet
- [?] Invalid state

- [ ] Valid task
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 1
        assert "Valid task" in tasks[0].description

    def test_parse_empty_file(self, tmp_path: Path) -> None:
        """Test parsing an empty tasks file."""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text("")

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert len(tasks) == 0

    def test_parse_file_not_found(self, tmp_path: Path) -> None:
        """Test that FileNotFoundError is raised for missing file."""
        parser = TaskParser()

        with pytest.raises(FileNotFoundError):
            parser.parse(tmp_path / "nonexistent.md")

    def test_parse_no_path_provided(self) -> None:
        """Test that ValueError is raised when no path provided."""
        parser = TaskParser()

        with pytest.raises(ValueError, match="No tasks path provided"):
            parser.parse()

    def test_get_tasks_for_requirement(self, tmp_path: Path) -> None:
        """Test getting tasks that reference a specific requirement."""
        tasks_content = """- [ ] Task A [FR-001]
- [ ] Task B [FR-002]
- [ ] Task C [FR-001, FR-002]
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.get_tasks_for_requirement("FR-001", tasks_file)

        assert len(tasks) == 2
        assert all("FR-001" in t.requirement_ids for t in tasks)

    def test_get_tasks_for_requirement_not_found(self, tmp_path: Path) -> None:
        """Test getting tasks for unreferenced requirement."""
        tasks_content = """- [ ] Task A [FR-001]"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.get_tasks_for_requirement("FR-999", tasks_file)

        assert len(tasks) == 0

    def test_get_all_referenced_ids(self, tmp_path: Path) -> None:
        """Test getting all unique requirement IDs referenced."""
        tasks_content = """- [ ] Task A [FR-001]
- [ ] Task B [FR-002]
- [ ] Task C [FR-001, FR-003]
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        ids = parser.get_all_referenced_ids(tasks_file)

        assert ids == {"FR-001", "FR-002", "FR-003"}

    def test_task_ids_are_unique_for_different_descriptions(
        self, tmp_path: Path
    ) -> None:
        """Test that different tasks get different IDs."""
        tasks_content = """- [ ] First task
- [ ] Second task
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser()
        tasks = parser.parse(tasks_file)

        assert tasks[0].id != tasks[1].id

    def test_task_ids_are_consistent_for_same_description(
        self, tmp_path: Path
    ) -> None:
        """Test that same description produces same ID."""
        parser = TaskParser()

        # Parse same content twice
        content = "- [ ] Same task description"
        tasks1 = parser.parse_content(content, "/path1/tasks.md")
        tasks2 = parser.parse_content(content, "/path2/tasks.md")

        assert tasks1[0].id == tasks2[0].id

    def test_constructor_with_path(self, tmp_path: Path) -> None:
        """Test using path from constructor."""
        tasks_content = """- [ ] Task"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        parser = TaskParser(tasks_file)
        tasks = parser.parse()

        assert len(tasks) == 1

    def test_parse_content_directly(self) -> None:
        """Test parsing content string directly."""
        content = """- [ ] First task [FR-001]
- [x] Second task [FR-002]"""

        parser = TaskParser()
        tasks = parser.parse_content(content, "/path/to/tasks.md")

        assert len(tasks) == 2
        assert tasks[0].tasks_file == "/path/to/tasks.md"
        assert tasks[0].requirement_ids == ["FR-001"]
        assert tasks[1].completed is True


class TestTaskParserReferencePreservation:
    """Tests for reference preservation functionality."""

    def test_preserve_references_exact_match(self) -> None:
        """Test preserving references for exactly matching tasks."""
        parser = TaskParser()

        old_content = """- [ ] Implement the parser [FR-001]"""
        old_tasks = parser.parse_content(old_content, "/old/tasks.md")

        new_content = """- [ ] Implement the parser"""
        new_tasks = parser.parse_content(new_content, "/new/tasks.md")

        preserved = parser.preserve_references(old_tasks, new_tasks)

        assert len(preserved) == 1
        assert preserved[0].requirement_ids == ["FR-001"]

    def test_preserve_references_similar_match(self) -> None:
        """Test preserving references for similar but not identical tasks."""
        parser = TaskParser()

        old_content = """- [ ] T001 Create RequirementParser class [FR-001, FR-002]"""
        old_tasks = parser.parse_content(old_content, "/old/tasks.md")

        # More similar description - only minor variations
        new_content = """- [ ] T001 [P] Create RequirementParser class"""
        new_tasks = parser.parse_content(new_content, "/new/tasks.md")

        preserved = parser.preserve_references(old_tasks, new_tasks)

        assert len(preserved) == 1
        assert preserved[0].requirement_ids == ["FR-001", "FR-002"]

    def test_preserve_references_no_match(self) -> None:
        """Test that unmatched tasks don't get references."""
        parser = TaskParser()

        old_content = """- [ ] Setup project [FR-001]"""
        old_tasks = parser.parse_content(old_content, "/old/tasks.md")

        new_content = """- [ ] Implement validation logic"""
        new_tasks = parser.parse_content(new_content, "/new/tasks.md")

        preserved = parser.preserve_references(old_tasks, new_tasks)

        assert len(preserved) == 1
        assert preserved[0].requirement_ids == []

    def test_preserve_references_multiple_tasks(self) -> None:
        """Test preserving references across multiple tasks."""
        parser = TaskParser()

        old_content = """- [ ] Setup the project structure and initialize dependencies [FR-001]
- [ ] Implement core parser logic [FR-002]
- [ ] Create and configure validation rules [FR-003]"""
        old_tasks = parser.parse_content(old_content, "/old/tasks.md")

        # Use similarity threshold of 0.5 for this test
        new_content = """- [ ] Setup the project structure and initialize config
- [ ] Completely different task here
- [ ] Create and configure validation checks"""
        new_tasks = parser.parse_content(new_content, "/new/tasks.md")

        preserved = parser.preserve_references(
            old_tasks, new_tasks, similarity_threshold=0.5
        )

        assert len(preserved) == 3
        assert preserved[0].requirement_ids == ["FR-001"]
        assert preserved[1].requirement_ids == []  # No match
        assert preserved[2].requirement_ids == ["FR-003"]

    def test_calculate_similarity_identical(self) -> None:
        """Test similarity score for identical texts."""
        parser = TaskParser()

        score = parser._calculate_similarity("hello world", "hello world")
        assert score == 1.0

    def test_calculate_similarity_partial(self) -> None:
        """Test similarity score for partially matching texts."""
        parser = TaskParser()

        score = parser._calculate_similarity("hello world foo", "hello world bar")
        # Intersection: {hello, world}, Union: {hello, world, foo, bar}
        assert score == 2 / 4  # 0.5

    def test_calculate_similarity_no_match(self) -> None:
        """Test similarity score for completely different texts."""
        parser = TaskParser()

        score = parser._calculate_similarity("foo bar baz", "hello world test")
        assert score == 0.0

    def test_calculate_similarity_empty(self) -> None:
        """Test similarity score for empty texts."""
        parser = TaskParser()

        assert parser._calculate_similarity("", "") == 0.0
        assert parser._calculate_similarity("hello", "") == 0.0
        assert parser._calculate_similarity("", "world") == 0.0

    def test_normalize_for_matching_removes_task_ids(self) -> None:
        """Test normalization removes task IDs."""
        parser = TaskParser()

        normalized = parser._normalize_for_matching("T001 Create parser")
        assert "T001" not in normalized
        assert "create parser" in normalized

    def test_normalize_for_matching_removes_markers(self) -> None:
        """Test normalization removes [P] and [US1] markers."""
        parser = TaskParser()

        normalized = parser._normalize_for_matching("[P] [US1] Create parser")
        assert "[P]" not in normalized
        assert "[US1]" not in normalized
        assert "create parser" in normalized

    def test_normalize_for_matching_removes_fr_refs(self) -> None:
        """Test normalization removes FR references."""
        parser = TaskParser()

        normalized = parser._normalize_for_matching("Create parser [FR-001, FR-002]")
        assert "[FR-001" not in normalized
        assert "FR-002" not in normalized
        assert "create parser" in normalized

    def test_build_reference_map(self) -> None:
        """Test building a reference map from tasks."""
        parser = TaskParser()

        content = """- [ ] Task A [FR-001]
- [ ] Task B without refs
- [ ] Task C [FR-002, FR-003]"""
        tasks = parser.parse_content(content, "/tasks.md")

        ref_map = parser.build_reference_map(tasks)

        # Only tasks with references should be in the map
        assert len(ref_map) == 2
        # Check that references are correct
        for key, refs in ref_map.items():
            if "task a" in key:
                assert len(refs) == 1
                assert refs[0].requirement_id == "FR-001"
            elif "task c" in key:
                assert len(refs) == 2
                assert refs[0].requirement_id == "FR-002"
                assert refs[1].requirement_id == "FR-003"

    def test_apply_references_to_content(self) -> None:
        """Test applying reference map to new content."""
        parser = TaskParser()

        # Build reference map from old content
        old_content = """- [ ] Setup project [FR-001]
- [ ] Create models [FR-002, FR-003]"""
        old_tasks = parser.parse_content(old_content, "/old/tasks.md")
        ref_map = parser.build_reference_map(old_tasks)

        # Apply to new content without references
        new_content = """# Tasks

- [ ] Setup project
- [ ] Different task
- [ ] Create models
"""

        result = parser.apply_references_to_content(new_content, ref_map)

        assert "[FR-001]" in result
        assert "[FR-002, FR-003]" in result
        # Different task should not have references
        lines = result.split("\n")
        for line in lines:
            if "Different task" in line:
                assert "[FR-" not in line

    def test_preserve_references_threshold(self) -> None:
        """Test custom similarity threshold."""
        parser = TaskParser()

        old_content = """- [ ] Create the parser class [FR-001]"""
        old_tasks = parser.parse_content(old_content, "/old/tasks.md")

        new_content = """- [ ] Create some class"""
        new_tasks = parser.parse_content(new_content, "/new/tasks.md")

        # With high threshold, should not match
        preserved_high = parser.preserve_references(
            old_tasks, new_tasks, similarity_threshold=0.9
        )
        assert preserved_high[0].requirement_ids == []

        # With low threshold, should match
        preserved_low = parser.preserve_references(
            old_tasks, new_tasks, similarity_threshold=0.3
        )
        assert preserved_low[0].requirement_ids == ["FR-001"]
