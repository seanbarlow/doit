# Feature Specification: Doit Command Refactoring

**Feature Branch**: `001-doit-command-refactor`
**Created**: 2026-01-09
**Status**: Draft
**Input**: Refactor speckit codebase to rename base command from "speckit" to "doit" and simplify commands to: constitution, specify, plan, tasks, implement, review, test, checkin

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rename Base Command (Priority: P1)

As a developer using the spec-driven workflow, I want all commands to use "doit" as the base command name instead of "speckit" so that the tool has a simpler, more memorable identity.

**Why this priority**: This is the foundational change that enables all other refactoring. Without renaming the base command, the tool cannot be rebranded.

**Independent Test**: Can be fully tested by running any doit command (e.g., `/doit.specify "test feature"`) and verifying it executes correctly with the new naming.

**Acceptance Scenarios**:

1. **Given** I have the doit tool installed, **When** I run `/doit.specify "create a login page"`, **Then** the specify command executes and creates a feature branch and spec file
2. **Given** I have an existing speckit installation, **When** I upgrade to doit, **Then** all command files are renamed from `speckit.*` to `doit.*`
3. **Given** I run any old speckit command (e.g., `/speckit.plan`), **When** the command is not found, **Then** a helpful message suggests using the new doit command name

---

### User Story 2 - Consolidate Specify Command (Priority: P1)

As a developer, I want the specify command to include clarification and analysis capabilities so that I can create complete, validated specifications in a single workflow step.

**Why this priority**: The specify command is the entry point for all features. Making it self-contained reduces workflow friction.

**Independent Test**: Run `/doit.specify "complex feature"` and verify it prompts for clarifications during spec creation and validates the spec before completion.

**Acceptance Scenarios**:

1. **Given** I provide a vague feature description, **When** I run doit.specify, **Then** the command asks up to 5 clarifying questions before generating the spec
2. **Given** I have completed answering clarifications, **When** the spec is generated, **Then** no [NEEDS CLARIFICATION] markers remain in the output
3. **Given** the spec is generated, **When** I review it, **Then** it includes all 8 analysis categories from the former clarify command (Functional Scope, Domain Model, UX Flow, etc.)

---

### User Story 3 - Plan Command (Priority: P1)

As a developer, I want the plan command to generate technical architecture and design documents from my specification so that I have a clear implementation roadmap.

**Why this priority**: Technical planning is essential before implementation begins.

**Independent Test**: Run `/doit.plan` on a spec and verify it generates plan.md and supporting design artifacts.

**Acceptance Scenarios**:

1. **Given** I have a completed spec.md, **When** I run doit.plan, **Then** it generates plan.md, research.md, data-model.md, and contracts/
2. **Given** the plan is generated, **When** I review it, **Then** it contains architecture decisions aligned with the spec
3. **Given** uncertainties exist during planning, **When** research is needed, **Then** findings are documented in research.md

---

### User Story 4 - Tasks Command with GitHub Issues (Priority: P1)

As a developer, I want the tasks command to generate actionable tasks AND automatically create GitHub issues so that my work is tracked both locally and in my project management system.

**Why this priority**: Task generation with issue tracking is critical for team coordination and must happen before implementation.

**Independent Test**: Run `/doit.tasks` on a plan and verify it generates tasks.md and creates corresponding GitHub issues.

**Acceptance Scenarios**:

1. **Given** I have a completed plan.md, **When** I run doit.tasks, **Then** it generates tasks.md with dependency-ordered tasks
2. **Given** the project has a GitHub remote configured, **When** doit.tasks completes, **Then** GitHub issues are automatically created for each task
3. **Given** the project does not have a GitHub remote, **When** doit.tasks completes, **Then** tasks.md is created and a message informs that GitHub issues were skipped
4. **Given** I want to skip GitHub issue creation, **When** I run doit.tasks with a skip flag, **Then** only tasks.md is created locally

---

### User Story 5 - New Review Command (Priority: P2)

As a developer, I want a review command that performs code review and guides me through manual testing after implementation so that I can validate my work before considering the feature complete.

**Why this priority**: Post-implementation validation is critical for quality but currently has no dedicated command.

