# Quickstart: Context Roadmap Summary

**Feature**: `038-context-roadmap-summary`
**Date**: 2026-01-20

## Overview

This feature enhances the AI context injection system to provide intelligent roadmap context summarization. After implementation, AI agents receive:

1. **Prioritized roadmap summary** - P1/P2 items with rationale, P3/P4 as titles only
2. **Relevant completed items** - Historical work formatted for AI semantic understanding
3. **Context condensation** - Guidance prompts and truncation when context exceeds limits

## Quick Usage

### Default Behavior (No Configuration Needed)

Once implemented, the enhanced context loading is automatic:

```bash
# Any doit command will use enhanced context
doit context show

# Output shows new sources:
# - constitution (complete)
# - roadmap (summarized)  # NEW: Shows summarized instead of full
# - completed_roadmap     # NEW: Related completed items
# - current_spec
```

### Configuration (Optional)

To customize summarization behavior, create/edit `.doit/config/context.yaml`:

```yaml
version: 1
enabled: true
max_tokens_per_source: 4000
total_max_tokens: 16000

# Summarization settings
summarization:
  enabled: true                    # Toggle roadmap summarization
  threshold_percentage: 80.0       # Add guidance at 80% of total_max_tokens
  fallback_to_truncation: true     # Truncate when exceeding hard limit
  source_priorities:               # Priority order for truncation
    - constitution                 # Highest priority (kept)
    - roadmap
    - completed_roadmap
    - current_spec
  completed_items:
    max_count: 5                   # Max completed items to include
    min_relevance: 0.3             # Minimum similarity score

sources:
  completed_roadmap:               # NEW source type
    enabled: true
    priority: 3
```

### Disable Features

```yaml
# Disable AI summarization (use truncation only)
summarization:
  enabled: false

# Disable completed items matching
sources:
  completed_roadmap:
    enabled: false
```

## What Changes

### Before

```markdown
<!-- PROJECT CONTEXT -->
## Constitution
[Full constitution content]

## Roadmap
[Full roadmap with all 20+ items]

## Current Spec
[Current spec content]
```

### After

```markdown
<!-- PROJECT CONTEXT -->
## Constitution
[Full constitution content - preserved]

## Roadmap Summary
### High Priority (P1-P2)
- Bug-fix workflow command (doit.fixit) [CURRENT FEATURE]
  - Rationale: Provides structured bug-fix process...

### Other Priorities
- Batch command execution
- CLI plugin architecture
- ...

## Related Completed Work
- AI context injection (completed 2026-01-15, branch: 026-ai-context-injection)
- Memory search and query (completed 2026-01-16, branch: 037-memory-search-query)

## Current Spec
[Current spec content]
```

## Testing the Feature

```bash
# Check context status
doit context show

# Verify roadmap summarization
doit context show --verbose  # Shows original vs summarized tokens

# Test with low threshold to force summarization
# Edit context.yaml: threshold_percentage: 10.0
doit context show
```

## Troubleshooting

### Summarization Not Triggering

1. Check if enabled: `summarization.enabled: true`
2. Verify threshold: may not be reached yet
3. Check logs: `doit --verbose context show`

### Slow Context Loading

1. Disable summarization: `summarization.enabled: false`
2. Reduce total_max_tokens for faster loading
3. Disable less critical sources like `related_specs`

### No Completed Items Showing

1. Check `completed_roadmap.md` exists in `.doit/memory/`
2. Verify `sources.completed_roadmap.enabled: true`
3. Lower relevance threshold: `completed_items.min_relevance: 0.1`

## Key Files

| File | Purpose |
|------|---------|
| `src/doit_cli/services/context_loader.py` | Main context loading logic |
| `src/doit_cli/services/roadmap_summarizer.py` | Roadmap parsing and summarization |
| `src/doit_cli/models/context_config.py` | Configuration models |
| `.doit/config/context.yaml` | User configuration |
| `.doit/memory/roadmap.md` | Source roadmap |
| `.doit/memory/completed_roadmap.md` | Completed items source |
