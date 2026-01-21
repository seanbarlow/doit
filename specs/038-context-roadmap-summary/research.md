# Research: Context Roadmap Summary

**Feature**: `038-context-roadmap-summary`
**Date**: 2026-01-20

## Research Questions

### Q1: How should roadmap items be prioritized and summarized?

**Decision**: Parse roadmap by priority sections (P1-P4) and generate a condensed summary that includes all P1/P2 items with their rationale, while condensing P3/P4 to just titles.

**Rationale**:
- P1/P2 items represent critical and high-priority work that AI needs full context on
- P3/P4 items provide awareness without consuming excessive tokens
- Maintaining rationale for high-priority items helps AI understand the "why"

**Alternatives Considered**:
1. Include all items equally - rejected because it doesn't optimize for token limits
2. Only include P1 items - rejected because P2 items also provide valuable context
3. Use semantic similarity to select items - rejected as overly complex for initial implementation

### Q2: How should completed roadmap items be matched to current features?

**Decision**: Include all completed roadmap items in the context, formatted with metadata (date, branch, description), and let the AI coding agent (Claude or Copilot) determine relevance semantically.

**Rationale**:
- The AI coding agent already has superior semantic understanding capabilities
- No need to implement complex TF-IDF or embedding matching when the AI can do this better
- Simpler implementation with better results
- AI can understand context nuances that keyword matching would miss

**Alternatives Considered**:
1. TF-IDF similarity scoring - rejected in favor of leveraging existing AI capabilities
2. AI embeddings for semantic search - rejected as unnecessarily complex when AI agent handles this
3. Simple substring matching - rejected as too imprecise
4. Manual tagging in roadmap - rejected as adding maintenance burden

### Q3: How should AI summarization be implemented?

**Decision**: Leverage the current AI coding agent (Claude or Copilot) for summarization. The agent running the doit command IS the summarizer - no external API calls needed.

**Rationale**:
- The AI coding agent is already present in the session when doit commands run
- Works identically for Claude Code, Copilot, Cursor, or any AI agent
- No external API dependency or subscription requirements
- The AI naturally understands priority and relevance

**Implementation**:
1. **Default**: Provide well-structured context with clear P1/P2/P3/P4 priorities
2. **Over threshold**: Include a prompt asking the current AI agent to focus on high-priority items
3. **Hard limit**: Simple truncation only if absolutely necessary

This approach treats the AI agent as a partner in context management rather than requiring separate API calls.

**Alternatives Considered**:
1. Local summarization with transformers - rejected due to added dependency weight
2. Rule-based summarization only - rejected as insufficient for maintaining coherence
3. Multiple AI providers - rejected as over-engineering for initial implementation

### Q4: Where should summarization configuration be stored?

**Decision**: Extend existing ContextConfig with a nested `summarization` section in `.doit/config/context.yaml`.

**Rationale**:
- ContextConfig already handles context loading configuration
- Users familiar with context.yaml can add summarization settings naturally
- Maintains single source of truth for context behavior

**Alternatives Considered**:
1. Separate `summarization.yaml` file - rejected to avoid configuration sprawl
2. Environment variables - rejected as less discoverable and harder to version control
3. Command-line flags only - rejected as not persistent

### Q5: What token threshold triggers AI summarization?

**Decision**: Default threshold of 80% of `total_max_tokens` config value. Configurable via `summarization.threshold_percentage` (default: 80).

**Rationale**:
- 80% provides buffer for final formatting and injection overhead
- Percentage-based approach scales with different token limit configurations
- Consistent with existing truncation behavior that kicks in near limits

**Alternatives Considered**:
1. Fixed token count - rejected as not adapting to user configuration
2. Per-source thresholds - rejected as overly complex
3. No threshold (always summarize) - rejected due to unnecessary API calls

## Technical Decisions

### Extending ContextConfig

Add to context_config.py:
```python
@dataclass
class SummarizationConfig:
    enabled: bool = True
    threshold_percentage: float = 80.0
    source_priorities: list[str] = field(default_factory=lambda: ["constitution", "roadmap", "completed_roadmap"])
    timeout_seconds: float = 10.0
    fallback_to_truncation: bool = True
```

### Roadmap Parsing Strategy

1. Parse markdown sections by H3 headers (### P1 - Critical, ### P2 - High, etc.)
2. Extract checklist items with format: `- [ ] Item text\n  - **Rationale**: ...`
3. Preserve feature branch references in backticks: `` `[###-feature-name]` ``
4. Generate summary markdown maintaining priority structure

### Completed Item Matching

1. Extract keywords from current branch name (split on `-` and numbers)
2. Extract keywords from spec title
3. Parse completed_roadmap.md table rows
4. Calculate TF-IDF similarity scores
5. Return top N items (default 3) above threshold (0.3)

### AI Summarization Flow

```
1. Calculate total tokens across all sources
2. If total > threshold:
   a. Build summarization prompt with source attribution
   b. Call Claude API with timeout
   c. On success: use summarized content
   d. On failure: fall back to truncation
3. Return final context
```

## Integration Points

### Existing Code to Modify

1. **context_loader.py**: Add summarization logic after loading sources
2. **context_config.py**: Add SummarizationConfig dataclass
3. **memory_search.py**: Reuse `extract_keywords()` function

### New Code to Create

1. **roadmap_summarizer.py**: Service for parsing and summarizing roadmap
2. **completed_matcher.py**: Service for matching completed items (or add to context_loader)

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| AI API unavailable | Fallback to truncation with warning |
| Slow summarization | Timeout with configurable duration |
| Poor keyword matching | Adjustable similarity threshold |
| Breaking existing behavior | Default config preserves current behavior |

## Dependencies

- No new external dependencies required
- Reuses existing: httpx, tiktoken (optional), sklearn (optional)
