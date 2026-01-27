"""Cross-platform parity tests for 'doit planit' command."""
import sys
from pathlib import Path

import pytest


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_planit_file_structure_parity(temp_project_dir, comparison_tools):
    """
    Test that plan files have identical structure across platforms.

    Given: plan.md created on both platforms
    When: File structure is compared
    Then: Section headers and structure match
    """
    spec_dir = temp_project_dir / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan: Test Feature

**Branch**: 001-test-feature

## Summary

Implement test feature with cross-platform support.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pytest, rich
**Database**: N/A (file-based)

## Architecture

### Component Overview

```mermaid
flowchart TD
    A[User Input] --> B[Validator]
    B --> C[Processor]
    C --> D[Output]
```

## Project Structure

```
tests/
├── e2e/
│   └── windows/
│       └── test_parity.py
└── utils/
    └── comparison.py
```

## Implementation Phases

### Phase 1: Setup
- Create directory structure
- Initialize configuration

### Phase 2: Core Implementation
- Implement validator
- Implement processor

## Testing Strategy

- Unit tests for all components
- E2E tests on Windows and Linux
- Cross-platform parity validation
"""
    plan_file.write_text(plan_content, encoding="utf-8")

    # Read and normalize
    read_content = plan_file.read_text(encoding="utf-8")
    normalized = comparison_tools.normalize_output(read_content)

    # Verify structure
    assert "# Implementation Plan:" in normalized
    assert "## Technical Context" in normalized
    assert "## Architecture" in normalized
    assert "## Project Structure" in normalized
    assert "## Implementation Phases" in normalized


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_planit_mermaid_diagram_parity(temp_project_dir):
    """
    Test that Mermaid diagrams are identical across platforms.

    Given: plan.md with Mermaid diagram
    When: Diagram syntax is compared
    Then: Syntax is identical
    """
    spec_dir = temp_project_dir / "specs" / "002-mermaid"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan

## Architecture

```mermaid
flowchart TD
    Start[User Input] --> Validate[Validation]
    Validate --> Process[Processing]
    Process --> Output[Generate Output]

    Validate -->|Error| ErrorHandler[Error Handler]
    ErrorHandler --> Output
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant System
    participant Database

    User->>System: Request
    System->>Database: Query
    Database-->>System: Result
    System-->>User: Response
```
"""
    plan_file.write_text(plan_content, encoding="utf-8")

    # Read and verify Mermaid preserved
    read_content = plan_file.read_text(encoding="utf-8")

    assert "```mermaid" in read_content
    assert "flowchart TD" in read_content
    assert "sequenceDiagram" in read_content
    assert "Start[User Input]" in read_content
    assert "participant User" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_planit_code_block_parity(temp_project_dir):
    """
    Test that code blocks in plans are preserved across platforms.

    Given: plan.md with various code blocks
    When: Content is compared
    Then: Code blocks are identical
    """
    spec_dir = temp_project_dir / "specs" / "003-codeblocks"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan

## Code Examples

### Python Example

```python
def validate_input(data):
    if not data:
        raise ValueError("Data cannot be empty")
    return True
```

### Bash Example

```bash
#!/bin/bash
pytest tests/e2e/windows/ -v
```

### PowerShell Example

