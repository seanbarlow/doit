# Research: GitHub Copilot Prompt File Deprecation

**Feature**: 021-copilot-agent-fix
**Date**: 2026-01-13
**Status**: Complete

## Research Summary

This document captures the research findings for the deprecated `mode: agent` attribute in GitHub Copilot prompt files.

## Decision 1: Frontmatter Attribute Format

**Decision**: Replace `mode: agent` with `agent: true`

**Rationale**:
- VS Code documentation for prompt files (v1.106+) shows `agent` as a supported property
- The `agent` property accepts: `ask`, `edit`, `agent`, or a custom agent name
- Using `agent: true` is equivalent to `agent: agent` (enables agent mode)
- GitHub issue #464 in awesome-copilot confirms `mode` is deprecated

**Alternatives Considered**:
- `agent: agent` - Verbose but explicit
- `mode: agent` - Deprecated, triggers warnings
- Removing the property entirely - Would change default behavior

**Source**: [VS Code Prompt Files Documentation](https://code.visualstudio.com/docs/copilot/customization/prompt-files)

## Decision 2: File Scope

**Decision**: Update files in `/templates/prompts/` and `/src/doit_cli/templates/prompts/` only

**Rationale**:
- These are the source template directories
- Files in `.venv/` are derived artifacts (created by pip install)
- `.venv/` files will update automatically on reinstall

**Alternatives Considered**:
- Update all locations including `.venv/` - Unnecessary, derived artifacts
- Update only one directory - Would cause inconsistency

## Decision 3: Validation Method

**Decision**: Use grep commands for verification

**Rationale**:
- Simple, reliable, no tooling dependencies
- Can verify both negative (no `mode: agent`) and positive (`agent: true`)
- Easily scriptable for CI/CD

**Alternatives Considered**:
- YAML parser validation - Overkill for this simple change
- Manual file inspection - Error-prone at scale

## Technical Findings

### Current VS Code Prompt File Specification

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `description` | string | Optional | Short description of the prompt |
| `name` | string | Optional | Name used after typing `/` in chat |
| `agent` | string | Optional | Agent type: `ask`, `edit`, `agent`, or custom |
| `model` | string | Optional | Language model to use |
| `tools` | array | Optional | Available tools for the prompt |
| `argument-hint` | string | Optional | Hint text in chat input field |

### Deprecated Properties

| Property | Status | Replacement |
|----------|--------|-------------|
| `mode` | Deprecated | Use `agent` instead |

### Reference Implementation

`doit-testit.prompt.md` already uses the correct format:

```yaml
---
agent: true
description: Execute automated tests and generate test reports with requirement mapping
---
```

## Files Requiring Update

| Directory | Files | Current | Required |
|-----------|-------|---------|----------|
| `/templates/prompts/` | 10 | `mode: agent` | `agent: true` |
| `/src/doit_cli/templates/prompts/` | 10 | `mode: agent` | `agent: true` |
| Both | 1 | `agent: true` | No change |

**Total**: 20 files to update, 2 files already correct

## Conclusion

The research confirms:
1. `mode: agent` is deprecated in favor of `agent: true`
2. The change is a simple text replacement on line 2 of each file
3. All other frontmatter properties remain valid and unchanged
4. VS Code 1.106+ is required for prompt file support
