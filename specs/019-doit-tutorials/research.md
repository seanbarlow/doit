# Research: DoIt Comprehensive Tutorials

**Feature**: 019-doit-tutorials
**Date**: 2026-01-13
**Status**: Complete

## Research Questions

### RQ-001: What DoIt commands need to be documented?

**Decision**: Document all 10 slash commands in the DoIt workflow

**Commands Identified**:

1. `doit init` - CLI command to initialize DoIt in a project
2. `/doit.constitution` - Create/update project constitution
3. `/doit.scaffoldit` - Generate project structure
4. `/doit.specit` - Create feature specification
5. `/doit.planit` - Generate implementation plan
6. `/doit.taskit` - Create actionable tasks
7. `/doit.implementit` - Execute implementation tasks
8. `/doit.reviewit` - Review implementation
9. `/doit.testit` - Run automated tests
10. `/doit.checkin` - Finalize feature and create PR
11. `/doit.roadmapit` - Manage project roadmap
12. `/doit.documentit` - Organize documentation

**Rationale**: These commands represent the complete spec-driven development workflow

**Alternatives Considered**: None - all commands are part of the core workflow

---

### RQ-002: What tutorial structure works best for developer documentation?

**Decision**: Use a "learn by doing" approach with a realistic sample project

**Structure Elements**:

- **What You'll Build** - Clear outcome at the start
- **Prerequisites** - Checklist format for quick validation
- **Time Estimate** - Set expectations (2 hours greenfield, 90 min existing)
- **Step-by-Step Sections** - One command per major section
- **Code Blocks** - Show exact inputs with syntax highlighting
- **Output Examples** - Show what users should see (abbreviated)
- **Callout Boxes** - Tips, warnings, notes in distinct styling
- **Checkpoint Summaries** - Recap at end of each major section

**Rationale**: This structure follows established patterns from popular developer tutorials (Django Girls, Rails Tutorial, Rust Book)

**Alternatives Considered**:

- Reference documentation style (rejected - less engaging for beginners)
- Video-first approach (rejected - out of scope, harder to maintain)

---

### RQ-003: What sample projects should the tutorials use?

**Decision**: Use domain-specific but simple examples

**Greenfield Tutorial**: TaskFlow CLI

- A command-line task management application
- Simple enough to understand quickly
- Complex enough to demonstrate full workflow
- Sample feature: "Add task priority levels" (involves data model, CLI, storage)

**Existing Project Tutorial**: Weather API

- A pre-existing REST API (Flask or FastAPI)
- Represents common real-world scenario
- Sample feature: "Add weather alerts endpoint"
- Shows how to work with existing patterns

**Rationale**: Task management and weather APIs are universally understood domains

**Alternatives Considered**:

- E-commerce (rejected - too complex for tutorial)
- Todo app (rejected - too simple, won't demonstrate full workflow)
- Blog engine (rejected - less relevant to modern development)

---

### RQ-004: How should interactive command outputs be formatted?

**Decision**: Use annotated transcript format with clear visual distinction

**Format Example**:

```markdown
When you run the command, you'll see prompts like this:

```text
$ /doit.specit Add user authentication

Claude: I'll create a specification for user authentication.

## Question 1: Authentication Method

**Context**: The feature involves user authentication but the method isn't specified.

| Option | Answer        | Implications                    |
| ------ | ------------- | ------------------------------- |
| A      | Email/Password | Traditional, requires DB storage |
| B      | OAuth2         | Delegates to provider           |
| C      | Magic Links    | Passwordless, email-based       |

Your choice: **A** ← (user selects this)

Claude: Got it. I'll proceed with email/password authentication...
```

**Rationale**: Shows the interactive nature of commands clearly

**Alternatives Considered**:

- Screenshots (rejected - harder to maintain, accessibility issues)
- Simplified summaries (rejected - loses important interaction details)

---

### RQ-005: How should platform differences be handled?

**Decision**: Use platform-agnostic examples with callout boxes for differences

**Approach**:

- Default to Unix-style commands (works on Mac/Linux, WSL on Windows)
- Add callout boxes for Windows-specific variations
- Use `$` for shell prompts (universal recognition)
- Avoid platform-specific paths in examples

**Example Callout**:

```markdown
> **Windows Users**: If not using WSL, replace `source .venv/bin/activate`
> with `.venv\Scripts\activate`
```

**Rationale**: Most developers can translate between platforms; WSL makes Windows compatible

**Alternatives Considered**:

- Separate Windows tutorial (rejected - maintenance burden, duplicated content)
- Windows-first examples (rejected - less common in dev tutorials)

---

### RQ-006: What existing documentation should be referenced?

**Decision**: Link to but don't duplicate existing docs

**Referenced Resources**:

- `CONTRIBUTING.md` - For development workflow context
- `README.md` - For installation instructions
- `.doit/templates/` - For understanding generated output structure
- `docs/features/` - For examples of completed features

**Rationale**: Keeps tutorials focused, avoids content drift

---

## Best Practices Identified

### Tutorial Writing

1. **Show, don't tell** - Lead with examples, explain after
2. **One concept at a time** - Each section introduces one command
3. **Provide escape hatches** - What to do if something goes wrong
4. **Test your tutorials** - Follow them end-to-end before publishing

### Documentation Structure

1. **Consistent headings** - Same structure for each command section
2. **Progressive complexity** - Start simple, add nuance
3. **Clear navigation** - Table of contents, section anchors
4. **Searchable content** - Use keywords users will search for

### Code Examples

1. **Complete examples** - No "..." that leaves users guessing
2. **Realistic data** - Use plausible names, not "foo/bar"
3. **Annotated output** - Highlight important parts of responses
4. **Copy-paste friendly** - Users should be able to run examples directly

## Open Questions (Resolved)

| Question | Resolution |
| -------- | ---------- |
| Which sample project for greenfield? | TaskFlow CLI - task management app |
| Which sample project for existing? | Weather API - REST API example |
| Include troubleshooting section? | No - out of scope, separate doc |
| Support non-GitHub users? | Yes - mention `--skip-issues` flag |