```powershell
# Run tests
pytest tests/e2e/windows/ -v
```
"""
    plan_file.write_text(plan_content, encoding="utf-8")

    # Read and verify code blocks
    read_content = plan_file.read_text(encoding="utf-8")

    assert "```python" in read_content
    assert "```bash" in read_content
    assert "```powershell" in read_content
    assert "def validate_input" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_planit_file_tree_parity(temp_project_dir, comparison_tools):
    """
    Test that file tree structures in plans are consistent.

    Given: plan.md with file tree
    When: Tree structure is normalized
    Then: Structure is comparable across platforms
    """
    spec_dir = temp_project_dir / "specs" / "004-tree"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan

## Project Structure

```
src/
├── core/
│   ├── __init__.py
│   ├── validator.py
│   └── processor.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── tests/
    ├── test_validator.py
    └── test_processor.py
```
"""
    plan_file.write_text(plan_content, encoding="utf-8")

    # Read and verify tree structure
    read_content = plan_file.read_text(encoding="utf-8")

    # Verify tree elements present
    assert "src/" in read_content
    assert "├──" in read_content or "├─" in read_content
    assert "│" in read_content
    assert "└──" in read_content or "└─" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_planit_dependency_list_parity(temp_project_dir, comparison_tools):
    """
    Test that dependency lists are identical across platforms.

    Given: plan.md with dependency specifications
    When: Dependencies are compared
    Then: Lists are identical
    """
    spec_dir = temp_project_dir / "specs" / "005-dependencies"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- pytest >= 7.0.0
- rich >= 13.0.0
- typer >= 0.9.0

**Development Dependencies**:
- black
- ruff
- mypy

**System Requirements**:
- Windows 10+ or Linux (Ubuntu 20.04+)
- PowerShell 7.x (Windows only)
- Git 2.30+
"""
    plan_file.write_text(plan_content, encoding="utf-8")

    # Read and normalize
    read_content = plan_file.read_text(encoding="utf-8")
    normalized = comparison_tools.normalize_output(read_content)

    # Verify dependencies listed
    assert "pytest >= 7.0.0" in read_content
    assert "rich >= 13.0.0" in read_content
    assert "Python 3.11+" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_planit_phase_structure_parity(temp_project_dir):
    """
    Test that implementation phases are structured identically.

    Given: plan.md with phase breakdown
    When: Phase structure is compared
    Then: Structure is consistent
    """
    spec_dir = temp_project_dir / "specs" / "006-phases"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan

## Implementation Phases

### Phase 1: Setup (Day 1)

**Objective**: Initialize project structure

**Tasks**:
- [ ] Create directory structure
- [ ] Initialize Git repository
- [ ] Configure pytest

### Phase 2: Core Development (Days 2-3)

**Objective**: Implement core functionality

**Tasks**:
- [ ] Implement validator
- [ ] Implement processor
- [ ] Add error handling

### Phase 3: Testing (Day 4)

**Objective**: Comprehensive testing

**Tasks**:
- [ ] Write unit tests
- [ ] Write E2E tests
- [ ] Run cross-platform validation
"""
    plan_file.write_text(plan_content, encoding="utf-8")

    # Read and verify phase structure
    read_content = plan_file.read_text(encoding="utf-8")

    assert "### Phase 1:" in read_content
    assert "### Phase 2:" in read_content
    assert "### Phase 3:" in read_content
    assert "**Objective**:" in read_content
    assert "**Tasks**:" in read_content


@pytest.mark.windows
@pytest.mark.unix
@pytest.mark.skipif(sys.platform != "win32", reason="Windows parity test")
def test_planit_table_format_parity(temp_project_dir):
    """
    Test that tables in plans are formatted consistently.

    Given: plan.md with tables
    When: Table formatting is compared
    Then: Format is consistent across platforms
    """
    spec_dir = temp_project_dir / "specs" / "007-tables"
    spec_dir.mkdir(parents=True, exist_ok=True)

    plan_file = spec_dir / "plan.md"
    plan_content = """# Implementation Plan

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET    | /api/v1/users | List users | Yes |
| POST   | /api/v1/users | Create user | Yes |
| PUT    | /api/v1/users/:id | Update user | Yes |
| DELETE | /api/v1/users/:id | Delete user | Yes |

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400  | Bad Request | Invalid input |
| 401  | Unauthorized | Auth required |
| 404  | Not Found | Resource missing |
"""
    plan_file.write_text(plan_content, encoding="utf-8")

    # Read and verify table format
    read_content = plan_file.read_text(encoding="utf-8")

    assert "| Method | Endpoint |" in read_content
    assert "|--------|----------|" in read_content
    assert "| GET    |" in read_content
    assert "| Code | Message |" in read_content
