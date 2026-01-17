# CLI Contract: Memory Search Commands

**Feature**: 037-memory-search-query
**Date**: 2026-01-16

## Command Overview

```bash
doit memory search <query> [OPTIONS]
doit memory history [OPTIONS]
```

## Commands

### `doit memory search`

Search across all project memory files (constitution, roadmap, specs).

#### Synopsis

```bash
doit memory search <QUERY> [--type TYPE] [--source SOURCE] [--max MAX] [--case-sensitive] [--regex] [--json]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `QUERY` | string | Yes | Search term, phrase, or natural language question |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--type` | `-t` | enum | `keyword` | Query type: `keyword`, `phrase`, `natural`, `regex` |
| `--source` | `-s` | enum | `all` | Source filter: `all`, `governance`, `specs` |
| `--max` | `-m` | int | `20` | Maximum results to return (1-100) |
| `--case-sensitive` | `-c` | flag | `false` | Enable case-sensitive matching |
| `--regex` | `-r` | flag | `false` | Interpret query as regular expression |
| `--json` | `-j` | flag | `false` | Output results as JSON |

#### Query Types

| Type | Behavior | Example |
|------|----------|---------|
| `keyword` | Searches for individual words, partial matches allowed | `doit memory search authentication` |
| `phrase` | Exact phrase matching (like quoted search) | `doit memory search -t phrase "user login"` |
| `natural` | Interprets as question, extracts keywords | `doit memory search -t natural "how do users authenticate?"` |
| `regex` | Regular expression pattern matching | `doit memory search -r "auth(entication\|orization)"` |

#### Source Filters

| Filter | Files Searched |
|--------|----------------|
| `all` | All memory files and specs |
| `governance` | `.doit/memory/constitution.md`, `.doit/memory/roadmap.md`, `.doit/memory/completed_roadmap.md` |
| `specs` | All `specs/*/spec.md` files |

#### Output Format (Rich Terminal)

```
Memory Search Results

Query: "authentication" (keyword)
Sources: all | Found: 5 results

─────────────────────────────────────────────────────────

📄 .doit/memory/constitution.md (Score: 0.95)
   Line 42:
   > Users must **authenticate** using secure credentials

─────────────────────────────────────────────────────────

📄 specs/015-user-auth/spec.md (Score: 0.87)
   Line 15:
   > The **authentication** system validates user identity

─────────────────────────────────────────────────────────

[3 more results...]

Searched 45 files in 0.23s
```

#### Output Format (JSON)

```json
{
  "query": {
    "text": "authentication",
    "type": "keyword",
    "source_filter": "all",
    "case_sensitive": false
  },
  "results": [
    {
      "id": "result-001",
      "source": {
        "path": ".doit/memory/constitution.md",
        "type": "governance"
      },
      "relevance_score": 0.95,
      "line_number": 42,
      "matched_text": "authenticate",
      "context": {
        "before": "Users must ",
        "match": "authenticate",
        "after": " using secure credentials"
      }
    }
  ],
  "metadata": {
    "total_results": 5,
    "files_searched": 45,
    "execution_time_ms": 230
  }
}
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (results found or no results) |
| `1` | Invalid arguments or options |
| `2` | File system error (cannot read files) |
| `3` | Invalid regex pattern |

#### Examples

```bash
# Basic keyword search
doit memory search authentication

# Exact phrase search
doit memory search -t phrase "user story"

# Natural language query
doit memory search -t natural "what are the testing requirements?"

# Search only in specs with regex
doit memory search -s specs -r "FR-\d{3}"

# Case-sensitive search with max results
doit memory search -c -m 10 "API"

# JSON output for scripting
doit memory search authentication --json | jq '.results[0]'
```

---

### `doit memory history`

View recent search queries from the current session.

#### Synopsis

```bash
doit memory history [--clear] [--json]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--clear` | `-c` | flag | `false` | Clear search history |
| `--json` | `-j` | flag | `false` | Output history as JSON |

#### Output Format (Rich Terminal)

```
Search History (Session)

Started: 2026-01-16 10:30:00

 # │ Time     │ Query                  │ Type    │ Results
───┼──────────┼────────────────────────┼─────────┼─────────
 1 │ 10:30:15 │ authentication         │ keyword │ 5
 2 │ 10:32:42 │ "user login"           │ phrase  │ 2
 3 │ 10:35:18 │ how do users auth...   │ natural │ 8

3 queries this session
```

#### Output Format (JSON)

```json
{
  "session_id": "sess-abc123",
  "session_start": "2026-01-16T10:30:00Z",
  "entries": [
    {
      "query_text": "authentication",
      "query_type": "keyword",
      "timestamp": "2026-01-16T10:30:15Z",
      "result_count": 5
    }
  ],
  "total_entries": 3
}
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | No history available |

#### Examples

```bash
# View search history
doit memory history

# Clear history
doit memory history --clear

# Export history as JSON
doit memory history --json > search_history.json
```

---

## Validation Rules

### Query Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| V-001 | Query text not empty | "Query cannot be empty" |
| V-002 | Query length <= 500 chars | "Query exceeds maximum length of 500 characters" |
| V-003 | Valid regex (if --regex) | "Invalid regex pattern: {error}" |

### Option Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| V-004 | `--max` between 1-100 | "Max results must be between 1 and 100" |
| V-005 | `--type` is valid enum | "Invalid query type. Use: keyword, phrase, natural, regex" |
| V-006 | `--source` is valid enum | "Invalid source filter. Use: all, governance, specs" |
| V-007 | `--regex` and `--type regex` are equivalent | Warning: "--regex flag sets type to regex" |

---

## Error Handling

### User Errors

```bash
# Empty query
$ doit memory search ""
Error: Query cannot be empty

# Invalid max value
$ doit memory search auth --max 500
Error: Max results must be between 1 and 100

# Invalid regex
$ doit memory search -r "[invalid("
Error: Invalid regex pattern: missing closing bracket
```

### System Errors

```bash
# Memory directory not found
$ doit memory search auth
Error: Memory directory not found. Run 'doit init' to initialize project.

# Permission denied
$ doit memory search auth
Error: Cannot read file: .doit/memory/constitution.md (Permission denied)
```

---

## Integration Points

### Context Loader (Feature 026)

The memory search command integrates with the existing `ContextLoader` service:

```python
# Uses existing context loader to enumerate files
from doit_cli.services.context_loader import ContextLoader

loader = ContextLoader()
files = loader.get_memory_files()  # Returns governance files
specs = loader.get_spec_files()    # Returns spec files
```

### Slash Command Integration

The `/doit.memory` slash command wraps the CLI:

```markdown
/doit.memory search authentication
# Equivalent to: doit memory search authentication

/doit.memory what are the testing requirements?
# Equivalent to: doit memory search -t natural "what are the testing requirements?"
```

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search latency | < 5 seconds | For projects with < 100 spec files |
| Memory usage | < 50 MB | Peak memory during search |
| File size limit | 1 MB | Maximum file size to index |

---

## Accessibility

- All output includes screen-reader friendly text alternatives
- Color is not the only indicator (uses symbols: 📄, ✓, ✗)
- JSON output available for programmatic access
- Respects `NO_COLOR` environment variable