**Independent Test**: After implementing a feature, run `/doit.review` and verify it analyzes the code and presents a manual testing checklist.

**Acceptance Scenarios**:

1. **Given** I have completed implementing tasks, **When** I run doit.review, **Then** the command performs automated code review against the spec and plan
2. **Given** the code review is complete, **When** issues are found, **Then** they are presented with severity, location, and recommended fixes
3. **Given** the automated review passes, **When** manual testing items exist, **Then** the command walks me through each manual test step
4. **Given** I am completing manual testing, **When** I confirm each test passes, **Then** the command tracks my progress and generates a sign-off report
5. **Given** all tests pass, **When** I provide sign-off, **Then** the feature is marked as review-complete

---

### User Story 6 - New Test Command (Priority: P2)

As a developer, I want a test command that executes all automated tests and generates a comprehensive testing report so that I have documented proof of quality.

**Why this priority**: Test execution and reporting should be a first-class citizen in the workflow for quality assurance.

**Independent Test**: Run `/doit.test` and verify it executes the test suite and generates a report linked to the spec.

**Acceptance Scenarios**:

1. **Given** I have implemented code with tests, **When** I run doit.test, **Then** all automated tests are executed
2. **Given** tests have run, **When** execution completes, **Then** a testing report is generated showing pass/fail status for each test
3. **Given** the testing report is generated, **When** I review it, **Then** it maps test results back to requirements in spec.md
4. **Given** manual testing items exist, **When** doit.test runs, **Then** it presents a manual checklist for user verification
5. **Given** I complete manual testing, **When** I mark items as passed/failed, **Then** results are recorded in the testing report

---

### User Story 7 - Implement Command with Checklist Gate (Priority: P2)

As a developer, I want the implement command to verify checklist completion before starting work so that I don't begin implementation with incomplete requirements.

**Why this priority**: The checklist gate ensures quality by catching specification issues before code is written.

**Independent Test**: Run `/doit.implement` and verify it checks checklist status before proceeding with task execution.

**Acceptance Scenarios**:

1. **Given** I have tasks.md and checklists exist, **When** I run doit.implement, **Then** it displays checklist completion status before proceeding
2. **Given** checklists are incomplete, **When** I run doit.implement, **Then** it warns me and requires confirmation to proceed
3. **Given** I confirm to proceed despite incomplete checklists, **When** implementation begins, **Then** tasks are executed in dependency order
4. **Given** implementation is in progress, **When** a task is completed, **Then** tasks.md is updated with completion markers
5. **Given** all tasks are complete, **When** implementation finishes, **Then** a summary report is generated showing completed work

---

### User Story 8 - Enhanced Constitution Command (Priority: P1)

As a project lead, I want the constitution command to capture project purpose, tech stack, frameworks, libraries, and infrastructure requirements so that all subsequent commands have full context about the project's technical environment.

**Why this priority**: The constitution is the foundation for all other commands. Tech stack and infrastructure context enables better code generation and planning.

**Independent Test**: Run `/doit.constitution` and verify it prompts for project purpose, tech stack, and infrastructure, then documents all responses.

**Acceptance Scenarios**:

1. **Given** I start a new project, **When** I run doit.constitution, **Then** I am asked about the project's purpose and goals
2. **Given** I am setting up constitution, **When** prompted for tech stack, **Then** I can specify programming languages, frameworks, and major libraries
3. **Given** I am setting up constitution, **When** prompted for infrastructure, **Then** I can specify target hosting environment, cloud provider, and deployment strategy
4. **Given** I complete all prompts, **When** constitution is saved, **Then** it contains sections for: Purpose, Principles, Tech Stack, Frameworks/Libraries, and Infrastructure
5. **Given** I have an existing constitution, **When** I run doit.constitution, **Then** I can update any section including tech stack and infrastructure
6. **Given** the constitution exists, **When** other doit commands run, **Then** they can reference the tech stack and infrastructure for context-aware generation

---

### User Story 9 - New Checkin Command (Priority: P2)

As a developer, I want a checkin command that finalizes my feature by closing GitHub issues, updating roadmaps, generating documentation, and creating a pull request so that my work is properly wrapped up and ready for merge.

