# [PROJECT_NAME] Constitution

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

## Tech Stack

### Languages

[PRIMARY_LANGUAGE]
<!-- Example: Python 3.11+ (primary), TypeScript (frontend) -->

### Frameworks

[FRAMEWORKS]
<!-- Example: FastAPI (API), React (frontend), pytest (testing) -->

### Libraries

[KEY_LIBRARIES]
<!-- Example: Pydantic (validation), SQLAlchemy (ORM), Rich (CLI) -->

## Infrastructure

### Hosting

[HOSTING_PLATFORM]
<!-- Example: AWS ECS, Google Cloud Run, Azure Container Apps, Self-hosted -->

### Cloud Provider

[CLOUD_PROVIDER]
<!-- Example: AWS, GCP, Azure, Multi-cloud, On-premises -->

### Database

[DATABASE]
<!-- Example: PostgreSQL (primary), Redis (cache), none -->

## Deployment

### CI/CD Pipeline

[CICD_PIPELINE]
<!-- Example: GitHub Actions, GitLab CI, Jenkins, CircleCI -->

### Deployment Strategy

[DEPLOYMENT_STRATEGY]
<!-- Example: Blue-green, Rolling, Canary, Manual -->

### Environments

[ENVIRONMENTS]
<!-- Example: dev, staging, production -->

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

## [SECTION_2_NAME]

<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## [SECTION_3_NAME]

<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance

<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
