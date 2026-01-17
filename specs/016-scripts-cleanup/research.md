# Research: Scripts Cleanup and Agent Support Standardization

**Feature**: 016-scripts-cleanup
**Date**: 2026-01-12

## Executive Summary

This research documents the current state of scripts in the doit repository and identifies all locations requiring cleanup to remove unsupported AI agent references. The cleanup is straightforward with changes concentrated in two primary files.

## Current State Analysis

### Script Inventory

| Location | Bash Scripts | PowerShell Scripts | Status |
| -------- | ------------ | ------------------ | ------ |
| scripts/ | 5 files | 5 files | Source of truth |
| templates/scripts/ | 5 files | 0 files | Missing PowerShell |

### Agent References by File

#### Files WITH Agent References (Need Cleanup)

| File | Agent Count | Cleanup Required |
| ---- | ----------- | ---------------- |
| scripts/bash/update-agent-context.sh | 17 agents | Remove 15 unsupported |
| scripts/powershell/update-agent-context.ps1 | 17 agents | Remove 15 unsupported |
| templates/scripts/bash/update-agent-context.sh | 17 agents | Will sync from scripts/ |

#### Files WITHOUT Agent References (No Changes Needed)

- scripts/bash/common.sh - Utility functions only
- scripts/bash/check-prerequisites.sh - Prerequisite validation only
- scripts/bash/create-new-feature.sh - Feature creation only
- scripts/bash/setup-plan.sh - Plan setup only
- scripts/powershell/common.ps1 - Utility functions only
- scripts/powershell/check-prerequisites.ps1 - Prerequisite validation only
- scripts/powershell/create-new-feature.ps1 - Feature creation only
- scripts/powershell/setup-plan.ps1 - Plan setup only

### Unsupported Agents to Remove

The following 15 agents must be removed from scripts (keeping only `claude` and `copilot`):

1. gemini - Gemini CLI
2. cursor-agent - Cursor IDE
3. qwen - Qwen Code
4. opencode - opencode
5. codex - Codex CLI
6. windsurf - Windsurf
7. kilocode - Kilo Code
8. auggie - Auggie CLI
9. roo - Roo Code
10. codebuddy - CodeBuddy CLI
11. qoder - Qoder CLI
12. amp - Amp
13. shai - SHAI
14. q - Amazon Q Developer CLI
15. bob - IBM Bob

### Code Locations Requiring Changes (update-agent-context.sh)

#### 1. Header Comments (Lines 31-39)

```bash
# Current:
# 5. Multi-Agent Support
#    - Supports: Claude, Gemini, Copilot, Cursor, Qwen, opencode, Codex, Windsurf, Kilo Code, Auggie CLI, Roo Code, CodeBuddy CLI, Qoder CLI, Amp, SHAI, or Amazon Q Developer CLI
#
# Usage: ./update-agent-context.sh [agent_type]
# Agent types: claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|shai|q|bob|qoder

# Should be:
# 5. Multi-Agent Support
#    - Supports: Claude Code, GitHub Copilot
#
# Usage: ./update-agent-context.sh [agent_type]
# Agent types: claude|copilot
```

#### 2. Agent File Path Variables (Lines 62-77)

Remove these variable declarations:
- GEMINI_FILE
- CURSOR_FILE
- QWEN_FILE
- AGENTS_FILE (used by multiple agents)
- WINDSURF_FILE
- KILOCODE_FILE
- AUGGIE_FILE
- ROO_FILE
- CODEBUDDY_FILE
- QODER_FILE
- AMP_FILE
- SHAI_FILE
- Q_FILE
- BOB_FILE

Keep only:
- CLAUDE_FILE
- COPILOT_FILE

#### 3. update_specific_agent() Function (Lines 581-642)

Remove case statements for all unsupported agents. Keep only:
- claude
- copilot

#### 4. update_all_existing_agents() Function (Lines 644-728)

Remove file existence checks for all unsupported agents. Keep only:
- CLAUDE_FILE
- COPILOT_FILE

#### 5. print_summary() Function (Lines 729-748)

Update usage text to show only supported agents.

### Code Locations Requiring Changes (update-agent-context.ps1)

#### 1. Header/Synopsis (Lines 1-25)

Update .DESCRIPTION to list only Claude and Copilot.

#### 2. ValidateSet Parameter (Lines 26-30)

```powershell
# Current:
[ValidateSet('claude','gemini','copilot','cursor-agent','qwen','opencode','codex','windsurf','kilocode','auggie','roo','codebuddy','amp','shai','q','bob','qoder')]

# Should be:
[ValidateSet('claude','copilot')]
```

#### 3. Agent File Path Variables (Lines 47-62)

Remove all variables except CLAUDE_FILE and COPILOT_FILE.

#### 4. Update-SpecificAgent Function (Lines 368-393)

Remove switch cases for unsupported agents.

#### 5. Update-AllExistingAgents Function (Lines 395-418)

Remove file checks for unsupported agents.

#### 6. Print-Summary Function (Lines 420-428)

Update usage text.

## Synchronization Status

### scripts/bash/ vs templates/scripts/bash/

```
diff -r scripts/bash templates/scripts/bash
(no output - files are identical)
```

**Status**: IN SYNC

### templates/scripts/powershell/

**Status**: DIRECTORY MISSING

This directory needs to be created and populated with copies of scripts/powershell/.

## CLI Verification Requirements

### doit init Command

The CLI init command copies scripts from templates/scripts/ to the user's .doit/scripts/ directory. After cleanup:

1. `doit init . --agent claude` should work correctly
2. `doit init . --agent copilot` should work correctly
3. Copied scripts should only reference claude and copilot

### doit check Command

Should verify project configuration is valid.

## Implementation Recommendations

### Order of Operations

1. **Clean scripts/bash/update-agent-context.sh** - Primary source file
2. **Clean scripts/powershell/update-agent-context.ps1** - PowerShell equivalent
3. **Create templates/scripts/powershell/** - Missing directory
4. **Sync scripts/ to templates/scripts/** - Distribution copies
5. **Verify CLI commands** - End-to-end testing

### Testing Strategy

After cleanup, run these verification commands:

```bash
# Verify no unsupported agents remain
grep -ri "gemini\|codebuddy\|cursor-agent\|qwen\|opencode\|codex\|windsurf\|kilocode\|auggie\|roo\|amp\|shai\|\bq\b\|bob\|qoder" scripts/ templates/scripts/

# Verify scripts are synchronized
diff -r scripts/bash templates/scripts/bash
diff -r scripts/powershell templates/scripts/powershell

# Test script help output
./scripts/bash/update-agent-context.sh --help
pwsh ./scripts/powershell/update-agent-context.ps1 -Help
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Breaking existing scripts | Low | Medium | Test both Bash and PowerShell after changes |
| Missing template sync | Medium | Low | Create explicit sync step in implementation |
| CLI init fails | Low | High | Test init command with both agents |

## Conclusion

The cleanup is well-scoped with changes concentrated in two files (update-agent-context.sh and .ps1). The architecture with scripts/ as source of truth simplifies the work - clean the source files once, then sync to templates. The missing templates/scripts/powershell/ directory must be created as part of this work.
