# Doit Testit

Execute automated tests and generate test reports with requirement mapping

## User Input

Consider any arguments or options the user provides.

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

1. **Setup**: Run `.doit/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. **Load test context**:
   - **REQUIRED**: Read spec.md for requirements (FR-XXX identifiers)
   - **REQUIRED**: Read tasks.md for test file locations
   - **IF EXISTS**: Read plan.md for test strategy and coverage goals
   - **IF EXISTS**: Read contracts/ for API test expectations

3. **Detect test framework**:
   - Check for test configuration files:
     - **Python**: pytest.ini, pyproject.toml [tool.pytest], setup.cfg, conftest.py
     - **JavaScript/TypeScript**: jest.config.js/ts, vitest.config.js/ts, mocha.opts, .mocharc.*
     - **Java**: pom.xml (maven-surefire), build.gradle (test task)
     - **Go**: *_test.go files present
     - **Ruby**: Rakefile, .rspec, spec/ directory
     - **C#/.NET**: *.csproj with test SDK, xunit, nunit references
     - **Rust**: Cargo.toml with [dev-dependencies] test crates
   - Determine test command:
     - pytest: `pytest -v --tb=short`
     - jest: `npm test` or `npx jest`
     - vitest: `npm test` or `npx vitest run`
     - go: `go test ./...`
     - maven: `mvn test`
     - gradle: `./gradlew test`
     - dotnet: `dotnet test`
     - cargo: `cargo test`

4. **Execute test suite**:
   - Run detected test command
   - Capture stdout/stderr
   - Parse test results:
     - Total tests run
     - Passed tests
     - Failed tests
     - Skipped tests
     - Test duration
   - Capture any coverage reports if generated

5. **Generate test report**:

   ```text
   ## Automated Test Results

   **Framework**: [detected framework]
   **Command**: [test command used]
   **Duration**: [total time]

   ### Summary
   | Metric | Count |
   |--------|-------|
   | Total | X |
   | Passed | X |
   | Failed | X |
   | Skipped | X |

   ### Failed Tests
   | Test | File | Error |
   |------|------|-------|
   | test_name | path/to/test.py | AssertionError: ... |

   ### Coverage (if available)
   | File | Coverage |
   |------|----------|
   | src/module.py | 85% |
   ```

6. **Map tests to requirements**:
   - Parse test names and docstrings for FR-XXX references
   - Match tests to requirements from spec.md
   - Generate requirement coverage matrix:

     ```text
     ## Requirement Coverage

     | Requirement | Description | Tests | Status |
     |-------------|-------------|-------|--------|
     | FR-001 | User login | test_login, test_auth | COVERED |
     | FR-002 | Password reset | - | NOT COVERED |
     | FR-003 | Session timeout | test_session_expiry | COVERED |
     ```

   - Calculate coverage percentage: (covered requirements / total requirements) * 100

7. **Generate manual testing checklist**:
   - Extract acceptance criteria from spec.md that cannot be automated
   - Create checklist format:

     ```text
     ## Manual Testing Checklist

     ### UI/UX Tests
     - [ ] MT-001: Verify login form displays correctly on mobile
     - [ ] MT-002: Verify error messages are user-friendly

     ### Integration Tests
     - [ ] MT-003: Verify third-party payment processing
     - [ ] MT-004: Verify email notifications are received

     ### Edge Cases
     - [ ] MT-005: Verify behavior with slow network
     - [ ] MT-006: Verify recovery from server timeout
     ```

8. **Record manual test results**:
   - If the user's input contains `--manual`:
     - Present each manual test item
     - Ask for PASS/FAIL/SKIP result
     - Record notes for failed tests
     - Track completion progress
   - Otherwise, output checklist for later completion

9. **Generate test-report.md** in FEATURE_DIR:

   ```markdown
   # Test Report: [Feature Name]

   **Date**: [timestamp]
   **Branch**: [current branch]
   **Test Framework**: [detected]

   ## Automated Tests

   ### Execution Summary
   | Metric | Value |
   |--------|-------|
   | Total Tests | X |
   | Passed | X |
   | Failed | X |
   | Skipped | X |
   | Duration | Xs |

   ### Failed Tests Detail
   [list of failed tests with errors]

   ### Code Coverage
   [coverage summary if available]

   ## Requirement Coverage

   | Requirement | Tests | Status |
   |-------------|-------|--------|
   | FR-XXX | test_xxx | COVERED |
   ...

   **Coverage**: X/Y requirements (Z%)

   ## Manual Testing

   ### Checklist Status
   | Test ID | Description | Status |
   |---------|-------------|--------|
   | MT-001 | ... | PENDING |
   ...

   ## Recommendations

   1. [Fix failing tests before merge]
   2. [Add tests for uncovered requirements]
   3. [Complete manual testing checklist]

   ## Next Steps

   - Fix any failing tests
   - Complete manual testing if not done
   - Run `/doit.checkin` when all tests pass
   ```

10. **Report**: Output path to test-report.md and summary:
    - Automated test pass rate
    - Requirement coverage percentage
    - Manual test completion status
    - Overall readiness for merge

## Key Rules

- Use absolute paths for all file operations
- If no test framework detected, report and suggest adding tests
- Continue generating report even if some tests fail
- Preserve test output for debugging
- Map requirements using FR-XXX pattern matching in test names/docstrings

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (all tests pass)

Display the following at the end of your output:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                                      │
│  ● specit → ● planit → ● taskit → ● implementit → ● testit → ○ checkin │
└─────────────────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.reviewit` for a code review before finalizing.

**Alternative**: Run `/doit.checkin` to merge your changes if code review is not needed.
```

### On Failure (tests fail)

If some tests fail:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                                      │
│  ● specit → ● planit → ● taskit → ● implementit → ◐ testit → ○ checkin │
└─────────────────────────────────────────────────────────────────────────┘

**Status**: N tests failed out of M total.

**Recommended**: Run `/doit.implementit` to fix the failing tests.
```

### On Error (no test framework detected)

If no test framework is detected:

```markdown
---

## Next Steps

**Issue**: No test framework detected in this project.

**Recommended**: Add tests to your project and run `/doit.testit` again, or proceed with `/doit.reviewit` for code review.
```
