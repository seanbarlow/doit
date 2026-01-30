---
description: Finalize feature implementation, close issues, update roadmaps, and create pull request
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
- Consider roadmap priorities (roadmap content is already loaded)
- Identify connections to related specifications
- Determine if roadmap files exist (absence means empty context section)

**DO NOT read these files again for context** (already loaded above):

- `.doit/memory/constitution.md` - principles are in context
- `.doit/memory/roadmap.md` - content is in context (read for MODIFICATION only in step 6)
- `.doit/memory/completed_roadmap.md` - content is in context

**Legitimate explicit reads** (for modification, NOT in context show):

- `specs/{feature}/spec.md` - feature details for documentation
- `specs/{feature}/tasks.md` - completion status
- `specs/{feature}/review-report.md` - code review status
- `specs/{feature}/test-report.md` - test status

## Code Quality Guidelines

Before generating or modifying code:

1. **Search for existing implementations** - Use Glob/Grep to find similar functionality before creating new code
2. **Follow established patterns** - Match existing code style, naming conventions, and architecture
3. **Avoid duplication** - Reference or extend existing utilities rather than recreating them
4. **Check imports** - Verify required dependencies already exist in the project

## Artifact Storage

- **Temporary scripts**: Save to `.doit/temp/{purpose}-{timestamp}.sh` (or .py/.ps1)
- **Status reports**: Save to `specs/{feature}/reports/{command}-report-{timestamp}.md`
- **Create directories if needed**: Use `mkdir -p` before writing files
- Note: `.doit/temp/` is gitignored - temporary files will not be committed

## Outline

