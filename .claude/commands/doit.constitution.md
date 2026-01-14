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

## Outline

You are updating the project constitution at `.doit/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

### Step 0: Project Scanning with Dotfile Exclusion

**CRITICAL**: When scanning the project for context inference, you MUST exclude dotfiles and dotfolders.

**Exclusion Rules**:

1. **Directories to EXCLUDE** (any path starting with `.`):
   - `.git` - Git version control
   - `.doit` - Do-It configuration (EXCEPTION: `.doit/memory/constitution.md` is the target file)
   - `.vscode` - VS Code settings
   - `.idea` - JetBrains IDE settings
   - `.env` - Environment variable files
   - `.config` - Application config
   - `.cache` - Cache directories
   - `.npm`, `.yarn`, `.pnpm` - Package manager caches
   - Any other directory starting with `.`

2. **Files to EXCLUDE**:
   - `.gitignore`, `.dockerignore`, `.eslintignore` - Ignore files
   - `.env`, `.env.local`, `.env.production` - Environment files
   - `.DS_Store`, `.Thumbs.db` - System files
   - Any file starting with `.`

3. **Additional Exclusions** (non-dotfiles but irrelevant):
   - `node_modules/` - Node.js dependencies
   - `__pycache__/` - Python bytecode
   - `target/`, `build/`, `dist/` - Build outputs
   - `vendor/` - Vendored dependencies

4. **EXCEPTION**: Always read `.doit/memory/constitution.md` as the target file for updates

**Rationale**: Dotfiles contain configuration metadata, not project source code. Including them leads to incorrect tech stack inference.

### Step 0.5: Greenfield Project Detection

After applying dotfile exclusion, detect if the project is greenfield (empty or minimal).

**Source File Extensions** (files that indicate existing project code):

```text
.py, .js, .ts, .jsx, .tsx, .java, .go, .rs, .rb, .php, .cs, .cpp, .c, .h, .swift, .kt, .scala, .clj, .ex, .exs
```

**Files NOT counted as source code**:

- `README.md`, `LICENSE`, `CHANGELOG.md` - Documentation
- `*.json`, `*.yaml`, `*.yml` - Configuration files
- `*.md` - Markdown documentation
- `Makefile`, `Dockerfile` - Build files

**Detection Logic**:

1. Scan project directories (excluding dotfolders and node_modules)
2. Count files matching source file extensions
3. If source file count == 0: **Project is GREENFIELD**
4. If source file count > 0: **Project has EXISTING CODE** → proceed to Step 1

**If Greenfield Detected**:

Display: "Detected greenfield project - entering interactive mode"

Then proceed to **Step 0.75: Interactive Constitution Creation** (below).

**If Existing Code Detected**:

Proceed to **Step 1: Load existing constitution template** and use inference mode.

### Step 0.75: Interactive Constitution Creation (Greenfield Mode Only)

When a greenfield project is detected, guide the user through constitution creation with the following questions.

**Argument Pre-fill Logic**:

Before asking questions, parse any arguments provided with the command. Match keywords to categories and skip questions where answers are provided.

| Category  | Example Keywords                                                              |
| --------- | ----------------------------------------------------------------------------- |
| Language  | Python, JavaScript, TypeScript, Go, Rust, Java, C#, Ruby, PHP, Swift, Kotlin  |
| Framework | FastAPI, Django, Flask, React, Vue, Angular, Express, Spring, Rails, Laravel  |
| Database  | PostgreSQL, MySQL, MongoDB, Redis, SQLite, DynamoDB, Firestore, none          |
| Hosting   | AWS, GCP, Azure, Vercel, Netlify, Heroku, DigitalOcean, self-hosted           |
| CI/CD     | GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis CI                       |

Example: `/doit.constitution Python FastAPI PostgreSQL` → Skip Q2 (language), Q3 (framework), Q6 (database)

**Interactive Question Sequence**:

#### Q1: Project Purpose (MANDATORY)

> "What is the purpose of this project? Describe what it will do and what problem it solves."

Maps to: `[PROJECT_NAME]`, `[PROJECT_PURPOSE]`, `[SUCCESS_CRITERIA]`

#### Q2: Primary Programming Language (MANDATORY)

> "What programming language will this project primarily use?"
>
> Examples: Python 3.11+, TypeScript, Go, Rust, Java

Maps to: `[PRIMARY_LANGUAGE]`

#### Q3: Frameworks (OPTIONAL - press Enter to skip)

> "What frameworks will you use? (Enter to skip if none or undecided)"
>
> Examples: FastAPI, React, Django, Express, Spring Boot

Maps to: `[FRAMEWORKS]`

#### Q4: Key Libraries (OPTIONAL - press Enter to skip)

> "What key libraries or packages are essential? (Enter to skip)"
>
> Examples: Pydantic, SQLAlchemy, Axios, Lodash

Maps to: `[KEY_LIBRARIES]`

#### Q5: Hosting Platform (OPTIONAL - press Enter to skip)

> "Where will this project be hosted? (Enter to skip)"
>
> Examples: AWS ECS, Google Cloud Run, Vercel, Heroku, self-hosted

Maps to: `[HOSTING_PLATFORM]`, `[CLOUD_PROVIDER]`

#### Q6: Database (OPTIONAL - type "none" if no database needed)

> "What database will you use? Type 'none' if no database is needed. (Enter to skip)"
>
> Examples: PostgreSQL, MongoDB, Redis, SQLite, none

Maps to: `[DATABASE]`

#### Q7: CI/CD Pipeline (OPTIONAL - press Enter to skip)

> "What CI/CD system will you use? (Enter to skip)"
>
> Examples: GitHub Actions, GitLab CI, Jenkins

Maps to: `[CICD_PIPELINE]`

**After Interactive Collection**:

1. Set `[RATIFICATION_DATE]` to today's date (YYYY-MM-DD format)
2. Set `[CONSTITUTION_VERSION]` to `1.0.0`
3. Set `[LAST_AMENDED_DATE]` to today's date
4. For any skipped optional questions, use reasonable defaults or mark as "TBD"
5. Proceed to **Step 5** to draft the constitution with collected values
6. Skip Steps 1-4 (those are for inference mode)

---

1. Load the existing constitution template at `.doit/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. **Section-by-Section Update Mode** (FR-011):
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

   **Purpose & Goals (FR-004):**
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

   **Deployment (FR-009):**
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

## Constitution Reading Utility (FR-013)

Other commands can read and utilize the constitution by:

1. **Loading the constitution**: Read `.doit/memory/constitution.md`
2. **Extracting tech stack**: Parse the Tech Stack section for language, framework, and library information
3. **Extracting infrastructure**: Parse the Infrastructure section for hosting and cloud provider details
4. **Extracting deployment**: Parse the Deployment section for CI/CD and environment configuration
5. **Checking principles**: Parse Core Principles for project constraints and requirements

**Usage in other commands**:

```text
# At the start of any command that needs project context:
1. Check if `.doit/memory/constitution.md` exists
2. If exists, read and parse relevant sections
3. Use extracted values to inform command behavior (e.g., scaffold uses tech stack, plan uses constraints)
4. If constitution is incomplete or missing, prompt user or proceed with defaults
```
