# Quickstart: Constitution and Tech Stack Separation

**Feature**: 046-constitution-tech-stack-split
**Date**: 2026-01-22

## Prerequisites

- Python 3.11+
- doit-toolkit-cli installed
- Existing doit project (for migration) or new project setup

## Implementation Order

```
Phase 1: Templates → Phase 2: Init → Phase 3: Cleanup → Phase 4: Context → Phase 5: Commands → Phase 6: Tests
```

## Phase 1: Template Updates

### 1.1 Create tech-stack.md template

**File**: `templates/memory/tech-stack.md`

```markdown
# [PROJECT_NAME] Tech Stack

> **See also**: [Constitution](constitution.md) for project principles and governance.

## Tech Stack

### Languages

[PRIMARY_LANGUAGE]

### Frameworks

- [FRAMEWORK_1]

### Libraries

- [LIBRARY_1]

## Infrastructure

### Hosting

[HOSTING_PLATFORM]

### Cloud Provider

[CLOUD_PROVIDER]

### Database

[DATABASE]

## Deployment

### CI/CD Pipeline

[CICD_TOOL]

### Deployment Strategy

[DEPLOYMENT_APPROACH]

### Environments

- Development (local)
- Production
```

### 1.2 Update constitution.md template

**File**: `templates/memory/constitution.md`

Remove sections: `## Tech Stack`, `## Infrastructure`, `## Deployment`

Add cross-reference after title:
```markdown
> **See also**: [Tech Stack](tech-stack.md) for languages, frameworks, and deployment details.
```

### 1.3 Update TemplateManager

**File**: `src/doit_cli/services/template_manager.py`

```python
# Update constant
MEMORY_TEMPLATES = ["constitution.md", "roadmap.md", "completed_roadmap.md", "tech-stack.md"]
```

---

## Phase 2: Init Command Updates

### 2.1 Verify template copying

**File**: `src/doit_cli/cli/init_command.py`

The `copy_memory_templates()` method in TemplateManager already copies all files in `MEMORY_TEMPLATES`. No code changes needed if constant is updated.

### 2.2 Test init creates both files

```bash
# Create test directory
mkdir /tmp/test-init && cd /tmp/test-init
git init

# Run init
doit init --yes

# Verify both files exist
ls -la .doit/memory/
# Should show: constitution.md, tech-stack.md, roadmap.md, completed_roadmap.md
```

---

## Phase 3: Cleanup Command

### 3.1 Create CleanupService

**File**: `src/doit_cli/services/cleanup_service.py`

```python
"""Service for separating constitution and tech stack content."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from rich.console import Console


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    backup_path: Path
    extracted_sections: list[str]
    preserved_sections: list[str]
    unclear_sections: list[str]
    tech_stack_created: bool


class CleanupService:
    """Separates tech stack content from constitution."""

    TECH_SECTIONS = ["Tech Stack", "Infrastructure", "Deployment"]
    TECH_KEYWORDS = ["language", "framework", "library", "hosting", "cloud",
                     "database", "cicd", "ci/cd", "pipeline", "environment"]

    def __init__(self, memory_dir: Path, console: Console | None = None):
        self.memory_dir = memory_dir
        self.console = console or Console()
        self.constitution_path = memory_dir / "constitution.md"
        self.tech_stack_path = memory_dir / "tech-stack.md"

    def analyze(self) -> dict[str, list[str]]:
        """Analyze constitution and categorize sections."""
        # Implementation: Parse sections and categorize
        pass

    def create_backup(self) -> Path:
        """Create timestamped backup of constitution."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.constitution_path.with_suffix(f".{timestamp}.bak")
        shutil.copy2(self.constitution_path, backup_path)
        return backup_path

    def cleanup(self, merge_existing: bool = False) -> CleanupResult:
        """Execute the cleanup operation."""
        # Implementation: Separate content and write files
        pass
```

### 3.2 Add constitution command

**File**: `src/doit_cli/cli/constitution_command.py`

```python
"""Constitution management commands."""

import typer
from rich.console import Console

from ..services.cleanup_service import CleanupService
from ..utils.project import find_project_root

app = typer.Typer(help="Manage project constitution")
console = Console()


@app.command()
def cleanup(
    merge: bool = typer.Option(False, "--merge", help="Merge with existing tech-stack.md"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be changed"),
):
    """Separate tech stack content from constitution."""
    project_root = find_project_root()
    memory_dir = project_root / ".doit" / "memory"

    service = CleanupService(memory_dir, console)

    if dry_run:
        analysis = service.analyze()
        # Display what would be extracted
        return

    result = service.cleanup(merge_existing=merge)
    # Display results
```

### 3.3 Register command in main CLI

**File**: `src/doit_cli/cli/main.py`

```python
from .constitution_command import app as constitution_app

app.add_typer(constitution_app, name="constitution")
```

---

## Phase 4: Context Integration

### 4.1 Add tech_stack source

**File**: `src/doit_cli/models/context_config.py`