1. **Setup**: Run `.doit/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. **Load checkin context**:
   - **REQUIRED**: Read spec.md for feature name and requirements
   - **REQUIRED**: Read tasks.md for completion status
   - **IF EXISTS**: Read review-report.md for code review status
   - **IF EXISTS**: Read test-report.md for test status

3. **Retrieve GitHub issues for feature**:
   - Detect GitHub remote: `git remote get-url origin`
   - If GitHub remote found:
     - Search for Epic issue matching feature branch name
     - Search for Feature issues linked to the Epic
     - Search for Task issues linked to Features
     - Build issue hierarchy tree
   - If no GitHub remote: Skip issue management, proceed to step 6

4. **Review issue completion status**:
   - For each issue in hierarchy:
     - Check if issue is open or closed
     - Compare against tasks.md completion
   - Generate status summary:

     ```text
     ## Issue Status

     ### Epic: #XXX - [Epic Name]
     Status: OPEN

     ### Features
     | Issue | Title | Status | Tasks Done |
     |-------|-------|--------|------------|
     | #YYY | Feature A | OPEN | 5/5 |
     | #ZZZ | Feature B | OPEN | 3/4 |

     ### Tasks
     | Issue | Title | Status |
     |-------|-------|--------|
     | #AAA | Task 1 | CLOSED |
     | #BBB | Task 2 | OPEN |
     ```

5. **Handle incomplete issues**:
   - If any issues are still open but tasks show complete:
     - List the incomplete issues
     - Ask: "The following issues are still open. Do you want to close them? (yes/no/select)"
     - If "select": Present each issue for individual decision
   - If tasks show incomplete work:
     - Warn: "Some tasks are not marked complete in tasks.md"
     - Ask: "Do you want to proceed anyway? (yes/no)"
   - Close approved issues via GitHub API

6. **Update roadmap files** (FR-039, FR-040):

   #### 6.1 Get Current Feature Branch

   ```bash
   git branch --show-current
   ```

   Extract the feature pattern (e.g., `008-doit-roadmapit-command` from branch name).

   #### 6.2 Check and Update roadmap.md

   - Roadmap availability is known from context show (if section was empty, file doesn't exist)
     - If no roadmap in context: Log "No roadmap.md found, skipping roadmap archive"
     - If roadmap exists (was in context):
       1. Read the roadmap file **for modification** (context has summary, need full file to edit)
       2. Search for items with matching feature branch reference `[###-feature-name]`
          - Pattern: Items containing backtick references like `` `008-feature-name` `` or `[008-feature-name]`
       3. For each matching item found:
          - Extract: item text, priority (P1-P4), rationale
          - Remove the item from its current priority section
          - Mark as completed with `[x]` if using checkbox format

   #### 6.3 Archive to completed_roadmap.md

   - completed_roadmap availability is known from context show
   - Read file **for modification** if it exists:
     - If NOT exists:
       1. Copy template from `.doit/templates/completed-roadmap-template.md`
       2. Replace `[PROJECT_NAME]` with project name
       3. Replace `[DATE]` with current date
       4. If template not found, create with basic structure:
          ```markdown
          # Completed Roadmap Items

          **Project**: [Project Name]
          **Created**: [Date]

          ## Recently Completed

          | Item | Original Priority | Completed Date | Feature Branch | Notes |
          |------|-------------------|----------------|----------------|-------|
          ```
     - If exists: Load existing file

   - For each matched roadmap item:
     1. Add to "Recently Completed" table with:
        - Item text (without the branch reference)
        - Original priority (P1-P4)
        - Completion date (today's date)
        - Feature branch reference (`` `###-feature-name` ``)
        - Notes (from spec.md summary if available)

   - **Maintain 20-item limit** in Recently Completed:
     1. Count items in "Recently Completed" section
     2. If count > 20:
        - Move oldest items (beyond 20) to Archive section
        - Update Statistics section with new counts (P1, P2, P3, P4 totals)

   #### 6.4 Write Updated Files

   - Write updated roadmap.md (with completed items removed)
   - Write updated completed_roadmap.md (with new completed items)

   #### 6.5 Report Roadmap Changes

   ```markdown
   ## Roadmap Archive Summary

   **Items Archived**: [N]
   | Item | Original Priority |
   |------|-------------------|
   | [item text] | P[N] |

   **Files Updated**:
   - `.doit/memory/roadmap.md` - Removed [N] completed items
   - `.doit/memory/completed_roadmap.md` - Added [N] items to archive
   ```

   If no matching items found: Log "No matching roadmap items found for branch [branch-name]"

7. **Generate feature documentation** in docs/:
   - Create `docs/features/[feature-name].md`:

     ```markdown
     # [Feature Name]

     **Completed**: [date]
     **Branch**: [branch name]
     **PR**: #XXX

     ## Overview
     [Summary from spec.md]

     ## Requirements Implemented
     | ID | Description | Status |
     |----|-------------|--------|
     | FR-001 | ... | Done |

     ## Technical Details
     [Key decisions from plan.md]

     ## Files Changed
     [List from tasks.md]

     ## Testing
     - Automated tests: [summary from test-report.md]
     - Manual tests: [summary from review-report.md]

     ## Related Issues
     - Epic: #XXX
     - Features: #YYY, #ZZZ
     - Tasks: #AAA, #BBB, ...
     ```

8. **Prepare git commit**:
   - Stage all changes: `git add -A`
   - Generate commit message from feature context:

     ```text
     feat([feature-name]): [brief description]

     Implements [Epic/Feature name] with the following:
     - [Key change 1]
     - [Key change 2]
     - [Key change 3]

     Closes #XXX, #YYY, #ZZZ

     Requirements: FR-001, FR-002, ...
     Tests: X passed, Y manual verified
     ```

   - Execute commit: `git commit -m "[message]"`

9. **Create pull request**:
   - Determine target branch:
     - Check $ARGUMENTS for `--target [branch]` flag
     - If not specified, check for `develop` branch
     - If no `develop`, use `main` or `master`
   - Check for gh CLI:
     - Run `which gh` to verify installation
     - If not found: Output manual PR instructions and skip (FR-044 fallback)
   - If gh CLI available:
     - Push branch: `git push -u origin [branch]`
     - Create PR:

       ```bash
       gh pr create \
         --title "feat([feature]): [description]" \
         --body "[PR body from template]" \
         --base [target-branch]
       ```

   - PR body template:

     ```markdown
     ## Summary
     [Brief description from spec.md]

     ## Changes
     - [List of key changes]

     ## Testing
     - [ ] Automated tests pass
     - [ ] Manual testing complete
     - [ ] Code review approved

     ## Requirements
     | ID | Description | Status |
     |----|-------------|--------|
     | FR-XXX | ... | Done |

     ## Related Issues
     Closes #XXX, #YYY, #ZZZ

     ---
     Generated by `/doit.checkin`
     ```

10. **Handle missing gh CLI** (FR-044 fallback):
    - If gh CLI not installed:

      ```text
      ## Manual PR Creation Required

      The gh CLI is not installed. Please create a PR manually:

      1. Push your branch:
         git push -u origin [branch-name]

      2. Create PR at:
         https://github.com/[owner]/[repo]/compare/[target]...[branch]

      3. Use this PR template:
         [output template content]

      4. Link these issues:
         - Closes #XXX, #YYY, #ZZZ
      ```

11. **Handle missing develop branch** (fallback):
    - If target branch doesn't exist:
      - Check for `main`, then `master`
      - If none found, ask user for target branch name

12. **Report**: Output summary:
    - Issues closed (count)
    - Roadmap updated (yes/no)
    - Documentation generated (path)
    - Commit created (hash)
    - PR created (URL) or manual instructions
    - Next steps (merge PR, delete branch after merge)

## Key Rules

- Use absolute paths for all file operations
- Never force-push or modify git history
- Always confirm before closing issues
- Generate documentation even if GitHub unavailable
- Provide manual fallbacks for all GitHub operations
- Include issue references in commit message for auto-linking

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (PR merged or ready to merge)

Display the following at the end of your output:

```markdown
---

## Next Steps

┌───────────────────────────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                                                    │
│  ● specit → ● planit → ● taskit → ● implementit → ● testit → ● reviewit → ● checkin  │
└───────────────────────────────────────────────────────────────────────────────────────┘

**Status**: Feature complete! 🎉

**Recommended**: Run `/doit.roadmapit` to update the project roadmap with this completion.

**Alternative**: Run `/doit.specit [next feature]` to start the next feature development.
```

### On Partial Success (PR created, pending merge)

If the PR was created but not yet merged:

```markdown
---

## Next Steps

┌───────────────────────────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                                                    │
│  ● specit → ● planit → ● taskit → ● implementit → ● testit → ● reviewit → ◐ checkin  │
└───────────────────────────────────────────────────────────────────────────────────────┘

**Status**: PR created and awaiting merge.

**Next**: Merge the PR when ready, then run `/doit.roadmapit` to update the project roadmap.
```

### On Error (issues incomplete)

If some issues or tasks are still incomplete:

```markdown
---

## Next Steps

**Issue**: Some tasks or issues are still open.

**Recommended**: Complete the outstanding tasks with `/doit.implementit`, or use `--force` flag to proceed anyway.
```