**Why this priority**: The checkin command is the final workflow step that ensures all loose ends are tied up before merging.

**Independent Test**: After completing review and test, run `/doit.checkin` and verify it closes issues, updates roadmaps, generates docs, and creates a PR.

**Acceptance Scenarios**:

1. **Given** I have completed all tasks, **When** I run doit.checkin, **Then** all associated GitHub issues are reviewed and closed
2. **Given** GitHub issues are closed, **When** the checkin continues, **Then** the feature is added to roadmap_completed.md in the project root
3. **Given** roadmap_completed.md is updated, **When** the checkin continues, **Then** roadmap.md is updated to remove the completed feature
4. **Given** roadmaps are updated, **When** the checkin continues, **Then** documentation for the feature is generated in the docs/ folder
5. **Given** documentation is generated, **When** the checkin continues, **Then** all changes are committed with a descriptive message
6. **Given** changes are committed, **When** the checkin completes, **Then** a pull request is created to merge the feature branch into develop

---

### User Story 10 - GitHub Issue Templates (Priority: P1)

As a developer, I want standardized GitHub issue templates for Epics, Features, and Tasks so that all issues are consistently structured and properly linked in a hierarchy.

**Why this priority**: Issue templates ensure consistency and traceability across all GitHub issues created by the workflow.

**Independent Test**: Create issues using each template and verify they contain required sections and proper parent linking.

**Acceptance Scenarios**:

1. **Given** I run doit.specify, **When** a GitHub remote exists, **Then** an Epic issue is created using the Epic template with spec summary, success criteria, and user story links
2. **Given** an Epic issue exists, **When** doit.specify creates Feature issues for user stories, **Then** each Feature issue links back to the parent Epic
3. **Given** I run doit.tasks, **When** Task issues are created, **Then** each Task issue links to its parent Feature issue
4. **Given** any issue is created, **When** I view it in GitHub, **Then** it contains acceptance criteria, labels, and proper metadata
5. **Given** I navigate from a Task issue, **When** I follow the parent links, **Then** I can trace up to Feature and then to Epic

---

### User Story 11 - New Scaffold Command (Priority: P1)

As a developer, I want a scaffold command that creates or analyzes project structure based on my tech stack so that my project follows best practices from the start with proper folder organization, config files, and starter files.

**Why this priority**: Proper project structure is foundational. Scaffold uses constitution's tech stack to generate appropriate structure before any feature development begins.

**Independent Test**: Run `/doit.scaffold` after constitution and verify it creates the appropriate folder structure, config files, and starter files based on tech stack.

**Acceptance Scenarios**:

1. **Given** I have a constitution with tech stack defined, **When** I run doit.scaffold on a new project, **Then** it generates folder structure matching best practices for my tech stack
2. **Given** I specify React as UI framework, **When** scaffold runs, **Then** it creates appropriate React folder structure (src/components/, src/hooks/, etc.) and config files (tsconfig.json, package.json)
3. **Given** I specify .NET as API framework, **When** scaffold runs, **Then** it creates appropriate .NET folder structure (Controllers/, Services/, Models/) and config files (.csproj, appsettings.json)
4. **Given** the constitution defines multiple tech stacks (frontend + backend), **When** scaffold runs, **Then** it creates appropriate structure for each with clear separation
5. **Given** I run scaffold on an existing project, **When** the structure doesn't match best practices, **Then** it generates a report of recommended changes without modifying files
6. **Given** the scaffold runs successfully, **When** it completes, **Then** it creates a .gitignore file with appropriate patterns for all tech stacks in use
7. **Given** the scaffold runs, **When** generating starter files, **Then** it creates README.md, Dockerfile (if applicable), and appropriate package/dependency files
8. **Given** I run scaffold, **When** prompted for clarification, **Then** it asks specific questions about my tech choices (UI framework, API framework, database, testing tools)

---

### Edge Cases

