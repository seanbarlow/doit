# Memory Search and Query

**Completed**: 2026-01-16
**Branch**: `037-memory-search-query`
**PR**: [#540](https://github.com/seanbarlow/doit/pull/540)

## Overview

Enables users to search and query across all project context files (constitution, roadmap, completed roadmap, specifications) to find relevant information quickly. This extends the AI context injection system (feature 026) by adding explicit search capabilities that surface related decisions, principles, and historical context on demand.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| US1 | Keyword Search Across Project Memory | Done |
| US2 | Natural Language Query | Done |
| US3 | Search Results Display | Done |
| US4 | Filter Search by Source Type | Done |
| US5 | Search History and Recent Queries | Done |

## Technical Details

### Architecture

- **CLI Layer**: `doit memory search` and `doit memory history` commands via Typer
- **Service Layer**: MemorySearchService (search logic), QueryInterpreter (NLP)
- **Data Layer**: Integration with ContextLoader for file discovery

### Key Design Decisions

1. **Regex-based search with TF-IDF scoring**: Chose regex over full-text search engines (Whoosh, SQLite FTS) to avoid external dependencies while maintaining good relevance scoring
2. **Local NLP interpretation**: Natural language queries use local keyword extraction with question-type classification, no external API calls
3. **Session-scoped history**: Search history is in-memory only, not persisted to disk (v1 scope)
4. **Rich terminal output**: Uses Rich panels with match highlighting for readable results

### Relevance Scoring Formula

```
score = (tf_score * 0.5) + (position_score * 0.3) + (section_bonus * 0.2)
```

- **tf_score**: Term frequency normalized 0-1
- **position_score**: 1.0 for titles/headers, 0.5 for first 100 lines, 0.3 otherwise
- **section_bonus**: 1.0 for Summary/Vision sections, 0.5 for Requirements

## Files Changed

### New Files
- `src/doit_cli/models/search_models.py` - Data models (SearchQuery, SearchResult, MemorySource, etc.)
- `src/doit_cli/services/memory_search.py` - Core search service
- `src/doit_cli/services/query_interpreter.py` - Natural language interpretation
- `src/doit_cli/cli/memory_command.py` - CLI commands
- `tests/unit/test_memory_search.py` - Unit tests (16 tests)
- `tests/unit/test_query_interpreter.py` - Unit tests (39 tests)
- `tests/integration/test_memory_command.py` - Integration tests (20 tests)

### Modified Files
- `src/doit_cli/main.py` - Registered memory_app subcommand
- `src/doit_cli/cli/__init__.py` - Exported memory_app
- `src/doit_cli/models/__init__.py` - Exported search models
- `src/doit_cli/services/context_loader.py` - Added file discovery methods

## Testing

### Automated Tests
- **Unit tests**: 55 tests (16 for memory_search, 39 for query_interpreter)
- **Integration tests**: 20 tests for CLI commands
- **Total**: 75 tests, all passing

### Manual Verification
- Tested `doit memory search authentication` - returns relevant results
- Tested `doit memory search -t natural "what is the project vision?"` - correctly interprets question
- Tested `doit memory search --source specs FR-001` - filters to spec files only
- Tested `doit memory search --json` - outputs valid JSON
- Tested `doit memory history` - shows session history

## Usage Examples

```bash
# Basic keyword search
doit memory search authentication

# Natural language query
doit memory search -t natural "what are the testing requirements?"

# Filter by source type
doit memory search API --source specs

# JSON output for scripting
doit memory search validation --json

# View search history
doit memory history

# Clear history
doit memory history --clear
```

## Related Issues

- Epic: #505
- Features: #506, #509, #510
- Tasks: #518-#539 (21 task issues)
