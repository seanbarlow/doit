---
description: Review implemented code for quality and completeness against specifications
handoffs:
  - label: Run Tests
    agent: doit.test
    prompt: Execute automated tests and generate test report
    send: true
  - label: Check In
    agent: doit.checkin
    prompt: Finalize feature and create pull request
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

1. **Setup**: Run `.doit/scripts/bash/check-prerequisites.sh --json --require-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. **Load review context**:
   - **REQUIRED**: Read spec.md for requirements and acceptance criteria
   - **REQUIRED**: Read plan.md for technical decisions and architecture
   - **REQUIRED**: Read tasks.md for implementation details and file paths
   - **IF EXISTS**: Read data-model.md for entity definitions
   - **IF EXISTS**: Read contracts/ for API specifications

3. **Detect implemented files** from tasks.md:
   - Parse completed tasks (marked with [X])
   - Extract file paths from task descriptions
   - Build list of files to review
   - Group files by category: models, services, endpoints, tests, config

4. **Execute code review** against requirements:
   - For each implemented file:
     - Read file contents
     - Compare against relevant spec requirements
     - Check adherence to plan.md architecture decisions
     - Verify data model compliance (if data-model.md exists)
     - Verify API contract compliance (if contracts/ exists)
   - Generate findings with severity levels:
     - **CRITICAL**: Requirement not implemented, security issue, data loss risk
     - **MAJOR**: Partial implementation, performance concern, missing validation
     - **MINOR**: Code style, documentation gap, minor deviation from plan
     - **INFO**: Suggestion, optimization opportunity, best practice note

5. **Format findings report**:

   ```text
   ## Code Review Findings

   ### Critical (X findings)
   | File | Issue | Requirement |
   |------|-------|-------------|
   | path/to/file.py | Description | FR-XXX |

   ### Major (X findings)
   ...

   ### Minor (X findings)
   ...

   ### Info (X findings)
   ...

   ### Summary
   - Total files reviewed: X
   - Critical issues: X
   - Major issues: X
   - Minor issues: X
   - Recommendations: [list]
   ```

6. **Extract manual test items** from spec.md:
   - Parse acceptance criteria/scenarios from spec
   - Extract testable items that require manual verification
   - Items typically marked as "Given/When/Then" or acceptance criteria
   - Create sequential test list with:
     - Test ID (MT-001, MT-002, etc.)
     - Description
     - Expected outcome
     - Prerequisites (if any)

7. **Present manual tests sequentially**:
   - For each manual test:

     ```text
     ## Manual Test MT-XXX

     **Description**: [test description]
     **Prerequisites**: [any setup needed]
     **Steps**:
     1. [step 1]
     2. [step 2]
     ...

     **Expected Result**: [what should happen]

     ---
     Please execute this test and respond with:
     - PASS: Test passed as expected
     - FAIL: Test failed (describe what happened)
     - SKIP: Cannot test right now (provide reason)
     - BLOCK: Blocked by issue (describe blocker)
     ```

   - Wait for user response before proceeding to next test
   - Track results in memory

8. **Track test progress**:
   - Maintain running tally:

     ```text
     Progress: X/Y tests completed
     - Passed: X
     - Failed: X
     - Skipped: X
     - Blocked: X
     ```

   - Display after each test completion

9. **Collect sign-off**:
   - After all manual tests complete, present summary:

     ```text
     ## Manual Testing Complete

     | Test ID | Description | Result |
     |---------|-------------|--------|
     | MT-001 | ... | PASS |
     | MT-002 | ... | FAIL |
     ...

     **Overall Status**: [PASS if no failures, FAIL otherwise]

     Do you approve these results and sign off on manual testing? (yes/no)
     ```

   - Record sign-off response and timestamp

10. **Generate review-report.md** in FEATURE_DIR:

    ```markdown
    # Review Report: [Feature Name]

    **Date**: [timestamp]
    **Reviewer**: [Claude]
    **Branch**: [current branch]

    ## Code Review Summary

    | Severity | Count |
    |----------|-------|
    | Critical | X |
    | Major | X |
    | Minor | X |
    | Info | X |

    ### Critical Findings
    [detailed list]

    ### Major Findings
    [detailed list]

    ## Manual Testing Summary

    | Metric | Count |
    |--------|-------|
    | Total Tests | X |
    | Passed | X |
    | Failed | X |
    | Skipped | X |
    | Blocked | X |

    ### Test Results
    [detailed table]

    ## Sign-Off

    - Manual Testing: [Approved/Not Approved] at [timestamp]
    - Notes: [any notes from sign-off]

    ## Recommendations

    1. [recommendation 1]
    2. [recommendation 2]
    ...

    ## Next Steps

    - Run `/doit.testit` for automated test execution
    - Address any CRITICAL or MAJOR findings before merge
    ```

11. **Generate Mermaid Visualizations** (FR-011, FR-012):

    After collecting all review data, generate visual quality dashboards:

    a. **Finding Distribution Pie Chart**:
       - Count findings by severity (Critical, Major, Minor, Info)
       - Generate pie chart showing distribution
       - Add to review-report.md in Quality Overview section

       ```mermaid
       pie title Finding Distribution
           "Critical" : 0
           "Major" : 2
           "Minor" : 5
           "Info" : 3
       ```

       Insert using auto-generated markers:

       ~~~markdown
       ## Quality Overview

       <!-- BEGIN:AUTO-GENERATED section="finding-distribution" -->
       ```mermaid
       pie title Finding Distribution
           "Critical" : [count]
           "Major" : [count]
           "Minor" : [count]
           "Info" : [count]
       ```
       <!-- END:AUTO-GENERATED -->
       ~~~

    b. **Test Results Visualization**:
       - Count test results by status (Passed, Failed, Skipped, Blocked)
       - Generate pie chart showing test outcomes
       - Add to review-report.md in Manual Testing Summary section

       ```mermaid
       pie title Test Results
           "Passed" : 8
           "Failed" : 1
           "Skipped" : 2
           "Blocked" : 0
       ```

       Insert using auto-generated markers:

       ~~~markdown
       ## Test Results Overview

       <!-- BEGIN:AUTO-GENERATED section="test-results" -->
       ```mermaid
       pie title Test Results
           "Passed" : [count]
           "Failed" : [count]
           "Skipped" : [count]
           "Blocked" : [count]
       ```
       <!-- END:AUTO-GENERATED -->
       ~~~

    c. **Conditional Generation**:
       - If no findings: Show "No Issues Found" message instead of empty pie chart
       - If no manual tests: Omit Test Results visualization entirely
       - If all tests pass: Use green-themed success message

    d. **Diagram Validation**:
       - Verify mermaid syntax is valid
       - Ensure all counts are non-negative integers
       - Check that pie chart values sum to total count

12. **Report**: Output path to review-report.md and summary of findings

## Key Rules

- Use absolute paths for all file operations
- STOP on any CRITICAL finding that blocks further review
- Present manual tests one at a time, wait for response
- Generate review-report.md even if some tests are skipped
- Include timestamps for audit trail

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (review approved, no critical issues)

Display the following at the end of your output:

```markdown
---

## Next Steps

┌───────────────────────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                                                │
│  ● specit → ● planit → ● taskit → ● implementit → ● testit → ● reviewit → ○ checkin │
└───────────────────────────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.checkin` to finalize and merge your changes.
```

### On Issues Found (changes requested)

If the review found issues that need to be addressed:

```markdown
---

## Next Steps

┌───────────────────────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                                                │
│  ● specit → ● planit → ● taskit → ● implementit → ● testit → ◐ reviewit → ○ checkin │
└───────────────────────────────────────────────────────────────────────────────────┘

**Status**: [N] critical, [M] major issues found.

**Recommended**: Run `/doit.implementit` to address the review feedback.

After fixing issues, run `/doit.reviewit` again to verify.
```

### On Error (missing prerequisites)

If required files are missing:

```markdown
---

## Next Steps

**Issue**: Required files for review are missing.

**Recommended**: Run `/doit.implementit` to complete the implementation first.
```
