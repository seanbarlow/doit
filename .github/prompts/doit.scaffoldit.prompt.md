# Doit Scaffoldit

Generate project folder structure and starter files based on tech stack from constitution or user input.

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

You are generating a project folder structure based on the tech stack defined in the constitution or provided by the user. This command creates directories, config files, and starter templates appropriate for the chosen technology.

Follow this execution flow:

### 1. Load Constitution

Read `.doit/memory/constitution.md` and extract:

- **Tech Stack**: Languages, Frameworks, Libraries
- **Infrastructure**: Hosting platform, Cloud provider, Database
- **Deployment**: CI/CD pipeline, Strategy, Environments

If constitution doesn't exist or has incomplete tech stack info, proceed to step 2.

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

## Languages

| Language | Version | Purpose |
| -------- | ------- | ------- |
| TypeScript | 5.0+ | Primary |

## Frameworks

| Framework | Version | Purpose |
| --------- | ------- | ------- |
| React | 18.x | Frontend UI |
| FastAPI | 0.100+ | Backend API |

## Key Libraries

| Library | Version | Purpose | Why Chosen |
| ------- | ------- | ------- | ---------- |
| Tailwind | 3.x | Styling | Rapid prototyping |

<!-- BEGIN:AUTO-GENERATED section="scaffold-captured" -->
Captured during scaffold on 2026-01-10
<!-- END:AUTO-GENERATED -->

## Custom Notes

[User additions preserved here]
```

### 12. Output Summary

After scaffolding, provide:

- List of created directories and files
- Confirmation that doit commands were generated (11 files in `.claude/commands/`)
- Confirmation that tech-stack.md was created in `.doit/memory/`
- Next steps for the user
- Suggested commands to run (e.g., `npm install`, `pip install -r requirements.txt`)
- Reminder to run `/doit.specit` to create feature specifications
- Reminder to run `/doit.documentit` to organize documentation

## Validation

Before creating files:

- Confirm tech stack selection with user
- Check for existing files that would be overwritten
- Prompt for confirmation before creating structure

## Notes

- Always create `.gitkeep` files in empty directories
- Use appropriate naming conventions for the tech stack (camelCase, snake_case, PascalCase)
- Include comments in generated config files explaining key settings
- Respect existing project structure when adding new directories

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (project scaffolded)

Display the following at the end of your output:

```markdown
---

## Next Steps

**Project structure created!**

**Recommended**: Run `/doit.specit [feature description]` to create your first feature specification.

**Alternative**: Run `/doit.documentit organize` to organize any existing documentation.
```

### On Existing Project (structure already exists)

If the project already has a structure:

```markdown
---

## Next Steps

**Project structure analyzed!**

**Recommended**: Run `/doit.specit [feature description]` to start developing a new feature.

**Alternative**: Run `/doit.documentit audit` to check documentation health.
```
