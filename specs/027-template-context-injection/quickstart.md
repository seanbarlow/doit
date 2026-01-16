# Quickstart: Template Context Injection

**Feature**: 027-template-context-injection
**Time to complete**: ~30 minutes

## Prerequisites

- Feature branch `027-template-context-injection` checked out
- Understanding of doit command template structure
- Access to `templates/commands/` directory

## Implementation Steps

### Step 1: Understand the Context Loading Section

The context loading section to add to each template:

```markdown
## Load Project Context

Before proceeding, load the project context to inform your responses:

\`\`\`bash
doit context show
\`\`\`

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:
- Reference constitution principles when making decisions
- Consider roadmap priorities
- Identify connections to related specifications
```

### Step 2: Modify Each Template

For each template in `templates/commands/`:

1. Open the template file
2. Locate the `## User Input` section
3. Add the context loading section AFTER `## User Input` and BEFORE `## Outline`
4. Add template-specific context usage guidance

**Template modification order** (recommended):

1. `doit.specit.md` - Add reference to constitution principles
2. `doit.planit.md` - Add tech stack consideration
3. `doit.taskit.md` - Add related spec awareness
4. `doit.implementit.md` - Add coding standards reference
5. `doit.reviewit.md` - Add principle validation
6. `doit.checkin.md` - Add roadmap verification
7. `doit.constitution.md` - Add existing context awareness
8. `doit.roadmapit.md` - Add current roadmap loading
9. `doit.scaffoldit.md` - Add tech stack scaffolding
10. `doit.documentit.md` - Add project context reference
11. `doit.testit.md` - Add test requirements reference

### Step 3: Run Sync Command

After modifying all templates:

```bash
doit sync-prompts
```

This propagates changes to:
- `.claude/commands/` (Claude Code)
- `.github/prompts/` (GitHub Copilot)

### Step 4: Verify Changes

Test each command by running it and verifying:
- [ ] Context loading step appears in command output
- [ ] AI references constitution principles (when applicable)
- [ ] Command completes successfully even without context files

## Example: Modified doit.specit.md

```markdown
---
description: Create or update the feature specification...
---

## User Input

\`\`\`text
$ARGUMENTS
\`\`\`

## Load Project Context

Before proceeding, load the project context to inform your responses:

\`\`\`bash
doit context show
\`\`\`

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:
- Reference constitution principles when generating specifications
- Align new features with roadmap priorities
- Identify potential overlap with existing specifications

## Outline

[Rest of template...]
```

## Verification Checklist

- [ ] All 11 templates modified
- [ ] Context loading section positioned correctly
- [ ] Template-specific guidance added
- [ ] `doit sync-prompts` executed
- [ ] Manual test of at least one command

## Troubleshooting

**Context loading fails silently**:
- Verify `doit context show` works from command line
- Check `.doit/config/context.yaml` exists and is valid

**Templates not syncing**:
- Ensure `doit sync-prompts` completes without errors
- Check file permissions on target directories

**AI not using loaded context**:
- Verify context loading section is before main logic
- Check that usage guidance is specific and actionable

## Future Enhancement: Selective Context Loading (US4)

For future implementation, selective context loading can be configured per-command in `.doit/config/context.yaml`. This optimization reduces context size for simpler commands.

**Configuration Example**:

```yaml
# .doit/config/context.yaml
defaults:
  sources:
    - constitution
    - roadmap
    - specs

per_command:
  doit.documentit:
    sources:
      - constitution  # Only needs project principles
  doit.constitution:
    sources: []       # Creates context, doesn't need to load it
```

**Implementation Notes**:

- Default behavior loads all context sources (constitution, roadmap, specs)
- Per-command overrides allow selective loading for efficiency
- Commands like `documentit` may only need constitution principles
- Commands like `constitution` create context and may skip loading
- This is a P3 enhancement - the current full-context approach works for all cases
