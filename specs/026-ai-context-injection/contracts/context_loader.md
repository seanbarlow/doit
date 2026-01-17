# Contract: ContextLoader Service

**Feature**: 026-ai-context-injection
**Type**: Internal Python API
**Date**: 2026-01-15

## Overview

The `ContextLoader` service is responsible for loading, processing, and aggregating project context for injection into doit commands.

## Interface Definition

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class ContextSource:
    """A loaded context source."""
    source_type: str
    path: Path
    content: str
    token_count: int
    truncated: bool = False
    original_tokens: Optional[int] = None


@dataclass
class LoadedContext:
    """Aggregated context ready for injection."""
    sources: list[ContextSource]
    total_tokens: int
    any_truncated: bool
    loaded_at: datetime

    def to_markdown(self) -> str:
        """Format all sources as markdown for injection."""
        ...

    def get_source(self, source_type: str) -> Optional[ContextSource]:
        """Get specific source by type."""
        ...

    def has_source(self, source_type: str) -> bool:
        """Check if source type is loaded."""
        ...


class ContextLoader:
    """Service for loading and aggregating project context."""

    def __init__(
        self,
        project_root: Path,
        config: Optional[ContextConfig] = None,
        command: Optional[str] = None,
    ):
        """
        Initialize context loader.

        Args:
            project_root: Root directory of the project
            config: Context configuration (loads default if None)
            command: Current command name for per-command overrides
        """
        ...

    def load(self) -> LoadedContext:
        """
        Load all configured context sources.

        Returns:
            LoadedContext with all sources loaded and processed

        Raises:
            No exceptions - missing files handled gracefully
        """
        ...

    def load_constitution(self) -> Optional[ContextSource]:
        """Load constitution.md if enabled and exists."""
        ...

    def load_roadmap(self) -> Optional[ContextSource]:
        """Load roadmap.md if enabled and exists."""
        ...

    def load_current_spec(self) -> Optional[ContextSource]:
        """Load current feature spec based on branch name."""
        ...

    def find_related_specs(self) -> list[ContextSource]:
        """Find and load specs related to current feature."""
        ...

    def get_current_branch(self) -> Optional[str]:
        """Get current git branch name."""
        ...

    def extract_feature_name(self, branch: str) -> Optional[str]:
        """Extract feature name from branch (e.g., '026-ai-context' -> '026-ai-context')."""
        ...
```

## Method Contracts

### `ContextLoader.__init__`

**Preconditions**:
- `project_root` exists and is a directory
- `config` is valid ContextConfig or None
- `command` is a known doit command name or None

**Postconditions**:
- Instance created with resolved configuration
- Per-command overrides applied if command specified

### `ContextLoader.load`

**Preconditions**:
- Instance properly initialized

**Postconditions**:
- Returns LoadedContext with all enabled sources
- Missing files result in source being omitted (no error)
- Truncation applied if content exceeds limits
- Total tokens respects total_max_tokens limit

**Invariants**:
- Sources ordered by priority (lowest first)
- Token counts are estimates (may vary by model)

### `ContextLoader.find_related_specs`

**Preconditions**:
- Current spec loaded (or branch name available)

**Postconditions**:
- Returns up to `max_count` related specs
- Specs sorted by relevance score descending
- Current spec not included in results
- Empty list if no related specs found

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Config file missing | Use default configuration |
| Config file malformed | Log warning, use defaults |
| Context file missing | Skip source, continue loading |
| Context file unreadable | Log warning, skip source |
| Git not available | Skip branch detection, no current_spec |
| Token estimation fails | Use character/4 fallback |

## Performance Requirements

| Operation | Target | Maximum |
|-----------|--------|---------|
| Full context load | < 200ms | 500ms |
| Single file load | < 50ms | 100ms |
| Token estimation | < 10ms | 50ms |
| Related spec search | < 100ms | 200ms |

## Usage Example

```python
from doit_cli.services.context_loader import ContextLoader
from pathlib import Path

# Basic usage
loader = ContextLoader(project_root=Path.cwd())
context = loader.load()

# With command-specific overrides
loader = ContextLoader(
    project_root=Path.cwd(),
    command="specit"
)
context = loader.load()

# Access loaded context
if context.has_source("constitution"):
    constitution = context.get_source("constitution")
    print(f"Constitution: {constitution.token_count} tokens")

# Get markdown for injection
markdown = context.to_markdown()
```

## Output Format

The `to_markdown()` method produces output in this format:

```markdown
<!-- PROJECT CONTEXT - Auto-loaded by doit -->

## Constitution

[Full or truncated constitution content]

## Roadmap

[Full or truncated roadmap content]

## Current Spec: 026-ai-context-injection

[Full or truncated spec content]

## Related Specs

### 023-copilot-prompts-sync

[Summary or truncated content]

<!-- End of project context -->
```
