# Research: AI Context Injection for Commands

**Feature**: 026-ai-context-injection
**Date**: 2026-01-15
**Status**: Complete

## Research Questions

### RQ-001: Token Counting Strategy

**Question**: How to accurately estimate token counts for context truncation?

**Decision**: Use `tiktoken` library (OpenAI's official tokenizer)

**Rationale**:

- Industry standard for token estimation
- Fast performance (Rust-based)
- Accurate for GPT/Claude model families
- Already widely used in AI tooling

**Alternatives Considered**:

- Character-based estimation (4 chars ≈ 1 token): Too imprecise, varies by content type
- Word-based estimation: Better but still varies significantly by vocabulary
- No estimation (fixed char limit): Doesn't optimize context usage

**Implementation Note**: Use `cl100k_base` encoding for GPT-4/Claude compatibility. If tiktoken is unavailable, fall back to character/4 estimate.

---

### RQ-002: Related Spec Discovery Algorithm

**Question**: How to identify semantically related specifications?

**Decision**: Keyword-based matching with TF-IDF similarity scoring

**Rationale**:

- Lightweight - no ML models or embeddings required
- Fast enough for real-time use (< 100ms for 50 specs)
- Good precision for technical documentation
- Easy to debug and tune

**Alternatives Considered**:

- Embedding similarity (sentence-transformers): Requires ML dependencies, slower, overkill for markdown docs
- Exact keyword matching: Too rigid, misses related terms
- LLM-based analysis: Too slow and expensive for real-time use

**Implementation Note**:

1. Extract keywords from title and first paragraph (summary)
2. Build TF-IDF vectors for all specs
3. Compute cosine similarity
4. Return top 3 matches above 0.3 threshold

---

### RQ-003: Configuration Format

**Question**: What format for context configuration?

**Decision**: YAML in `.doit/config/context.yaml`

**Rationale**:

- Consistent with existing `hooks.yaml` pattern in this project
- Human-readable and easy to edit
- PyYAML already a project dependency
- Supports nested structures for per-command overrides

**Alternatives Considered**:

- JSON: Less readable, no comments support
- TOML: Another dependency, less familiar to users
- Environment variables: Poor for complex configuration

**Configuration Schema**:

```yaml
# .doit/config/context.yaml
version: 1

# Global settings
enabled: true
max_tokens_per_source: 4000
total_max_tokens: 16000

# Source configuration
sources:
  constitution:
    enabled: true
    priority: 1
  roadmap:
    enabled: true
    priority: 2
  current_spec:
    enabled: true
    priority: 3
  related_specs:
    enabled: true
    priority: 4
    max_count: 3

# Per-command overrides (optional)
commands:
  specit:
    sources:
      related_specs:
        enabled: false  # Don't load related when creating new
```

---

### RQ-004: Context Caching Strategy

**Question**: How to cache loaded context efficiently?

**Decision**: In-memory cache scoped to command execution (no persistence)

**Rationale**:

- Context changes frequently (files edited between commands)
- Simple implementation with no cache invalidation complexity
- Memory overhead is minimal for typical projects
- No additional dependencies

**Alternatives Considered**:

- File-based cache with timestamps: Adds complexity, cache invalidation issues
- Persistent memory cache: Overkill for CLI tool, stale data risk
- No caching: Acceptable but slower for multiple context accesses per command

**Implementation Note**: Use a simple dict keyed by file path, cleared after each command completes.

---

### RQ-005: Truncation Strategy

**Question**: How to truncate large context files while preserving value?

**Decision**: Smart truncation preserving structure

**Rationale**:

- Markdown headers provide semantic structure
- Summaries and key sections at top are most important
- Truncation should be transparent to AI (no broken syntax)

**Truncation Algorithm**:

1. If file fits within limit → return full content
2. Extract and preserve:
   - Title (first H1)
   - All H2 headers with first paragraph under each
   - Any "Summary" or "Overview" sections in full
3. Add truncation notice: `<!-- Content truncated. Full file at: {path} -->`
4. Fill remaining tokens with content from top of file

**Alternatives Considered**:

- Simple head truncation: Loses structure, may cut mid-sentence
- Tail truncation: Misses conclusions and later sections
- Random sampling: Incoherent context

---

### RQ-006: Integration Point

**Question**: Where to inject context into command execution?

**Decision**: Inject via template variables in command prompt files

**Rationale**:

- Commands already use template files in `.claude/commands/`
- Can add `$PROJECT_CONTEXT` variable that gets replaced
- Non-invasive to existing command structure
- Easy to opt-out by not using the variable

**Alternatives Considered**:

- CLI middleware: Too complex, affects all commands
- Environment variables: Size limits, encoding issues
- Separate context file: AI must be instructed to read it

**Implementation Note**: Add `<!-- PROJECT_CONTEXT -->` marker in command templates that gets replaced with loaded context during execution.

---

## Dependencies Analysis

### Required New Dependencies

| Dependency | Purpose | Version | Notes |
|------------|---------|---------|-------|
| tiktoken | Token counting | ^0.5.0 | Optional - fallback to char/4 |
| scikit-learn | TF-IDF similarity | ^1.3.0 | Optional - fallback to keyword match |

### Existing Dependencies (No Changes)

- PyYAML: Already used for hooks configuration
- Rich: Already used for terminal output
- Typer: Already used for CLI framework

### Optional Dependency Strategy

Make advanced features optional:

- If `tiktoken` unavailable: Use character-based estimate
- If `scikit-learn` unavailable: Use simple keyword matching

This keeps core context loading working without heavy dependencies.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance overhead too high | Low | Medium | Caching, lazy loading, benchmarks |
| Token estimation inaccurate | Medium | Low | Fall back to conservative estimates |
| Related spec matching poor | Medium | Medium | Tune similarity threshold, manual override |
| Large projects slow | Low | Medium | Limit spec scanning, pagination |

---

## Conclusion

All research questions resolved. Proceed to Phase 1 design with:

- tiktoken for token counting (optional)
- TF-IDF for related spec discovery (optional, fallback to keywords)
- YAML configuration consistent with existing patterns
- In-memory caching per command execution
- Smart truncation preserving markdown structure
- Template variable injection for context
