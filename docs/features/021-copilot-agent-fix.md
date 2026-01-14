# GitHub Copilot Prompt File Fix

**Completed**: 2026-01-13
**Branch**: `021-copilot-agent-fix`
**PR**: #139

## Overview

Updated Do-It's GitHub Copilot prompt files (`.prompt.md`) to use the current (non-deprecated) YAML frontmatter specification. Changed the deprecated `mode: agent` attribute to `agent: true` across all prompt files, ensuring compatibility with VS Code 1.106+ and the current GitHub Copilot prompt file specification.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Replace `mode: agent` with `agent: true` | Done |
| FR-002 | `agent: true` on line 2 | Done |
| FR-003 | `description` on line 3 | Done |
| FR-004 | Preserve all other properties | Done |
| FR-005 | Update /templates/prompts/ (10 files) | Done |
| FR-006 | Update /src/doit_cli/templates/prompts/ (10 files) | Done |
| FR-007 | Do not modify .venv/ | Done |
| FR-008-017 | Update all 10 specific prompt files | Done |
| FR-018 | doit-testit.prompt.md unchanged | Done |
| FR-019 | Zero deprecated syntax remaining | Done |
| FR-020 | 22 files with correct syntax | Done |

## Technical Details

- **Change Type**: YAML frontmatter text replacement
- **Files Modified**: 20 prompt files (10 per directory)
- **Line Changed**: Line 2 in each file
- **Before**: `mode: agent`
- **After**: `agent: true`

## Files Changed

### templates/prompts/
- doit-checkin.prompt.md
- doit-constitution.prompt.md
- doit-documentit.prompt.md
- doit-implementit.prompt.md
- doit-planit.prompt.md
- doit-reviewit.prompt.md
- doit-roadmapit.prompt.md
- doit-scaffoldit.prompt.md
- doit-specit.prompt.md
- doit-taskit.prompt.md

### src/doit_cli/templates/prompts/
- (Same 10 files as above)

## Testing

- **Automated tests**: Validation via grep commands (22 files verified)
- **Manual tests**: 3/3 passed
  - MT-001: No deprecation warnings in VS Code
  - MT-002: Prompt executes in agent mode
  - MT-003: Consistent format across directories

## Related Issues

- Epic: #133
- Features: #134, #135
- Tasks: #136, #137, #138
