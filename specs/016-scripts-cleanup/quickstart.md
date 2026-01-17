# Quickstart: Scripts Cleanup and Agent Support Standardization

## Overview

This guide provides quick reference for implementing and testing the scripts cleanup feature.

## Implementation Checklist

### Phase 1: Cleanup Source Scripts

1. Edit `scripts/bash/update-agent-context.sh`:
   - [ ] Update header comments (lines 31-39)
   - [ ] Remove unsupported agent file path variables (lines 62-77)
   - [ ] Clean `update_specific_agent()` function (lines 581-642)
   - [ ] Clean `update_all_existing_agents()` function (lines 644-728)
   - [ ] Update `print_summary()` function (lines 729-748)

2. Edit `scripts/powershell/update-agent-context.ps1`:
   - [ ] Update header/synopsis (lines 1-25)
   - [ ] Update ValidateSet parameter (lines 26-30)
   - [ ] Remove unsupported agent file path variables (lines 47-62)
   - [ ] Clean `Update-SpecificAgent` function (lines 368-393)
   - [ ] Clean `Update-AllExistingAgents` function (lines 395-418)
   - [ ] Update `Print-Summary` function (lines 420-428)

### Phase 2: Sync Templates

```bash
# Create missing PowerShell templates directory
mkdir -p templates/scripts/powershell

# Sync all scripts to templates
cp -r scripts/bash/* templates/scripts/bash/
cp -r scripts/powershell/* templates/scripts/powershell/
```

### Phase 3: Verify

```bash
# Verify no unsupported agents remain
grep -ri "gemini" scripts/ templates/scripts/
grep -ri "codebuddy" scripts/ templates/scripts/
grep -ri "cursor-agent\|qwen\|opencode\|codex\|windsurf" scripts/ templates/scripts/
grep -ri "kilocode\|auggie\|roo\|amp\|shai" scripts/ templates/scripts/
grep -ri "\bq\b\|bob\|qoder" scripts/ templates/scripts/

# All grep commands should return no results
```

## Testing Commands

### Script Help Output

```bash
# Bash - should only show claude and copilot
./scripts/bash/update-agent-context.sh --help

# PowerShell - should only show Claude and Copilot
pwsh ./scripts/powershell/update-agent-context.ps1 -Help
```

### Template Synchronization

```bash
# Should show no differences
diff -r scripts/bash templates/scripts/bash
diff -r scripts/powershell templates/scripts/powershell
```

### CLI Commands

```bash
# Create a test directory
mkdir -p /tmp/doit-test && cd /tmp/doit-test

# Test init with Claude
doit init . --agent claude
# Verify .doit/scripts/ was created

# Clean up
rm -rf /tmp/doit-test

# Test init with Copilot
mkdir -p /tmp/doit-test && cd /tmp/doit-test
doit init . --agent copilot
# Verify configuration

# Clean up
rm -rf /tmp/doit-test
```

## Success Criteria Verification

| Criterion | Command | Expected Result |
| --------- | ------- | --------------- |
| SC-001: No "gemini" | `grep -ri "gemini" scripts/ templates/scripts/` | No output |
| SC-002: No "codebuddy" | `grep -ri "codebuddy" scripts/ templates/scripts/` | No output |
| SC-003: No other unsupported | See verify commands above | No output |
| SC-004: PowerShell parity | `ls scripts/powershell/*.ps1` | 5 files |
| SC-005: Bash templates sync | `diff -r scripts/bash templates/scripts/bash` | No output |
| SC-006: PS templates sync | `diff -r scripts/powershell templates/scripts/powershell` | No output |
| SC-007: Init with Claude | `doit init test --agent claude` | Success |
| SC-008: Init with Copilot | `doit init test --agent copilot` | Success |
| SC-009: Help shows only supported | Check --help output | Only claude, copilot |

## Agents to Keep

- `claude` - Claude Code (CLAUDE.md)
- `copilot` - GitHub Copilot (.github/agents/copilot-instructions.md)

## Agents to Remove

gemini, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, roo, codebuddy, qoder, amp, shai, q, bob
