# Feature Specification: Update Doit Templates

**Feature Branch**: `002-update-doit-templates`
**Created**: 2026-01-09
**Status**: Draft
**Input**: User description: "Update templates folder md files and commands to match the doit commands we just created"

## Summary

The templates folder (`.specify/templates/`) contains markdown files that serve as document templates for the doit command suite. These templates currently reference commands and paths that don't exist in the actual implementation. This feature ensures all template files accurately reference the actual doit commands available in `.claude/commands/`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accurate Command References (Priority: P1)

As a developer using the doit command suite, I want template documentation to accurately reference existing commands so that I don't encounter broken references or confusion when following the documented workflow.

**Why this priority**: Core usability - incorrect references break the developer experience and cause confusion about available functionality.

**Independent Test**: Open any template file and verify all `/doit.*` command references correspond to actual commands in `.claude/commands/`.

**Acceptance Scenarios**:

1. **Given** a template file with command references, **When** I review the `/doit.*` references, **Then** each referenced command has a corresponding file in `.claude/commands/`.
2. **Given** the checklist-template.md file, **When** I read it, **Then** it does not reference `/doit.checklist` (which doesn't exist).
3. **Given** the plan-template.md file, **When** I read the Note section, **Then** it references the actual command file location (`.claude/commands/doit.plan.md`) instead of the non-existent `.specify/templates/commands/plan.md`.

---

### User Story 2 - Remove Non-Existent Command References (Priority: P1)

As a developer, I want template files to only reference commands that actually exist so that the documentation accurately reflects the system capabilities.

**Why this priority**: Prevents confusion and wasted time searching for non-existent functionality.

**Independent Test**: Search all template files for command references and verify each one exists.

**Acceptance Scenarios**:

1. **Given** the checklist-template.md, **When** the update is complete, **Then** references to `/doit.checklist` are either removed or replaced with an appropriate existing command.
2. **Given** any template file, **When** searching for `/doit.clarify` references, **Then** zero matches are found (command doesn't exist).

---

### User Story 3 - Consistent Path References (Priority: P2)

As a developer, I want all file path references in templates to point to actual existing locations so that I can navigate the codebase correctly.

**Why this priority**: Secondary to command references but still important for navigation and understanding project structure.

**Independent Test**: Verify all path references in templates point to existing files or directories.

**Acceptance Scenarios**:

1. **Given** plan-template.md, **When** I check the referenced paths, **Then** all paths like `.specify/templates/commands/plan.md` are corrected to actual locations.
2. **Given** any template file with path references, **When** I follow those paths, **Then** the files or directories exist.

---

### Edge Cases

- What happens if a template needs to reference a future/planned command? Document with clear "planned" or "TODO" markers.
- How should templates handle commands that exist but aren't part of the primary workflow? Include only in relevant templates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All template files MUST only reference commands that exist in `.claude/commands/`.
- **FR-002**: The checklist-template.md MUST NOT reference `/doit.checklist` (non-existent command).
- **FR-003**: The plan-template.md MUST reference `.claude/commands/doit.plan.md` instead of `.specify/templates/commands/plan.md`.
- **FR-004**: All templates MUST use the correct command naming convention (`/doit.<command-name>`).
- **FR-005**: Path references in templates MUST point to existing files or directories.
- **FR-006**: The doit.specify.md command MUST NOT reference `/doit.clarify` (non-existent command).

### Affected Files

- **checklist-template.md**: References `/doit.checklist` which doesn't exist
- **plan-template.md**: References non-existent path `.specify/templates/commands/plan.md`
- **tasks-template.md**: References `/doit.tasks` (valid - no changes needed)
- **doit.specify.md**: References `/doit.clarify` which doesn't exist

### Available doit Commands (for reference)

- `/doit.checkin` - Finalize feature implementation
- `/doit.constitution` - Create/update project constitution
- `/doit.implement` - Execute implementation plan
- `/doit.plan` - Execute implementation planning workflow
- `/doit.review` - Review implemented code
- `/doit.scaffold` - Generate project structure
- `/doit.specify` - Create feature specification
- `/doit.tasks` - Generate task list
- `/doit.test` - Execute automated tests

## Assumptions

- The command naming convention will remain as `/doit.<command-name>`.
- Commands in `.claude/commands/` directory are the source of truth.
- If `/doit.checklist` functionality is needed, it should be implemented as a separate feature.
- If `/doit.clarify` functionality is needed, it should be implemented as a separate feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero template files contain references to non-existent commands.
- **SC-002**: 100% of path references in templates resolve to existing files or directories.
- **SC-003**: Developers can follow template documentation without encountering broken references.
- **SC-004**: All 5 template files pass validation for accurate command and path references.
