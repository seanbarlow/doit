---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.
handoffs:
  - label: Build Specification
    agent: doit.doit
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Cleanup Subcommand

If the user requests "cleanup" or "separate tech stack", use the CLI command:

```bash
# Preview what would be changed
doit constitution cleanup --dry-run

# Perform the cleanup (creates backup automatically)
doit constitution cleanup

# Merge with existing tech-stack.md if it already exists
doit constitution cleanup --merge
```

The cleanup command:

- Analyzes constitution.md for tech-stack sections (Tech Stack, Infrastructure, Deployment)
- Creates a timestamped backup of constitution.md
- Extracts tech sections to a new tech-stack.md
- Adds cross-references between both files

After running cleanup, inform the user about the two files:

- `.doit/memory/constitution.md` - Principles, governance, quality standards, workflow
- `.doit/memory/tech-stack.md` - Languages, frameworks, libraries, infrastructure, deployment

## Load Project Context

Before proceeding, load the project context to inform your responses:

```bash
doit context show
```

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:

- Reference existing constitution principles (if updating existing constitution)
- Consider roadmap priorities (already in context)
- Identify connections to related specifications

**Note**: Constitution is the source file being modified, so reading it for modification is legitimate.

**DO NOT read these files again** (already in context above):

- `.doit/memory/roadmap.md` - priorities are in context
- `.doit/memory/tech-stack.md` - tech decisions are in context (unless modifying it)

**Legitimate explicit reads** (for template sync validation in step 6):

- `.doit/templates/plan-template.md` - for consistency check
- `.doit/templates/spec-template.md` - for consistency check
- `.doit/templates/tasks-template.md` - for consistency check
- `.doit/templates/commands/*.md` - for consistency check

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

You are updating the project constitution at `.doit/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.doit/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. **Section-by-Section Update Mode**:
   If user input specifies a particular section to update (e.g., "update tech stack" or "change deployment"), focus on that section only while preserving other sections. Supported section keywords:
   - "purpose" / "goals" → Purpose & Goals section
   - "tech" / "stack" / "language" → Tech Stack section
   - "infrastructure" / "hosting" / "cloud" → Infrastructure section
   - "deployment" / "ci" / "cd" → Deployment section
   - "principles" → Core Principles section
   - "governance" → Governance section

   If no specific section mentioned, proceed with full constitution review.

3. **Guided Prompts for New Placeholders**:
   When collecting values for the following placeholders, use these prompts if values not provided:

   **Purpose & Goals:**
   - [PROJECT_PURPOSE]: "What is the main purpose of this project? What problem does it solve?"
   - [SUCCESS_CRITERIA]: "What are the key success metrics or criteria for this project?"

   **Tech Stack (FR-005, FR-006):**
   - [PRIMARY_LANGUAGE]: "What programming language(s) will this project use? (e.g., Python 3.11+, TypeScript)"
   - [FRAMEWORKS]: "What frameworks will you use? (e.g., FastAPI, React, Django)"
   - [KEY_LIBRARIES]: "What key libraries/packages are essential? (e.g., Pydantic, SQLAlchemy)"

   **Infrastructure (FR-007, FR-008):**
   - [HOSTING_PLATFORM]: "Where will this be hosted? (e.g., AWS ECS, Google Cloud Run, Vercel, self-hosted)"
   - [CLOUD_PROVIDER]: "Which cloud provider? (AWS, GCP, Azure, multi-cloud, on-premises)"
   - [DATABASE]: "What database(s) will you use? (e.g., PostgreSQL, MongoDB, none)"

   **Deployment:**
   - [CICD_PIPELINE]: "What CI/CD system? (e.g., GitHub Actions, GitLab CI, Jenkins)"
   - [DEPLOYMENT_STRATEGY]: "What deployment strategy? (blue-green, rolling, canary, manual)"
   - [ENVIRONMENTS]: "What environments? (e.g., dev, staging, production)"

4. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

5. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

6. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.doit/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.doit/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.doit/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.doit/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

7. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

8. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

9. Write the completed constitution back to `.doit/memory/constitution.md` (overwrite).

10. Output a final summary to the user with:
    - New version and bump rationale.
    - Any files flagged for manual follow-up.
    - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.doit/memory/constitution.md` file.

## Context Sources Reference

Other commands access project configuration via `doit context show`, which loads:

**Constitution** (`.doit/memory/constitution.md`):

- Purpose & Goals - Project purpose and success criteria
- Core Principles - Non-negotiable project rules
- Quality Standards - Testing and quality requirements
- Development Workflow - Step-by-step process
- Governance - Amendment rules and compliance

**Tech Stack** (`.doit/memory/tech-stack.md`):

- Languages - Primary and secondary languages
- Frameworks - Application frameworks
- Libraries - Key dependencies
- Infrastructure - Hosting, cloud provider, database
- Deployment - CI/CD, strategy, environments

**Usage in other commands**:

```text
# At the start of any command that needs project context:
1. Run `doit context show` - this loads constitution, tech-stack, roadmap automatically
2. Use the loaded context directly - DO NOT read memory files again
3. Only read files explicitly when they need to be MODIFIED (not just referenced)
4. Feature-specific artifacts (plan.md, spec.md, contracts/) require explicit reads
```

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (constitution created or updated)

Display the following at the end of your output:

```markdown
---

## Next Steps

**Constitution updated successfully!**

**Recommended**: Run `/doit.scaffoldit` to generate project structure based on the tech stack in your constitution.

**Alternative**: Run `/doit.specit [feature description]` to create a feature specification for your first feature.
```

### On Error (validation failed)

If the constitution could not be validated:

```markdown
---

## Next Steps

**Issue**: Constitution validation failed.

**Recommended**: Review the errors above and correct the constitution content.
```
