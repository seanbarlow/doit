# Quickstart: AI Context Injection

**Feature**: 026-ai-context-injection
**Date**: 2026-01-15

## Overview

This guide covers setting up the development environment and running the AI Context Injection feature.

## Prerequisites

- Python 3.11+
- Git
- doit-toolkit-cli installed in editable mode

## Development Setup

### 1. Install Dependencies

```bash
# From repository root
pip install -e .

# Optional: Install advanced features
pip install tiktoken scikit-learn
```

### 2. Verify Installation

```bash
# Check doit is available
doit --version

# Check context loading (once implemented)
doit context status
```

## Project Structure

```text
src/doit_cli/
├── models/
│   └── context_config.py    # ContextConfig, SourceConfig dataclasses
├── services/
│   └── context_loader.py    # ContextLoader service
└── __init__.py              # CLI commands

.doit/config/
└── context.yaml             # Context configuration

tests/
├── unit/
│   ├── test_context_config.py
│   └── test_context_loader.py
└── integration/
    └── test_context_injection.py
```

## Configuration

### Default Configuration

Context loading works out of the box with sensible defaults:

- Constitution: Enabled, priority 1
- Roadmap: Enabled, priority 2
- Current spec: Enabled, priority 3
- Related specs: Enabled, priority 4, max 3

### Custom Configuration

Create `.doit/config/context.yaml` to customize:

```yaml
version: 1

# Disable context loading entirely
enabled: false

# Or customize sources
sources:
  related_specs:
    enabled: false

# Per-command overrides
commands:
  specit:
    sources:
      related_specs:
        enabled: false
```

## Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Context-specific tests
pytest tests/unit/test_context_loader.py -v

# With coverage
pytest tests/ --cov=src/doit_cli --cov-report=html
```

## Manual Testing

### Test Context Loading

```bash
# Create a test project
mkdir test-project && cd test-project
doit init

# Create constitution
mkdir -p .doit/memory
echo "# Test Constitution" > .doit/memory/constitution.md

# Create a feature branch
git checkout -b 001-test-feature

# Run a command and verify context is loaded
doit specit "test feature" --debug
```

### Test Configuration

```bash
# Create custom config
mkdir -p .doit/config
cat > .doit/config/context.yaml << 'EOF'
version: 1
sources:
  roadmap:
    enabled: false
EOF

# Run command and verify roadmap not loaded
doit specit "test feature" --debug
```

## Debugging

### Enable Debug Logging

```bash
# Set environment variable
export DOIT_DEBUG=1

# Or use --debug flag
doit specit "feature" --debug
```

### Check Loaded Context

```bash
# Show what context would be loaded
doit context show

# Show context for specific command
doit context show --command specit
```

## Common Issues

### Context Not Loading

1. Check `.doit/memory/` directory exists
2. Verify constitution.md/roadmap.md are present
3. Check config file syntax: `cat .doit/config/context.yaml`

### Token Count Warnings

If you see "Token estimation using fallback":
- Install tiktoken: `pip install tiktoken`
- Or accept character-based estimation (less accurate)

### Related Specs Not Found

1. Verify you're on a feature branch (e.g., `026-feature-name`)
2. Check specs directory exists: `ls specs/`
3. Verify spec has title and summary for matching

## Next Steps

After implementation:

1. Run `/doit.taskit` to generate implementation tasks
2. Implement with `/doit.implementit`
3. Test with `/doit.testit`
4. Review with `/doit.reviewit`
5. Finalize with `/doit.checkin`
