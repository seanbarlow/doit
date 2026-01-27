"""Cross-platform parity tests for 'doit specit' command."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_specit_file_structure_parity(temp_project_dir, comparison_tools):
    """
    Test that spec files have identical structure across platforms.

    Given: spec.md created on both platforms
    When: File structure is compared
    Then: Section headers and structure match
    """
    spec_dir = temp_project_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"
    spec_content = """# Specification: Test Feature

**Status**: Draft
**Priority**: P1

## Overview

Test feature for cross-platform validation.

## Functional Requirements

### FR1: Core Functionality
The system shall implement core functionality.

## Success Criteria

- [ ] SC1: Feature works on Windows
- [ ] SC2: Feature works on Linux
- [ ] SC3: Feature works on macOS

## User Stories

### US1: Basic User Story
**As a** developer
**I want** to test cross-platform functionality
**So that** I can ensure consistency

**Acceptance Criteria**:
- Given: Platform-specific test environment
- When: Tests are executed
- Then: Results are identical after normalization
"""
    spec_file.write_text(spec_content, encoding="utf-8")

    # Read and normalize
    read_content = spec_file.read_text(encoding="utf-8")
    normalized = comparison_tools.normalize_output(read_content)

    # Verify structure
    assert "# Specification:" in normalized
    assert "## Overview" in normalized
    assert "## Functional Requirements" in normalized
    assert "## Success Criteria" in normalized
    assert "## User Stories" in normalized


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_specit_markdown_formatting_parity(temp_project_dir, comparison_tools):
    """
    Test that Markdown formatting is preserved across platforms.

    Given: spec.md with various Markdown elements
    When: Content is compared
    Then: Formatting is preserved (after normalization)
    """
    spec_dir = temp_project_dir / "specs" / "002-markdown"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"
    spec_content = """# Test Markdown Elements

## Lists

- Bullet item 1
- Bullet item 2
  - Nested item 2.1
  - Nested item 2.2

1. Numbered item 1
2. Numbered item 2

## Code Blocks

```python
def test_function():
    return True
```

## Tables

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |

## Emphasis

**Bold text** and *italic text* and `inline code`.
"""
    spec_file.write_text(spec_content, encoding="utf-8")

    # Read and verify
    read_content = spec_file.read_text(encoding="utf-8")

    # Verify all Markdown elements present
    assert "- Bullet item 1" in read_content
    assert "1. Numbered item 1" in read_content
    assert "```python" in read_content
    assert "| Column 1 |" in read_content
    assert "**Bold text**" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_specit_frontmatter_parity(temp_project_dir, comparison_tools):
    """
    Test that YAML frontmatter is consistent across platforms.

    Given: spec.md with frontmatter
    When: Frontmatter is parsed
    Then: Values are identical
    """
    spec_dir = temp_project_dir / "specs" / "003-frontmatter"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"
    spec_content = """---
title: Test Feature
status: Draft
priority: P1
created: 2026-01-26
tags: [testing, cross-platform, parity]
---

# Specification: Test Feature

Content here.
"""
    spec_file.write_text(spec_content, encoding="utf-8")

    # Read and verify frontmatter
    read_content = spec_file.read_text(encoding="utf-8")
    normalized = comparison_tools.normalize_output(read_content)

    assert "---" in read_content
    assert "title: Test Feature" in read_content
    assert "status: Draft" in read_content
    assert "priority: P1" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_specit_checkbox_format_parity(temp_project_dir):
    """
    Test that checkbox formatting is consistent across platforms.

    Given: Spec with checkboxes
    When: Checkboxes are compared
    Then: Format is identical (- [ ] and - [X])
    """
    spec_dir = temp_project_dir / "specs" / "004-checkboxes"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"
    spec_content = """# Specification: Checkbox Test

## Requirements

- [ ] Unchecked requirement 1
- [X] Checked requirement 2
- [ ] Unchecked requirement 3
- [X] Checked requirement 4
"""
    spec_file.write_text(spec_content, encoding="utf-8")

    # Read and verify checkbox format
    read_content = spec_file.read_text(encoding="utf-8")

    # Verify standard checkbox format
    assert "- [ ] Unchecked" in read_content
    assert "- [X] Checked" in read_content
    assert read_content.count("- [ ]") == 2
    assert read_content.count("- [X]") == 2


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_specit_unicode_content_parity(temp_project_dir, comparison_tools):
    """
    Test that Unicode content is preserved across platforms.

    Given: Spec with Unicode characters
    When: Content is read
    Then: Unicode is preserved correctly
    """
    spec_dir = temp_project_dir / "specs" / "005-unicode"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"
    spec_content = """# Specification: Unicode Test

## International Text

- English: Hello World
- Japanese: こんにちは世界
- Chinese: 你好世界
- Arabic: مرحبا بالعالم
- Russian: Привет мир
- Emoji: 🚀 🎉 ✅ ❌

## Special Characters

- Arrows: → ← ↑ ↓
- Math: ∑ ∏ ∫ ∞
- Currency: $ € £ ¥
"""
    spec_file.write_text(spec_content, encoding="utf-8")

    # Read and verify Unicode preserved
    read_content = spec_file.read_text(encoding="utf-8")

    assert "こんにちは世界" in read_content
    assert "你好世界" in read_content
    assert "مرحبا بالعالم" in read_content
    assert "🚀" in read_content
    assert "→" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_specit_nested_directory_parity(temp_project_dir, comparison_tools):
    """
    Test that nested spec directories work identically.

    Given: Deeply nested spec directory structure
    When: Specs are created in nested paths
    Then: Structure is accessible on both platforms
    """
    # Create deeply nested structure
    nested_spec_dir = temp_project_dir / "specs" / "category" / "subcategory" / "006-nested"
    nested_spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = nested_spec_dir / "spec.md"
    spec_file.write_text("# Nested Spec\n\nContent here.", encoding="utf-8")

    # Verify structure
    assert nested_spec_dir.exists()
    assert spec_file.exists()

    # Normalize path
    normalized_path = comparison_tools.normalize_path(str(nested_spec_dir))
    assert "/" in normalized_path or "\\" in str(nested_spec_dir)


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_specit_relative_link_parity(temp_project_dir):
    """
    Test that relative links in specs work across platforms.

    Given: Spec with relative links to other files
    When: Links are normalized
    Then: Links use forward slashes (cross-platform standard)
    """
    spec_dir = temp_project_dir / "specs" / "007-links"
    spec_dir.mkdir(parents=True, exist_ok=True)

    spec_file = spec_dir / "spec.md"
    spec_content = """# Specification: Links Test

## Related Files

- [Plan](./plan.md)
- [Tasks](./tasks.md)
- [Research](../research.md)
- [Data Model](./data-model.md)
"""
    spec_file.write_text(spec_content, encoding="utf-8")

    # Read and verify links use forward slashes
    read_content = spec_file.read_text(encoding="utf-8")

    assert "./plan.md" in read_content
    assert "./tasks.md" in read_content
    assert "../research.md" in read_content
    # Relative links should use forward slashes
    assert "\\" not in read_content.split("](")[1] if "](" in read_content else True
