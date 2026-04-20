---
name: doit.scaffoldit
description: Generate project folder structure and starter files based on tech stack from constitution or user input.
when_to_use: Use when the user wants to scaffold a new project directory structure based on the tech stack declared in the
  constitution.
allowed-tools: Read Write Edit Glob Grep Bash
argument-hint: '[tech stack | framework override]'
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

- Reference constitution principles when making decisions (already in context)
- Consider roadmap priorities (already in context)
- Use tech stack information from constitution/tech-stack (already in context)
- Identify connections to related specifications

**DO NOT read these files again** (already in context above):

- `.doit/memory/constitution.md` - principles and tech stack are in context
- `.doit/memory/tech-stack.md` - tech decisions are in context
- `.doit/memory/roadmap.md` - priorities are in context

**Legitimate explicit reads** (NOT in context show):

- `README.md` - for project description (if no constitution)
- `package.json` or `pyproject.toml` - for existing project metadata
- Existing project files for structure analysis

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

You are generating a project folder structure based on the tech stack defined in the constitution or provided by the user. This command creates directories, config files, and starter templates appropriate for the chosen technology.

Follow this execution flow:

### 1. Extract Tech Stack from Context

Tech stack information is already loaded from `doit context show`. Extract from context:

- **Tech Stack**: Languages, Frameworks, Libraries
- **Infrastructure**: Hosting platform, Cloud provider, Database
- **Deployment**: CI/CD pipeline, Strategy, Environments

If constitution/tech-stack context is not available or has incomplete tech stack info, proceed to step 2.

### 2. Tech Stack Clarification

If tech stack is not fully defined, prompt the user:

