# Research: Documentation and Tutorial Refresh

**Feature**: 028-docs-tutorial-refresh
**Date**: 2026-01-15

## Documentation Audit Results

### Files Reviewed

| File | Last Updated | Status |
|------|--------------|--------|
| README.md | Recent | Needs updates |
| docs/quickstart.md | Recent | Needs updates |
| docs/installation.md | Recent | Needs updates |
| docs/index.md | 2026-01-10 | Stale - missing features |
| docs/tutorials/02-existing-project-tutorial.md | Recent | Needs updates |

### Gap Analysis

#### 1. Missing CLI Commands in Documentation

The following CLI commands are implemented but **NOT documented** in quickstart or README:

| Command | Implementation | Documentation Status |
|---------|---------------|---------------------|
| `doit sync-prompts` | [src/doit_cli/cli/sync_prompts_command.py](src/doit_cli/cli/sync_prompts_command.py) | Missing |
| `doit context show` | [src/doit_cli/cli/context_command.py](src/doit_cli/cli/context_command.py) | Missing |
| `doit hooks install` | [src/doit_cli/cli/hooks_command.py](src/doit_cli/cli/hooks_command.py) | Missing |
| `doit hooks validate` | [src/doit_cli/cli/hooks_command.py](src/doit_cli/cli/hooks_command.py) | Missing |
| `doit verify` | [src/doit_cli/cli/verify_command.py](src/doit_cli/cli/verify_command.py) | Missing |

#### 2. Feature Index Gap (docs/index.md)

The AUTO-GENERATED section only shows 8 features:
- 003, 004, 005, 006, 008, 009, 012, update-doit-templates

**Missing from index** (19 feature docs exist but 11 not linked):
- 015-docs-branding-cleanup
- 016-scripts-cleanup
- 017-roadmap-template-cleanup
- 018-develop-branch-setup
- 020-constitution-improvements
- 021-copilot-agent-fix
- 022-docs-logo-integration
- 024-unified-templates
- 025-git-hooks-workflow
- 026-ai-context-injection
- 027-template-context-injection

#### 3. README.md Issues

**Current state**: Says "The 11 Commands" but doesn't distinguish CLI vs Slash commands

**Issues found**:
- Command count is misleading (11 slash commands + 5 CLI commands = 16 total)
- No mention of CLI commands at all
- Version in Status section may be stale (shows 0.0.23)

#### 4. quickstart.md Issues

**Command Reference Table** (lines 194-207):
- Only lists slash commands
- Missing CLI commands entirely
- No "Type" column to distinguish CLI vs Slash

**Missing sections**:
- No context injection explanation
- No mention of `doit context show`
- No mention of git hooks workflow

#### 5. Tutorial 02 Issues

**Current state**: Comprehensive brownfield tutorial but outdated

**Missing mentions**:
- Context injection (added in 026/027)
- sync-prompts for multi-agent setups
- Git hooks for team enforcement

### Recent Features Not Reflected in Docs

| Feature | PR | Completed | Documentation Impact |
|---------|-----|-----------|---------------------|
| 023-copilot-prompts-sync | - | 2026-01-15 | sync-prompts command not documented |
| 024-unified-templates | - | 2026-01-15 | Template system changes not reflected |
| 025-git-hooks-workflow | - | 2026-01-15 | Hooks workflow not documented |
| 026-ai-context-injection | #253 | 2026-01-15 | context command not documented |
| 027-template-context-injection | #266 | 2026-01-15 | Auto-loading not explained |

### Grep Search Results

Search for new feature mentions in docs:
```
sync-prompts|context show|hooks|git hook → 5 files found
```

Only feature docs mention these - not user guides.

## Recommendations

### Priority 1: Command Reference Updates
1. Update quickstart.md command table with CLI commands
2. Update README.md to show CLI + Slash command separation
3. Update installation.md verification section

### Priority 2: Feature Index Regeneration
1. Run `/doit.documentit` to regenerate index
2. Verify all 19 feature docs appear in index

### Priority 3: New Documentation Sections
1. Add "Context Injection" section to quickstart.md
2. Add "Git Hooks Workflow" section or separate guide
3. Add "Multi-Agent Setup" section mentioning sync-prompts

### Priority 4: Tutorial Updates
1. Tutorial 02: Add context injection mentions
2. Tutorial 02: Add sync-prompts mention for Copilot+Claude users

## Version Check

```bash
# Current pyproject.toml version
grep version pyproject.toml
# Result: version = "0.1.4"

# README.md shows: 0.0.23 (STALE)
```

**Action needed**: Update README.md version to 0.1.4

## Links to Feature Documentation

For context during implementation:

- [026-ai-context-injection.md](../../docs/features/026-ai-context-injection.md) - Context CLI implementation
- [027-template-context-injection.md](../../docs/features/027-template-context-injection.md) - Template context loading
- [025-git-hooks-workflow.md](../../docs/features/025-git-hooks-workflow.md) - Git hooks implementation
- [024-unified-templates.md](../../docs/features/024-unified-templates.md) - Template unification

---

*Research completed by Claude Code on 2026-01-15*
