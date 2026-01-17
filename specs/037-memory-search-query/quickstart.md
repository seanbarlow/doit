# Quickstart: Memory Search and Query

**Feature**: 037-memory-search-query
**Date**: 2026-01-16

## Overview

The memory search feature lets you search across all project context files including the constitution, roadmap, and specifications. This helps you find relevant information quickly without manually browsing files.

## Prerequisites

- doit CLI installed (`pip install doit-cli`)
- Initialized doit project (run `doit init` if needed)
- At least one of: constitution.md, roadmap.md, or spec files

## Basic Usage

### Search for Keywords

```bash
# Find all mentions of "authentication"
doit memory search authentication

# Search for "API" in specifications only
doit memory search API --source specs
```

### Ask Natural Language Questions

```bash
# Ask a question about your project
doit memory search -t natural "what are the testing requirements?"

# Find out about a specific topic
doit memory search -t natural "how does user authentication work?"
```

### Search with Exact Phrases

```bash
# Find exact phrase matches
doit memory search -t phrase "user story"

# Case-sensitive exact match
doit memory search -t phrase -c "API Gateway"
```

## Common Workflows

### 1. Understanding Project Context

When starting work on a new feature, search the memory to understand existing context:

```bash
# Check constitution for relevant principles
doit memory search -s governance "your-feature-topic"

# Find related specs
doit memory search -s specs "related-topic"
```

### 2. Finding Requirements

Search for functional requirements across specs:

```bash
# Find all functional requirements
doit memory search -r "FR-\d{3}"

# Find specific requirement patterns
doit memory search -t phrase "MUST validate"
```

### 3. Checking Completed Work

Search the completed roadmap for past decisions:

```bash
# Find what was done for a topic
doit memory search -s governance "authentication"
```

### 4. Exporting for AI Context

Export search results as JSON for AI agents:

```bash
# Get JSON output for scripting
doit memory search authentication --json > context.json

# Pipe to other tools
doit memory search "error handling" --json | jq '.results'
```

## Output Examples

### Rich Terminal Output

```
Memory Search Results

Query: "authentication" (keyword)
Sources: all | Found: 3 results

─────────────────────────────────────────────────────────

📄 .doit/memory/constitution.md (Score: 0.95)
   Line 42:
   > Users must **authenticate** using secure credentials

─────────────────────────────────────────────────────────

📄 specs/015-user-auth/spec.md (Score: 0.87)
   Line 15:
   > The **authentication** system validates user identity

─────────────────────────────────────────────────────────

Searched 12 files in 0.15s
```

### JSON Output

```json
{
  "query": {"text": "authentication", "type": "keyword"},
  "results": [
    {
      "source": {"path": ".doit/memory/constitution.md"},
      "relevance_score": 0.95,
      "line_number": 42,
      "matched_text": "authenticate"
    }
  ],
  "metadata": {"total_results": 3}
}
```

## Tips

1. **Start broad, then narrow**: Begin with simple keyword searches, then add filters
2. **Use natural language for questions**: The `-t natural` type understands questions
3. **Check governance first**: Constitution and roadmap often have key context
4. **Export to JSON for AI**: Use `--json` when feeding results to AI agents
5. **View history**: Use `doit memory history` to recall recent searches

## Troubleshooting

### "Memory directory not found"

Run `doit init` to initialize the project structure.

### "No results found"

- Try a simpler query term
- Remove filters to search all sources
- Check spelling and try synonyms

### Search is slow

- Large projects (>100 specs) may take longer
- Use `--source` to limit search scope
- Use `--max` to limit result count

## Next Steps

- Read the full [spec.md](spec.md) for detailed requirements
- Check [contracts/memory-cli.md](contracts/memory-cli.md) for complete CLI reference
- Review [data-model.md](data-model.md) for entity definitions
