---
description: Start and manage bug-fix workflows for GitHub issues
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
effort: high
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

## Code Quality Guidelines

Before generating or modifying code:

1. **Search for existing implementations** - Use Glob/Grep to find similar functionality before creating new code
2. **Follow established patterns** - Match existing code style, naming conventions, and architecture
3. **Avoid duplication** - Reference or extend existing utilities rather than recreating them
4. **Check imports** - Verify required dependencies already exist in the project

**Context already loaded** (DO NOT read these files again):

- Constitution principles and tech stack
- Roadmap priorities
- Current specification
- Related specifications

## Artifact Storage

- **Temporary scripts**: Save to `.doit/temp/{purpose}-{timestamp}.sh` (or .py/.ps1)
- **Status reports**: Save to `specs/{feature}/reports/{command}-report-{timestamp}.md`
- **Create directories if needed**: Use `mkdir -p` before writing files
- Note: `.doit/temp/` is gitignored - temporary files will not be committed

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

## Investigation Checkpoint Examples

Different bug types require different investigation approaches. Use these as templates:

### UI/Frontend Bug

```text
Checkpoints:
  cp-1: Reproduce in browser (note steps, screenshots)
  cp-2: Check browser console for errors/warnings
  cp-3: Inspect network requests for failed API calls
  cp-4: Trace component render cycle and state
  cp-5: Identify root cause in component tree

Findings:
  - type: reproduction_step
    detail: "Click submit with empty form -> TypeError in console"
  - type: affected_file
    detail: "src/components/Form.tsx:42 - missing null check on props.onSubmit"
  - type: confirmed_cause
    detail: "Optional callback prop accessed without guard"
```

### API/Backend Bug

```text
Checkpoints:
  cp-1: Review error logs and stack traces
  cp-2: Reproduce with curl/httpie (exact request)
  cp-3: Check input validation and edge cases
  cp-4: Trace code path from endpoint to error
  cp-5: Review database queries and data state

Findings:
  - type: reproduction_step
    detail: "POST /api/items with duplicate name -> 500 Internal Server Error"
  - type: affected_file
    detail: "src/services/item_service.py:88 - unhandled IntegrityError"
  - type: confirmed_cause
    detail: "Missing unique constraint error handling in create_item()"
```

### Data/Migration Bug

```text
Checkpoints:
  cp-1: Identify affected records/data
  cp-2: Check migration history and schema state
  cp-3: Compare expected vs actual data
  cp-4: Trace data transformation pipeline
  cp-5: Verify rollback safety

Findings:
  - type: hypothesis
    detail: "Migration 003 may have dropped column before data was moved"
  - type: confirmed_cause
    detail: "Migration ordering: column dropped in 003, data migration in 004"
```

### Performance Bug

```text
Checkpoints:
  cp-1: Establish baseline metrics (response time, memory, CPU)
  cp-2: Profile the slow operation
  cp-3: Identify bottleneck (N+1 query, large payload, blocking I/O)
  cp-4: Check for missing indexes or cache misses
  cp-5: Design optimization approach

Findings:
  - type: reproduction_step
    detail: "GET /api/reports with 10k+ records -> 12s response time"
  - type: confirmed_cause
    detail: "N+1 query: loading related items individually in loop"
```

---

## Error Recovery

### Workflow State Corruption

The workflow state file is unreadable or contains invalid data.

**FATAL** | Your investigation progress may be lost if the state file is unrecoverable. If `.doit/state/fixit-{issue_id}.json` becomes corrupted:

1. Run `doit fixit status {issue_id}` to see current state
2. If unreadable, delete the state file and restart: `doit fixit start {issue_id}`
3. Re-add key investigation findings manually
4. Verify: `doit fixit status {issue_id}` shows valid workflow state

> Prevention: Avoid manually editing state files in `.doit/state/`

If the above steps don't resolve the issue: recreate the workflow from scratch and document previous findings in the GitHub issue comments.

### GitHub Issue Not Found

The referenced GitHub issue does not exist or is inaccessible.

**ERROR** | If the issue was closed, deleted, or transferred:

1. Check issue status: `gh issue view {issue_id}`
2. If transferred, update the workflow with the new issue number
3. If closed by mistake, reopen: `gh issue reopen {issue_id}`
4. Verify: `gh issue view {issue_id}` shows the issue details

> Prevention: Confirm the issue number before starting a workflow

If the above steps don't resolve the issue: create a new issue describing the bug and start a fresh workflow.

### Branch Conflicts

The fix branch has merge conflicts with the base branch.

**ERROR** | If the fix branch has merge conflicts with the base branch:

1. Fetch latest: `git fetch origin`
2. Rebase onto target: `git rebase origin/main` (or develop)
3. Resolve conflicts, then continue the workflow
4. Do NOT force-push without confirming with the team
5. Verify: `git status` shows no merge conflicts remaining

> Prevention: Rebase frequently against the base branch during long-running fixes

If the above steps don't resolve the issue: consider creating a new branch from the latest base and cherry-picking your fix commits.

### Investigation Dead End

The investigation did not identify a root cause for the bug.

**WARNING** | If investigation doesn't reveal a root cause:

1. Add a `hypothesis` finding documenting what was ruled out
2. Run `doit fixit investigate --done` to close the investigation
3. Add a comment to the GitHub issue requesting more information
4. Consider running `doit fixit cancel {issue_id}` if the bug is not reproducible
5. Verify: the GitHub issue has a comment summarizing investigation findings

> Prevention: Set a time limit for investigation and request more context early if needed

If the above steps don't resolve the issue: escalate by tagging relevant team members on the GitHub issue for additional input.

### Plan Rejected After Review

The fix plan was not approved and needs changes.

**WARNING** | If the fix plan needs revision:

1. The workflow stays in `reviewing` phase
2. Run `doit fixit plan --generate` again with updated investigation findings
3. Review the new plan with `doit fixit review`
4. Verify: `doit fixit status {issue_id}` shows the workflow advanced past `reviewing`

> Prevention: Include thorough investigation findings before generating the plan

If the above steps don't resolve the issue: add more investigation findings to strengthen the root cause analysis before regenerating the plan.

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