- What happens when a user runs an old speckit command after migration? The system should display a helpful migration message pointing to the equivalent doit command.
- How does doit.plan handle GitHub issue creation failure? It should continue with local artifact creation and report the issue creation failure separately.
- What happens when doit.review is run before implementation is complete? It should warn the user and ask for confirmation to proceed.
- How does doit.test handle projects without a test suite? It should skip automated testing and proceed to manual testing checklist only.
- What happens when doit.checkin is run but some GitHub issues are still open? It should list open issues and ask for confirmation to close them or abort.
- How does doit.checkin handle missing roadmap.md? It should create the file if it doesn't exist.
- What happens if the develop branch doesn't exist? It should prompt the user to specify an alternative target branch or create develop.
- How does doit.checkin handle PR creation failure? It should commit changes locally and provide manual PR creation instructions.
- What happens when a Feature issue is created but the parent Epic doesn't exist? It should create the Epic first, then link the Feature.
- How does the system handle orphaned Task issues (no parent Feature)? Tasks should always link to a Feature; if none exists, link directly to Epic.
- What happens when issue templates are missing from the repository? The system should use built-in default templates.
- What happens when scaffold is run without a constitution? It should prompt the user to run constitution first or ask tech stack questions inline.
- How does scaffold handle unsupported tech stacks? It should generate a generic structure and warn the user that specific best practices may not be applied.
- What happens when scaffold detects conflicting tech stacks (e.g., React + Vue)? It should ask for clarification on the intended architecture.
- How does scaffold handle monorepo vs single-app projects? It should ask and generate appropriate structure for each.

## Requirements *(mandatory)*

### Functional Requirements

**Command Renaming**
- **FR-001**: System MUST rename all command files from `speckit.*` to `doit.*` in `.claude/commands/` directory
- **FR-002**: System MUST update all internal references from "speckit" to "doit" in command files, templates, and scripts
- **FR-003**: System MUST update the Python CLI from `specify_cli` to support the "doit" branding

**Constitution Command (Enhanced)**
- **FR-004**: The doit.constitution command MUST prompt for project purpose and goals
- **FR-005**: The doit.constitution command MUST prompt for tech stack including programming languages
- **FR-006**: The doit.constitution command MUST prompt for frameworks and major libraries being used
- **FR-007**: The doit.constitution command MUST prompt for target infrastructure and hosting environment
- **FR-008**: The doit.constitution command MUST prompt for cloud provider preferences (if applicable)
- **FR-009**: The doit.constitution command MUST prompt for deployment strategy and CI/CD requirements
- **FR-010**: The doit.constitution command MUST save all responses in structured sections within constitution.md
- **FR-011**: The doit.constitution command MUST allow updating individual sections without re-entering all information
- **FR-012**: The constitution.md MUST include sections for: Purpose, Principles, Tech Stack, Frameworks/Libraries, Infrastructure, and Deployment
- **FR-013**: All doit commands MUST be able to read and use constitution tech stack and infrastructure context

**Specify Command Consolidation**
- **FR-014**: The doit.specify command MUST include clarification question capability (up to 5 questions) during spec generation
- **FR-015**: The doit.specify command MUST perform analysis across 8 categories before finalizing the spec
- **FR-016**: The doit.specify command MUST produce specs with no [NEEDS CLARIFICATION] markers upon completion

**Plan Command**
- **FR-017**: The doit.plan command MUST generate plan.md, research.md, data-model.md, and contracts/
- **FR-018**: The doit.plan command MUST align architecture decisions with the spec requirements and constitution tech stack

**Tasks Command with GitHub Issues**
- **FR-019**: The doit.tasks command MUST generate tasks.md with dependency-ordered tasks
- **FR-020**: The doit.tasks command MUST automatically create GitHub issues when a GitHub remote is detected
- **FR-021**: The doit.tasks command MUST provide an option to skip GitHub issue creation
- **FR-022**: The doit.tasks command MUST handle GitHub API failures gracefully without blocking local task generation

**Review Command (New)**
- **FR-023**: The doit.review command MUST perform automated code review comparing implementation to spec and plan
- **FR-024**: The doit.review command MUST present code issues with severity, location, and recommendations
- **FR-025**: The doit.review command MUST present manual testing checklist items sequentially
- **FR-026**: The doit.review command MUST track manual test progress and generate sign-off report
- **FR-027**: The doit.review command MUST require explicit user sign-off to mark feature as complete

