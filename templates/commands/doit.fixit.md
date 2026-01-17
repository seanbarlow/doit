---
description: Start and manage bug-fix workflows for GitHub issues
handoffs:
  - label: Create Plan
    agent: doit.planit
    prompt: Create fix plan from investigation findings
    send: true
  - label: Implement Fix
    agent: doit.implementit
    prompt: Execute the fix plan tasks
    send: true
  - label: Check In
    agent: doit.checkin
    prompt: Finalize fix and create pull request
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Load Project Context

Before proceeding, load the project context to inform your responses:

```bash
doit context show
```

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:

- Reference constitution principles when making decisions
- Consider roadmap priorities
- Identify connections to related specifications

## Outline

This command manages the bug-fix workflow lifecycle for GitHub issues.

### 1. Parse Command Arguments

Extract the operation from `$ARGUMENTS`:

| Pattern | Operation | Example |
|---------|-----------|---------|
| `start <issue_id>` | Start workflow for issue | `/doit.fixit start 123` |
| `start` | Interactive issue selection | `/doit.fixit start` |
| `list` | List open bugs | `/doit.fixit list` |
| `status [issue_id]` | Show workflow status | `/doit.fixit status` |
| `investigate [issue_id]` | Start/manage investigation | `/doit.fixit investigate` |
| `plan [issue_id]` | Generate fix plan | `/doit.fixit plan` |
| `review [issue_id]` | Review and approve plan | `/doit.fixit review` |
| `cancel [issue_id]` | Cancel workflow | `/doit.fixit cancel` |
| `workflows` | List all workflows | `/doit.fixit workflows` |

### 2. Workflow Phases

The fixit workflow progresses through these phases:

```
initialized → investigating → planning → reviewing → approved → implementing → completed
                    ↓              ↓          ↓
                cancelled      cancelled   cancelled
```

### 3. Start Workflow

When starting a new workflow (`doit fixit start <issue_id>`):

1. Verify the GitHub issue exists and is open
2. Check no existing workflow for this issue
3. Create fix branch: `fix/{issue_id}-{slug}`
4. Initialize workflow state in `.doit/state/fixit-{issue_id}.json`
5. Display next steps for investigation

### 4. Investigation Phase

Run `doit fixit investigate` to:

1. Extract keywords from issue title/body
2. Create checkpoints for investigation:
   - Review error logs and stack traces
   - Identify affected code paths
   - Search for related issues or commits
   - Formulate root cause hypothesis
3. Add findings with types:
   - `hypothesis` - Initial theories
   - `confirmed_cause` - Verified root cause
   - `affected_file` - Files that need changes
   - `reproduction_step` - Steps to reproduce

Example:
```bash
doit fixit investigate -a "Null pointer in click handler" -t confirmed_cause
doit fixit investigate -c cp-1  # Complete checkpoint
doit fixit investigate --done    # Finish investigation
```

### 5. Planning Phase

Run `doit fixit plan --generate` to:

1. Extract confirmed root cause from investigation
2. Identify affected files from findings
3. Generate fix plan with:
   - Root cause summary
   - Proposed solution
   - Files to modify
   - Risk assessment (low/medium/high)
4. Save plan to workflow state

### 6. Review and Approval

Run `doit fixit review` to:

1. Display the fix plan for review
2. Use `--approve` to approve the plan
3. On approval, advance to implementing phase

### 7. Implementation

After plan approval:

1. Run `/doit.implementit` to execute the fix
2. The fix plan guides the implementation
3. Workflow tracks implementation progress

### 8. Completion

Run `/doit.checkin` to:

1. Create pull request
2. Link PR to GitHub issue
3. Mark workflow as completed
4. Optionally close the GitHub issue

---

## Key Rules

- Always verify GitHub issue exists before starting
- Require confirmed_cause finding before planning
- Require plan approval before implementation
- Branch naming: `fix/{issue_id}-{slug}`
- State persistence: `.doit/state/fixit-{issue_id}.json`

---

## Next Steps

After completing this command, display recommendations:

### On Workflow Started

```markdown
**Workflow started for issue #123!**

**Recommended**: Run `/doit.fixit investigate` to start the investigation phase.
```

### On Investigation Complete

```markdown
**Investigation complete!**

**Recommended**: Run `/doit.fixit plan --generate` to create a fix plan.
```

### On Plan Approved

```markdown
**Plan approved!**

**Recommended**: Run `/doit.implementit` to implement the fix.
```
