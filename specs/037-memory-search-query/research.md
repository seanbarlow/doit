# Research: Memory Search and Query

**Feature**: 037-memory-search-query
**Date**: 2026-01-16
**Status**: Complete

## Research Topics

### 1. Text Search Implementation in Python

**Decision**: Use regex-based search with optional TF-IDF for relevance scoring

**Rationale**:
- Regex provides flexible pattern matching without external dependencies
- Project already has sklearn available (used in context_loader.py for TF-IDF similarity)
- No need for full-text search engine (Elasticsearch, Whoosh) for file-based scope
- Streaming search handles large files without memory issues

**Alternatives Considered**:
- Whoosh (pure Python full-text search): Rejected - adds dependency, overkill for <100 files
- SQLite FTS5: Rejected - requires database migration, adds complexity
- ripgrep subprocess: Rejected - external binary dependency

### 2. Integration with Existing Context Loader

**Decision**: Extend ContextLoader with search-specific methods

**Rationale**:
- ContextLoader already handles file discovery and loading
- Reuse `_discover_related_specs()` for spec file enumeration
- Reuse `estimate_tokens()` for result truncation
- Add new `search_content()` method that returns matched snippets

**Integration Points**:
- `ContextLoader.load_source()` - reuse for reading files
- `ContextLoader._get_memory_files()` - reuse for governance files
- `ContextLoader._discover_specs()` - reuse for spec enumeration
- `LoadedContext` model - extend with search result metadata

### 3. Natural Language Query Interpretation

**Decision**: Keyword extraction with question-type classification

**Rationale**:
- No external API calls required (v1 constraint)
- Simple pattern matching for question types (what, why, how, where)
- Extract noun phrases and technical terms as search keywords
- Use TF-IDF weighting from existing sklearn integration

**Approach**:
1. Classify question type (factual, procedural, definitional)
2. Extract keywords by removing stop words
3. Identify section hints ("vision" → look in Vision section)
4. Generate search query from extracted terms

**Alternatives Considered**:
- spaCy NLP: Rejected - adds large dependency (~500MB)
- OpenAI API: Rejected - violates v1 constraint (no external APIs)
- NLTK: Rejected - heavy dependency for simple keyword extraction

### 4. Relevance Scoring Algorithm

**Decision**: Hybrid scoring with term frequency and position weighting

**Rationale**:
- Term frequency (TF) measures keyword density
- Position weighting prioritizes matches in headers/titles
- Section bonus for matches in key sections (Summary, Vision)
- Decay factor for very long documents

**Scoring Formula**:
```
score = (tf_score * 0.5) + (position_score * 0.3) + (section_bonus * 0.2)

where:
- tf_score = matches / total_words (normalized 0-1)
- position_score = 1.0 if in title/header, 0.5 if in first 100 lines, 0.3 otherwise
- section_bonus = 1.0 if in Summary/Vision, 0.5 if in Requirements, 0.0 otherwise
```

### 5. Result Display and Highlighting

**Decision**: Rich-based terminal output with ANSI highlighting

**Rationale**:
- Project already uses Rich for all CLI output
- Rich supports text highlighting with markup
- Consistent with existing commands (status, analytics)
- JSON output uses standard json.dumps for machine readability

**Display Format**:
```
┌─ .doit/memory/roadmap.md:15 ─────────── Score: 0.85 ─┐
│ ...the **validation** workflow ensures quality...    │
└──────────────────────────────────────────────────────┘
```

### 6. Source Type Classification

**Decision**: Three source types: governance, specs, all

**Rationale**:
- Governance: constitution.md, roadmap.md, completed_roadmap.md
- Specs: All spec.md files in specs/ directory
- All: Default, searches everything
- Simple classification, no need for complex taxonomy

**File Mapping**:
| Source Type | Files |
|-------------|-------|
| governance | `.doit/memory/constitution.md`, `.doit/memory/roadmap.md`, `.doit/memory/completed_roadmap.md` |
| specs | `specs/*/spec.md` |
| all | governance + specs |

### 7. Search History Implementation

**Decision**: Session-based in-memory list (not persisted)

**Rationale**:
- v1 scope limits to session-based history
- Simple list with timestamps
- No file I/O overhead
- Can add persistence in future version

**Data Structure**:
```python
@dataclass
class SearchHistoryEntry:
    query: str
    query_type: str  # "search" or "ask"
    timestamp: datetime
    result_count: int
```

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| How to handle large files? | Streaming search with line-by-line processing |
| How to highlight matches in Rich? | Use `rich.markup` with `[bold red]term[/]` syntax |
| How to integrate with context_loader? | Extend with search methods, reuse file discovery |
| What NLP approach for questions? | Keyword extraction + question classification |
| How to score relevance? | Hybrid TF + position + section scoring |

## Dependencies Confirmed

| Dependency | Purpose | Already Available |
|------------|---------|-------------------|
| rich | Terminal output, highlighting | Yes |
| typer | CLI framework | Yes |
| sklearn | TF-IDF scoring (optional) | Yes |
| re | Regex search | Yes (stdlib) |
| dataclasses | Models | Yes (stdlib) |

## Next Steps

Proceed to Phase 1: Generate data-model.md and contracts/memory-cli.md
