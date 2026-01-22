# Research: Constitution and Tech Stack Separation

**Feature**: 046-constitution-tech-stack-split
**Date**: 2026-01-22
**Status**: Complete

## Research Questions

### 1. How does the current init command create constitution.md?

**Finding**: The init command uses `TemplateManager` to copy templates from `templates/memory/` to `.doit/memory/`.

**Key Files**:
- [init_command.py](../../src/doit_cli/cli/init_command.py) - `run_init()` function (line 345)
- [template_manager.py](../../src/doit_cli/services/template_manager.py) - `copy_memory_templates()` method
- [templates/memory/constitution.md](../../templates/memory/constitution.md) - Source template

**Decision**: Follow the same pattern - add `tech-stack.md` to `MEMORY_TEMPLATES` constant and create the template file.

---

### 2. How does context loading currently work for constitution.md?

**Finding**: Context sources are defined in `SourceConfig.get_defaults()` with priority ordering. The `ContextLoader` class loads each source via dedicated methods like `load_constitution()`.

**Key Files**:
- [context_config.py](../../src/doit_cli/models/context_config.py) - `SourceConfig` class (line 103)
- [context_loader.py](../../src/doit_cli/services/context_loader.py) - `load_constitution()` method (line 712)
- [context.yaml](../../.doit/config/context.yaml) - Configuration file

**Decision**: Add `tech_stack` as a new source type with priority 2 (after constitution at priority 1, before roadmap).

---

### 3. What sections should be extracted to tech-stack.md?

**Finding**: Based on the current constitution template structure:

**Extract to tech-stack.md**:
- `## Tech Stack` (Languages, Frameworks, Libraries subsections)
- `## Infrastructure` (Hosting, Cloud Provider, Database subsections)
- `## Deployment` (CI/CD Pipeline, Deployment Strategy, Environments subsections)

**Keep in constitution.md**:
- `## Purpose & Goals`
- `## Core Principles`
- `## Quality Standards`
- `## Development Workflow`
- `## Governance`

**Decision**: Use section header matching for content analysis. Keywords: "Tech Stack", "Languages", "Frameworks", "Libraries", "Infrastructure", "Hosting", "Cloud", "Database", "Deployment", "CI/CD", "Environments".

---

### 4. How should the cleanup command identify tech sections?

**Finding**: Content analysis approach using:
1. **Section headers** - Match H2 headers (`## Tech Stack`, `## Infrastructure`, `## Deployment`)
2. **Keyword detection** - Backup for non-standard headers
3. **Subsection grouping** - Keep related H3 sections together

**Algorithm**:
```python
TECH_SECTIONS = ["Tech Stack", "Infrastructure", "Deployment"]
TECH_KEYWORDS = ["language", "framework", "library", "hosting", "cloud",
                 "database", "cicd", "ci/cd", "pipeline", "environment"]

def is_tech_section(header: str, content: str) -> bool:
    # Check exact header match first
    if any(ts.lower() in header.lower() for ts in TECH_SECTIONS):
        return True
    # Fallback to keyword analysis
    keyword_count = sum(1 for kw in TECH_KEYWORDS if kw in content.lower())
    return keyword_count >= 3
```

**Decision**: Prioritize header matching over keyword analysis for deterministic behavior.

---

### 5. How should command-specific context loading work?

**Finding**: The context system already supports per-command overrides via `CommandOverride` in `context.yaml`.

**Current overrides** (from context.yaml):
- `specit`: Disables `related_specs`
- `roadmapit`: Disables `current_spec`, `related_specs`
- `constitution`: Disables `current_spec`, `related_specs`

**Proposed overrides**:
| Command | constitution | tech_stack | Rationale |
|---------|--------------|------------|-----------|
| specit | ✅ | ❌ | Specs focus on principles, not tech details |
| planit | ✅ | ✅ | Planning needs tech stack for decisions |
| taskit | ✅ | ✅ | Task breakdown needs implementation details |
| reviewit | ✅ | ✅ | Review needs full context |
| constitution | ✅ | ❌ | Working on constitution, not tech stack |

**Decision**: Add command overrides to context.yaml template with tech_stack disabled for specit and constitution commands.

---

### 6. What should the cross-reference format be?

**Finding**: Other doit files use markdown links for cross-references.

**Proposed format**:

In constitution.md:
```markdown
> **See also**: [Tech Stack](tech-stack.md) for languages, frameworks, and deployment details.
```

In tech-stack.md:
```markdown
> **See also**: [Constitution](constitution.md) for project principles and governance.
```

**Decision**: Use blockquote format with "See also" prefix for visual distinction.

---

## Best Practices Researched

### Markdown Section Parsing

**Pattern**: Use regex to parse markdown sections by header level.

```python
import re

def parse_sections(content: str) -> dict[str, str]:
    """Parse markdown into sections by H2 headers."""
    sections = {}
    pattern = r'^## (.+?)$'
    parts = re.split(pattern, content, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections[header] = body.strip()

    return sections
```

### File Backup Strategy

**Pattern**: Create timestamped backup before modification.

```python
from datetime import datetime
from pathlib import Path
import shutil

def create_backup(file_path: Path) -> Path:
    """Create timestamped backup of file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".{timestamp}.bak")
    shutil.copy2(file_path, backup_path)
    return backup_path
```

**Decision**: Use `.bak` extension with timestamp for multiple backup support.

---

## Alternatives Considered

### 1. YAML-based configuration instead of markdown files

**Rejected because**:
- Constitution and tech-stack are meant to be human-readable and editable
- Markdown aligns with existing doit patterns (specs, roadmap, etc.)
- AI agents work better with markdown context

### 2. Single file with markers instead of two separate files

**Rejected because**:
- Defeats the purpose of selective context loading
- More complex to parse and maintain
- Cross-references between files provide clearer navigation

### 3. Automatic sync between files

**Rejected because**:
- Out of scope per spec
- Would add complexity without clear benefit
- Files serve different purposes and shouldn't be synchronized

---

## Conclusion

All research questions resolved. Implementation can proceed with:
1. Template-based approach using existing `TemplateManager`
2. Section header matching for content analysis
3. Per-command context overrides for selective loading
4. Cross-references using "See also" blockquotes