**Test Command (New)**
- **FR-028**: The doit.test command MUST detect and execute the project's test suite
- **FR-029**: The doit.test command MUST generate a testing report with pass/fail status per test
- **FR-030**: The doit.test command MUST map test results to requirements in spec.md
- **FR-031**: The doit.test command MUST present manual testing checklist when manual items exist
- **FR-032**: The doit.test command MUST record manual test results in the testing report

**Implement Command (with Checklist Gate)**
- **FR-033**: The doit.implement command MUST check and display checklist completion status before starting
- **FR-034**: The doit.implement command MUST warn and require confirmation when checklists are incomplete
- **FR-035**: The doit.implement command MUST mark tasks complete in tasks.md as they are finished
- **FR-036**: The doit.implement command MUST generate completion summary report

**Checkin Command (New)**
- **FR-037**: The doit.checkin command MUST review all GitHub issues associated with the feature and close completed ones
- **FR-038**: The doit.checkin command MUST prompt for confirmation before closing issues that appear incomplete
- **FR-039**: The doit.checkin command MUST create or update roadmap_completed.md in the project root with the completed feature
- **FR-040**: The doit.checkin command MUST update roadmap.md in the project root to reflect feature completion
- **FR-041**: The doit.checkin command MUST generate feature documentation in the docs/ folder
- **FR-042**: The doit.checkin command MUST commit all changes with a descriptive commit message
- **FR-043**: The doit.checkin command MUST create a pull request targeting the develop branch
- **FR-044**: The doit.checkin command MUST handle missing develop branch by prompting for alternative target

**GitHub Issue Templates**
- **FR-045**: System MUST provide an Epic issue template with sections for: Summary, Success Criteria, User Stories (linked), Acceptance Criteria, and Labels
- **FR-046**: System MUST provide a Feature issue template with sections for: Description, Parent Epic (linked), Acceptance Scenarios, Priority, and Labels
- **FR-047**: System MUST provide a Task issue template with sections for: Description, Parent Feature (linked), Definition of Done, Estimated Effort, and Labels
- **FR-048**: The doit.specify command MUST create an Epic issue when GitHub remote is configured
- **FR-049**: The doit.specify command MUST create Feature issues for each user story, linked to the Epic
- **FR-050**: The doit.tasks command MUST create Task issues linked to their parent Feature issues
- **FR-051**: All issue templates MUST include a "Part of" section showing the issue hierarchy (Task -> Feature -> Epic)
- **FR-052**: Epic issues MUST be labeled with `epic` and the feature branch name
- **FR-053**: Feature issues MUST be labeled with `feature`, priority level, and linked Epic number
- **FR-054**: Task issues MUST be labeled with `task`, phase, and linked Feature number
- **FR-055**: Issue templates MUST be stored in `.github/ISSUE_TEMPLATE/` directory

**Scaffold Command (New)**

- **FR-056**: The doit.scaffold command MUST read tech stack information from constitution.md
- **FR-057**: The doit.scaffold command MUST ask clarifying questions about tech choices (UI framework, API framework, database, testing tools) if not specified in constitution
- **FR-058**: The doit.scaffold command MUST generate folder structure matching best practices for the specified tech stack
- **FR-059**: The doit.scaffold command MUST create appropriate config files for the tech stack (e.g., tsconfig.json, package.json, .csproj, appsettings.json)
- **FR-060**: The doit.scaffold command MUST create starter files including README.md and appropriate package/dependency files
- **FR-061**: The doit.scaffold command MUST create Dockerfile when containerization is part of the infrastructure requirements
- **FR-062**: The doit.scaffold command MUST generate a .gitignore file with patterns appropriate for all tech stacks in use
- **FR-063**: The doit.scaffold command MUST support multi-stack projects (e.g., React frontend + .NET backend) with clear separation
- **FR-064**: The doit.scaffold command MUST NOT modify existing files when analyzing an existing project
- **FR-065**: The doit.scaffold command MUST generate a structure analysis report when run on existing projects with recommendations for improvements
- **FR-066**: The doit.scaffold command MUST support common tech stacks including: React, Vue, Angular, .NET, Node.js, Python, Go, Java

