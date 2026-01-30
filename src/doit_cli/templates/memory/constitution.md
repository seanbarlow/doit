# [PROJECT_NAME] Constitution

> **See also**: [Tech Stack](tech-stack.md) for languages, frameworks, and deployment details.

<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Purpose & Goals

### Project Purpose

[PROJECT_PURPOSE]
<!-- Example: A CLI tool for managing feature specifications and task tracking -->

### Success Criteria

[SUCCESS_CRITERIA]
<!-- Example:
- Reduce feature specification time by 50%
- Enable consistent task breakdown across teams
- Support multiple AI assistants for development -->

## Core Principles

### [PRINCIPLE_1_NAME]

<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]

<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]

<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]

<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]

<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## Quality Standards

[QUALITY_STANDARDS]
<!-- Example: All code MUST include tests. The test suite uses pytest and MUST pass before any release. -->

## Development Workflow

[DEVELOPMENT_WORKFLOW]
<!-- Example:
1. Create feature branch from main
2. Run /doit.specit to create specification
3. Run /doit.planit for technical design
4. Run /doit.taskit for task breakdown
5. Implement with /doit.implementit
6. Review with /doit.reviewit
7. Check in with /doit.checkin -->

## Governance

<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
