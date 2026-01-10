---
description: Finalize feature implementation, close issues, update roadmaps, and create pull request
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. **Load checkin context**:
   - **REQUIRED**: Read spec.md for feature name and requirements
   - **REQUIRED**: Read tasks.md for completion status
   - **IF EXISTS**: Read review-report.md for code review status
   - **IF EXISTS**: Read test-report.md for test status

3. **Retrieve GitHub issues for feature** (FR-037):
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

5. **Handle incomplete issues** (FR-038):
   - If any issues are still open but tasks show complete:
     - List the incomplete issues
     - Ask: "The following issues are still open. Do you want to close them? (yes/no/select)"
     - If "select": Present each issue for individual decision
   - If tasks show incomplete work:
     - Warn: "Some tasks are not marked complete in tasks.md"
     - Ask: "Do you want to proceed anyway? (yes/no)"
   - Close approved issues via GitHub API

6. **Update roadmap files** (FR-039, FR-040):
   - Check if `.specify/memory/roadmap.md` exists:
     - If exists: Find feature entry, update status to "Completed"
     - If not exists: Log "No roadmap.md found, skipping"
   - Check if `.specify/memory/roadmap_completed.md` exists:
     - If exists: Append feature entry with completion date
     - If not exists: Create file with header and first entry

   ```markdown
   # Completed Features

   | Feature | Branch | Completed | PR |
   |---------|--------|-----------|-----|
   | [Feature Name] | [branch] | [date] | #XXX |
   ```

7. **Generate feature documentation** in docs/ (FR-041):
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

8. **Prepare git commit** (FR-042):
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

9. **Create pull request** (FR-043):
   - Determine target branch:
     - Check $ARGUMENTS for `--target [branch]` flag (FR-044)
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