**Command Removal**

- **FR-067**: The speckit.clarify command MUST be removed (functionality absorbed into specify)
- **FR-068**: The speckit.analyze command MUST be removed (functionality absorbed into specify and review)
- **FR-069**: The speckit.checklist command MUST be removed (functionality absorbed into specify and review)
- **FR-070**: The speckit.taskstoissues command MUST be removed (functionality absorbed into tasks)

### Key Entities

- **Command**: A markdown file defining a workflow step with description, handoffs, and execution outline
- **Constitution**: Project foundation document containing Purpose, Principles, Tech Stack, Frameworks/Libraries, Infrastructure, and Deployment strategy
- **Scaffold**: Project structure configuration defining folder organization, config files, and starter files based on tech stack
- **Structure Analysis Report**: Report generated when scaffold analyzes existing projects, listing recommendations without modifying files
- **Spec**: Feature specification document capturing what and why (not how)
- **Plan**: Technical implementation plan with architecture decisions and task breakdown
- **Task**: Actionable work item with ID, priority, dependencies, and description
- **Review Report**: Code review findings and manual testing results with sign-off status
- **Test Report**: Automated and manual test results mapped to requirements
- **Roadmap**: Project-level tracking document (roadmap.md) listing planned features
- **Roadmap Completed**: Project-level archive (roadmap_completed.md) of finished features
- **Feature Documentation**: Generated documentation in docs/ folder describing implemented feature
- **Pull Request**: GitHub PR created to merge feature branch into develop
- **Epic Issue**: Top-level GitHub issue representing the entire spec/feature, contains success criteria and links to all Feature issues
- **Feature Issue**: GitHub issue representing a user story, links to parent Epic and contains acceptance scenarios
- **Task Issue**: GitHub issue representing an individual task, links to parent Feature and contains definition of done
- **Issue Template**: Markdown template in `.github/ISSUE_TEMPLATE/` defining structure for Epic, Feature, or Task issues

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Total number of user-facing commands is 9 (constitution, scaffold, specify, plan, tasks, implement, review, test, checkin)
- **SC-002**: Users can complete the full workflow (specify through checkin) with a clear linear progression
- **SC-003**: 100% of speckit command references updated to doit across all files
- **SC-004**: New users can learn the complete workflow in under 10 minutes (reduced cognitive load)
- **SC-005**: Zero functionality loss - all capabilities from removed commands are preserved in consolidated commands
- **SC-006**: GitHub issue creation success rate of 95% when GitHub remote is properly configured
- **SC-007**: Review command generates actionable findings for 80% of common code issues
- **SC-008**: Test command correctly maps 90% of automated tests to their corresponding requirements
- **SC-009**: Checkin command successfully creates PR in 95% of cases when GitHub remote is configured
- **SC-010**: 100% of completed features are documented in roadmap_completed.md after checkin
- **SC-011**: 100% of Task issues link to their parent Feature, and 100% of Feature issues link to their parent Epic
- **SC-012**: All GitHub issues created by doit commands use the standardized templates with required sections
- **SC-013**: Scaffold command generates valid, working project structure for supported tech stacks in 95% of cases
- **SC-014**: Constitution captures tech stack and infrastructure information in 100% of new project setups

## Assumptions

1. The existing speckit command infrastructure (markdown files, scripts, templates) will be preserved and renamed rather than rebuilt from scratch
2. Users will access commands through the same mechanism (slash commands in Claude/AI assistant)
3. GitHub issue creation will use the existing MCP server integration
4. The Python CLI update is optional and can be done in a separate iteration if needed
5. Existing projects using speckit will need a manual migration (or simple find/replace)

## Dependencies

- GitHub MCP server for issue creation functionality
- Existing template files (.specify/templates/)
- Existing script files (.specify/scripts/)
- Git repository for branch management

## Out of Scope

- Backward compatibility layer for speckit commands (migration is one-way)
- GUI or web interface for commands
- Integration with non-GitHub issue trackers (GitLab, Jira, etc.)
- Automated migration tool for existing speckit projects
