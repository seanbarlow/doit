# Quickstart: Documentation and Tutorial Refresh

**Feature**: 028-docs-tutorial-refresh
**Date**: 2026-01-15

## Overview

This feature updates all Do-It documentation to reflect recent enhancements (features 023-027). It's a **documentation-only** feature with no code changes.

## Prerequisites

- Access to the doit repository
- Git checkout of branch `028-docs-tutorial-refresh`
- Text editor for markdown files

## Implementation Order

Follow this order for efficient implementation:

### Phase 1: Command Reference Updates (P1)

1. **Update quickstart.md command table**
   ```markdown
   | `doit sync-prompts` | Sync templates to AI agents | CLI |
   | `doit context show` | Display project context | CLI |
   | `doit hooks install` | Install workflow hooks | CLI |
   | `doit verify` | Verify project structure | CLI |
   ```

2. **Update README.md**
   - Find "The 11 Commands" section
   - Update to reflect actual command count
   - Add CLI Commands subsection

3. **Update installation.md**
   - Add CLI command verification after slash command verification

### Phase 2: Feature Index (P1)

```bash
# Regenerate the feature index
/doit.documentit
```

Verify docs/index.md shows all 19+ features.

### Phase 3: Context Injection Docs (P1)

Add new section to docs/quickstart.md after "Quick Command Reference":

```markdown
## Project Context

Do-It automatically loads project context before executing commands...

### View Context
\`\`\`bash
doit context show
\`\`\`

### Configure Context
Edit `.doit/context.yaml` to customize...
```

### Phase 4: Git Hooks Docs (P2)

Add new section to docs/quickstart.md:

```markdown
## Workflow Enforcement (Optional)

Enable spec-first enforcement with git hooks...

### Install Hooks
\`\`\`bash
doit hooks install
\`\`\`

### Bypass (Emergency)
\`\`\`bash
git commit --no-verify -m "emergency fix"
\`\`\`
```

### Phase 5: Tutorial Updates (P2)

Edit docs/tutorials/02-existing-project-tutorial.md:
- Add context awareness note in Section 3
- Mention sync-prompts for multi-agent setups

### Phase 6: Version Updates (P3)

1. Update README.md version to 0.1.4
2. Add changelog entries for features 023-027

## Verification

After all updates:

1. Check all internal links work
2. Verify code examples are copy-paste runnable
3. Run `/doit.reviewit` to validate changes

## Files Changed

| File | Type of Change |
|------|---------------|
| README.md | Update commands section, version |
| docs/quickstart.md | Add sections, update table |
| docs/installation.md | Add CLI verification |
| docs/index.md | Regenerate via documentit |
| docs/tutorials/02-existing-project-tutorial.md | Add context mentions |
| CHANGELOG.md | Add feature entries |

## Success Criteria

- [ ] All 5 CLI commands documented in quickstart
- [ ] Feature index shows 19+ features
- [ ] Context injection has dedicated section
- [ ] Git hooks have setup guide
- [ ] README version matches pyproject.toml