```python
# In SourceConfig.get_defaults()
@classmethod
def get_defaults(cls) -> dict[str, "SourceConfig"]:
    return {
        "constitution": SourceConfig(enabled=True, priority=1, max_count=1),
        "tech_stack": SourceConfig(enabled=True, priority=2, max_count=1),  # NEW
        "roadmap": SourceConfig(enabled=True, priority=3, max_count=1),
        "completed_roadmap": SourceConfig(enabled=True, priority=4, max_count=1),
        "current_spec": SourceConfig(enabled=True, priority=5, max_count=1),
        "related_specs": SourceConfig(enabled=True, priority=6, max_count=3),
    }
```

### 4.2 Add load_tech_stack method

**File**: `src/doit_cli/services/context_loader.py`

```python
def load_tech_stack(self) -> ContextSource | None:
    """Load tech stack from .doit/memory/tech-stack.md."""
    tech_stack_path = self.project_root / ".doit" / "memory" / "tech-stack.md"

    if not tech_stack_path.exists():
        # Fallback: check for tech stack in constitution (legacy)
        return None

    content = tech_stack_path.read_text()
    tokens = estimate_tokens(content)

    if tokens > self.config.max_tokens_per_source:
        content = truncate_content(content, self.config.max_tokens_per_source)
        tokens = self.config.max_tokens_per_source

    return ContextSource(
        source_type="tech_stack",
        path=tech_stack_path,
        content=content,
        tokens=tokens,
        truncated=tokens >= self.config.max_tokens_per_source,
    )
```

### 4.3 Update context.yaml template

**File**: `templates/config/context.yaml`

```yaml
sources:
  constitution:
    enabled: true
    priority: 1
  tech_stack:  # NEW
    enabled: true
    priority: 2
  roadmap:
    enabled: true
    priority: 3
  # ... rest unchanged

command_overrides:
  specit:
    sources:
      tech_stack:
        enabled: false  # Specs don't need tech details
  constitution:
    sources:
      tech_stack:
        enabled: false  # Working on constitution
```

---

## Phase 5: Command Template Updates

### 5.1 Update doit.planit.md

**File**: `templates/commands/doit.planit.md`

Add to "Load context" section:
```markdown
- Read `.doit/memory/tech-stack.md` for technology decisions
- If tech-stack.md doesn't exist, check constitution.md for Tech Stack section (legacy)
```

### 5.2 Update doit.taskit.md

**File**: `templates/commands/doit.taskit.md`

Add reference:
```markdown
- Reference tech-stack.md for implementation technology choices
```

### 5.3 Update doit.constitution.md

**File**: `templates/commands/doit.constitution.md`

Add cleanup subcommand documentation:
```markdown
## Cleanup Subcommand

To separate tech stack content from an existing combined constitution:

```bash
doit constitution cleanup
```

Or via slash command:
```
/doit.constitution cleanup
```
```

---

## Phase 6: Testing

### 6.1 Unit tests for CleanupService

**File**: `tests/unit/test_cleanup_service.py`

```python
import pytest
from pathlib import Path

from doit_cli.services.cleanup_service import CleanupService


@pytest.fixture
def temp_memory_dir(tmp_path):
    memory_dir = tmp_path / ".doit" / "memory"
    memory_dir.mkdir(parents=True)
    return memory_dir


def test_analyze_identifies_tech_sections(temp_memory_dir):
    """Test that tech sections are correctly identified."""
    constitution = temp_memory_dir / "constitution.md"
    constitution.write_text("""
# Test Constitution

## Purpose & Goals
Project purpose here.

## Tech Stack
### Languages
Python 3.11+

## Core Principles
Principles here.

## Infrastructure
### Hosting
PyPI
""")

    service = CleanupService(temp_memory_dir)
    analysis = service.analyze()

    assert "Tech Stack" in analysis["tech"]
    assert "Infrastructure" in analysis["tech"]
    assert "Purpose & Goals" in analysis["constitution"]
    assert "Core Principles" in analysis["constitution"]


def test_cleanup_creates_backup(temp_memory_dir):
    """Test that backup is created before modification."""
    # Setup and test
    pass


def test_cleanup_handles_existing_tech_stack(temp_memory_dir):
    """Test behavior when tech-stack.md already exists."""
    # Setup and test
    pass
```

### 6.2 Integration test for init

**File**: `tests/integration/test_init_command.py`

```python
def test_init_creates_both_files(tmp_path):
    """Test that init creates both constitution.md and tech-stack.md."""
    # Run init command
    # Verify both files exist with cross-references
    pass
```

---

## Verification Checklist

- [ ] `doit init` creates both constitution.md and tech-stack.md
- [ ] Both files have cross-references to each other
- [ ] `doit constitution cleanup` separates existing combined files
- [ ] Backup is created before cleanup
- [ ] `doit context show` displays tech-stack.md as a source
- [ ] `/doit.planit` loads tech-stack.md for technical context
- [ ] Legacy projects (constitution-only) still work
