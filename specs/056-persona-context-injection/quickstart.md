# Quickstart: Project-Level Personas with Context Injection

**Branch**: `056-persona-context-injection`
**Date**: 2026-03-26

---

## Overview

This feature adds `personas` as a new context source in the doit context injection system. The context loader reads `.doit/memory/personas.md` and injects it into `/doit.researchit`, `/doit.specit`, and `/doit.planit` sessions.

## Files to Change

### Python Code (2 files)

1. **`src/doit_cli/models/context_config.py`**
   - Add `"personas"` to `SourceConfig.default_sources()` at priority 3
   - Shift existing source priorities: roadmap → 4, completed_roadmap → 5, current_spec → 6, related_specs → 7
   - Add `"personas"` to `SummarizationConfig.source_priorities` list
   - Add `"personas": "Personas"` to `LoadedContext.to_markdown()` display_names
   - Add command overrides to disable personas for non-target commands

2. **`src/doit_cli/services/context_loader.py`**
   - Add `load_personas()` method following the `load_constitution()` pattern
   - Read from `.doit/memory/personas.md` (or feature-level `specs/{feature}/personas.md` if it exists)
   - Never truncate — load full content
   - Add `elif source_name == "personas"` branch in `load()` method
   - Add `"personas"` to the source names list in `load()`

### Templates (4 files)

3. **`src/doit_cli/templates/config/context.yaml`**
   - Add personas source entry between tech_stack and roadmap

4. **`src/doit_cli/templates/commands/doit.roadmapit.md`**
   - Add persona generation step using `personas-output-template.md`

5. **`src/doit_cli/templates/commands/doit.researchit.md`**
   - Add instruction to reference project personas from injected context

6. **`src/doit_cli/templates/commands/doit.specit.md`**
   - Add instruction to map user stories to project persona IDs

7. **`src/doit_cli/templates/commands/doit.planit.md`**
   - Add instruction to reference personas for design decisions

### Config (1 file)

8. **`.doit/config/context.yaml`** (live project instance)
   - Add personas source with priority 3, adjust existing priorities

## Implementation Pattern

The `load_personas()` method follows the exact same pattern as `load_constitution()`:

```python
def load_personas(self, max_tokens: Optional[int] = None) -> Optional[ContextSource]:
    """Load personas.md if enabled and exists."""
    # Check feature-level first (precedence)
    feature_path = self._get_feature_personas_path()
    if feature_path and feature_path.exists():
        path = feature_path
    else:
        path = self.project_root / ".doit" / "memory" / "personas.md"

    content = self._read_file(path)
    if content is None:
        return None

    token_count = estimate_tokens(content)

    return ContextSource(
        source_type="personas",
        path=path,
        content=content,  # Full content, no truncation
        token_count=token_count,
        truncated=False,
        original_tokens=None,
    )
```

## Testing

```bash
# Run existing context tests to verify no regressions
pytest tests/unit/services/test_context_loader.py -x --tb=short

# Run config model tests
pytest tests/unit/models/test_context_config.py -x --tb=short

# Verify context loading works
doit context show
```

## Verification

After implementation, verify:

1. `doit context show` shows "Personas" source when `.doit/memory/personas.md` exists
2. `doit context show` works without error when personas file is missing
3. `doit context show --command specit` shows personas enabled
4. `doit context show --command taskit` shows personas disabled
