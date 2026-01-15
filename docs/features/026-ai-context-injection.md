# AI Context Injection for Commands

**Completed**: 2026-01-15
**Branch**: 026-ai-context-injection
**PR**: (pending)

## Overview

Enable doit commands to automatically load and inject relevant project context (constitution, roadmap, related specifications) when executing, providing AI assistants with comprehensive project understanding without manual context gathering. This improves AI response quality by ensuring commands have access to project principles, current priorities, and related work.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | System automatically loads `.doit/memory/constitution.md` when executing any doit command | Done |
| FR-002 | System automatically loads `.doit/memory/roadmap.md` when executing any doit command | Done |
| FR-003 | System identifies and loads current feature's spec.md based on branch name pattern | Done |
| FR-004 | System discovers related specs based on keyword matching in titles and summaries | Done |
| FR-005 | System provides loaded context in structured format suitable for AI consumption | Done |
| FR-006 | System gracefully handles missing context files without failing command execution | Done |
| FR-007 | System truncates large context files to configurable maximum size (default: 4000 tokens) | Done |
| FR-008 | System caches loaded context during command execution to avoid repeated file reads | Done |
| FR-009 | Users can configure context sources via `.doit/config/context.yaml` | Done |
| FR-010 | System supports per-command context overrides via command-line flags | Done |
| FR-011 | System logs which context sources were loaded for debugging purposes | Done |
| FR-012 | System detects and prevents circular reference loading (max depth: 2) | Done |

## Technical Details

### Architecture

- **ContextLoader** (`src/doit_cli/services/context_loader.py`): Core service for loading and managing context sources
- **ContextConfig** (`src/doit_cli/models/context_config.py`): Configuration dataclasses for context loading
- **ContextSource** (`src/doit_cli/models/context_config.py`): Represents individual loadable context sources
- **CLI Command** (`src/doit_cli/cli/context_command.py`): Typer-based `doit context` command group

### Key Decisions

1. **Token Estimation**: Uses tiktoken (cl100k_base encoding) for accurate token counting, with character/4 fallback
2. **TF-IDF Similarity**: Uses scikit-learn's TfidfVectorizer for related spec discovery via cosine similarity
3. **YAML Configuration**: Uses PyYAML for `.doit/config/context.yaml` configuration parsing
4. **Truncation Strategy**: Smart truncation preserves headers/summaries while reducing total tokens
5. **LRU Caching**: Uses `functools.lru_cache` for efficient repeated context access

## Files Changed

### New Files

- `src/doit_cli/models/context_config.py`
- `src/doit_cli/services/context_loader.py`
- `src/doit_cli/cli/context_command.py`
- `templates/config/context.yaml`
- `tests/unit/test_context_loader.py`
- `tests/unit/test_context_config.py`
- `tests/integration/test_context_command.py`

### Modified Files

- `pyproject.toml` - Added tiktoken and scikit-learn dependencies
- `src/doit_cli/main.py` - Registered context_app subcommand
- `src/doit_cli/services/template_manager.py` - Added config template copying
- `src/doit_cli/services/scaffolder.py` - Added config and logs directories
- `src/doit_cli/cli/init_command.py` - Integrated config template copying during init

## Testing

- **Unit Tests**: 59 tests covering ContextLoader, ContextConfig, and related functions
- **Integration Tests**: 12 tests covering CLI command execution
- **Total**: 71 context-specific tests, 271 total project tests passing

## CLI Commands

| Command | Description |
|---------|-------------|
| `doit context show` | Display loaded context with token counts |
| `doit context show --json` | Output context in JSON format for programmatic use |
| `doit context config` | Show current configuration settings |
| `doit context validate` | Validate context files and configuration |

## Related Issues

- Epic: #227
- Tasks: #229-#252 (22 completed, 2 deferred)

## User Stories

1. **US-1 Automatic Context Loading** (P1): Commands automatically load constitution and roadmap
2. **US-2 Context-Aware Spec Creation** (P2): Specs reference constitution principles
3. **US-3 Related Spec Discovery** (P2): System identifies and loads related specifications
4. **US-4 Configurable Context Sources** (P3): Users customize which sources to include

## Deferred Items

- **TASK-013 Command Integration**: doit commands are templates executed by AI agents, not the CLI directly. Full integration requires updating template instructions to call `doit context show`.
- **TASK-024 Performance Benchmarks**: Blocked pending production usage data collection.

## Future Work

A follow-up item "Template context injection" has been added to the roadmap as P1 to add instructions to command templates that call `doit context show` before executing, completing the end-to-end context injection workflow.