- "What is your primary programming language?" (e.g., Python, TypeScript, Go, Java, C#)
- "What framework are you using?" (e.g., React, FastAPI, .NET, Spring Boot)
- "Is this a frontend, backend, or full-stack project?"
- "Do you need containerization (Docker)?"

### 3. Structure Generation

Based on detected/provided tech stack, generate the appropriate folder structure:

#### React/TypeScript Frontend

```text
src/
├── components/
│   └── .gitkeep
├── hooks/
│   └── .gitkeep
├── pages/
│   └── .gitkeep
├── services/
│   └── .gitkeep
├── styles/
│   └── .gitkeep
├── types/
│   └── .gitkeep
├── utils/
│   └── .gitkeep
└── App.tsx
public/
└── index.html
tests/
└── .gitkeep
```

#### .NET/C# Backend

```text
src/
├── Controllers/
│   └── .gitkeep
├── Models/
│   └── .gitkeep
├── Services/
│   └── .gitkeep
├── Data/
│   └── .gitkeep
├── DTOs/
│   └── .gitkeep
└── Program.cs
tests/
├── Unit/
│   └── .gitkeep
└── Integration/
    └── .gitkeep
```

#### Node.js/Express Backend

```text
src/
├── controllers/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── services/
│   └── .gitkeep
├── routes/
│   └── .gitkeep
├── middleware/
│   └── .gitkeep
├── utils/
│   └── .gitkeep
└── app.js
tests/
└── .gitkeep
```

#### Python/FastAPI Backend

```text
src/
├── api/
│   ├── routes/
│   │   └── .gitkeep
│   └── deps.py
├── models/
│   └── .gitkeep
├── schemas/
│   └── .gitkeep
├── services/
│   └── .gitkeep
├── core/
│   ├── config.py
│   └── security.py
└── main.py
tests/
├── unit/
│   └── .gitkeep
└── integration/
    └── .gitkeep
```

#### Go Backend

```text
cmd/
└── main.go
internal/
├── handlers/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── services/
│   └── .gitkeep
├── repository/
│   └── .gitkeep
└── middleware/
    └── .gitkeep
pkg/
└── .gitkeep
tests/
└── .gitkeep
```

#### Vue.js Frontend

```text
src/
├── components/
│   └── .gitkeep
├── views/
│   └── .gitkeep
├── composables/
│   └── .gitkeep
├── stores/
│   └── .gitkeep
├── services/
│   └── .gitkeep
├── assets/
│   └── .gitkeep
├── App.vue
└── main.ts
public/
└── index.html
tests/
└── .gitkeep
```

#### Angular Frontend

```text
src/
├── app/
│   ├── components/
│   │   └── .gitkeep
│   ├── services/
│   │   └── .gitkeep
│   ├── models/
│   │   └── .gitkeep
│   ├── guards/
│   │   └── .gitkeep
│   └── app.module.ts
├── assets/
│   └── .gitkeep
└── environments/
    └── .gitkeep
tests/
└── .gitkeep
```

#### Java/Spring Boot Backend

```text
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── [package]/
│   │           ├── controller/
│   │           │   └── .gitkeep
│   │           ├── service/
│   │           │   └── .gitkeep
│   │           ├── repository/
│   │           │   └── .gitkeep
│   │           ├── model/
│   │           │   └── .gitkeep
│   │           └── Application.java
│   └── resources/
│       └── application.yml
└── test/
    └── java/
        └── .gitkeep
```

### 4. Config File Generation

Generate appropriate config files based on tech stack:

| Tech Stack | Config Files |
|------------|--------------|
| React/TypeScript | `tsconfig.json`, `package.json`, `vite.config.ts` |
| .NET | `*.csproj`, `appsettings.json`, `appsettings.Development.json` |
| Node.js | `package.json`, `tsconfig.json` (if TS), `.eslintrc.js` |
| Python | `pyproject.toml`, `requirements.txt`, `.python-version` |
| Go | `go.mod`, `go.sum` |
| Vue | `package.json`, `vite.config.ts`, `tsconfig.json` |
| Angular | `angular.json`, `package.json`, `tsconfig.json` |
| Java | `pom.xml` or `build.gradle`, `application.yml` |

### 5. Starter Files Generation

Create minimal starter files:

- `README.md` with project name, description, and setup instructions
- `.editorconfig` for consistent coding styles
- Appropriate `.gitkeep` files in empty directories

### 6. Docker Support

If containerization is required (from constitution or user input):

- Create `Dockerfile` appropriate for the tech stack
- Create `docker-compose.yml` for local development
- Create `.dockerignore`

### 7. .gitignore Generation

Generate comprehensive `.gitignore` based on tech stack:

- Language-specific ignores (node_modules, __pycache__, bin/obj, etc.)
- IDE ignores (.idea, .vscode settings, etc.)
- Environment files (.env, .env.local)
- Build artifacts (dist, build, target)

### 8. Doit Commands Generation

Generate the doit command suite for the new project:

1. Create `.claude/commands/` directory in the target project
2. Copy all 11 doit command templates from `.doit/templates/commands/`:
   - `doit.checkin.md` - Feature completion and PR creation
   - `doit.constitution.md` - Project constitution management
   - `doit.documentit.md` - Documentation organization and indexing
   - `doit.implementit.md` - Task implementation execution
   - `doit.planit.md` - Implementation planning
   - `doit.reviewit.md` - Code review workflow
   - `doit.roadmapit.md` - Project roadmap management
   - `doit.scaffoldit.md` - Project scaffolding
   - `doit.specit.md` - Feature specification
   - `doit.taskit.md` - Task generation
   - `doit.testit.md` - Test execution

This enables new projects to immediately use the full doit workflow without manual setup.

### 9. Multi-Stack Support

For full-stack projects (frontend + backend), create:

```text
frontend/
└── [frontend structure]
backend/
└── [backend structure]
shared/
└── types/  # Shared type definitions
docker-compose.yml  # Combined services
```

### 10. Existing Project Analysis (FR-064, FR-065)

If the project already has files:

1. Scan existing directory structure
2. Identify current tech stack from config files
3. Generate analysis report showing:
   - Detected technologies
   - Current structure vs. recommended structure
   - Missing recommended directories
   - Suggested improvements

### 11. Tech Stack Documentation (FR-015 to FR-018)

After tech stack is determined (from constitution or user input), generate `.doit/memory/tech-stack.md`:

1. Read `.doit/templates/tech-stack-template.md` for structure
2. Populate with captured tech stack information:
   - **Languages**: Primary language and version
   - **Frameworks**: Main framework(s) with versions
   - **Key Libraries**: Important dependencies with rationale
   - **Infrastructure**: Hosting, cloud provider, database choices
   - **Architecture Decisions**: Key decisions made during scaffolding

3. If `tech-stack.md` already exists:
   - Preserve content in "Custom Notes" section
   - Update auto-generated sections between markers

4. If `constitution.md` exists with tech info:
   - Include relevant details from constitution
   - Cross-reference but don't duplicate

Example output structure:

```markdown
# Tech Stack

**Generated**: 2026-01-10
**Last Updated**: 2026-01-10

### 12. Post-Scaffold Summary

Once scaffolding finishes, surface the next steps clearly. The freshly
written `.doit/memory/constitution.md` carries a **YAML frontmatter stub
full of `[PROJECT_…]` placeholders**; those MUST be filled in before the
project passes `doit verify-memory`. Direct the user to run
`/doit.constitution` next — that skill prompts for every frontmatter field
(`id`, `name`, `kind`, `phase`, `icon`, `tagline`, `competitor`,
`dependencies`, `consumers`) as well as the principles/governance body.

Optional follow-ups to mention:

- `doit verify-memory` — one-shot contract check; expected to fail until
  `/doit.constitution` runs.
- `/doit.roadmapit` — populate the roadmap (includes the `## Open
  Questions` table that downstream docs generators consume).
- `doit memory schema` — print the frontmatter JSON Schema for reference.

## Additional Reference

For the full set of sections that follow this playbook, see [reference.md](reference.md). Claude loads it on demand when the content is needed.
