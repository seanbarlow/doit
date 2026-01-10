---
description: Generate project folder structure and starter files based on tech stack from constitution or user input.
handoffs:
  - label: Create Specification
    agent: doit.doit
    prompt: Create a feature specification for this scaffolded project. I want to build...
  - label: Update Constitution
    agent: doit.constitution
    prompt: Update the project constitution with additional details...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are generating a project folder structure based on the tech stack defined in the constitution or provided by the user. This command creates directories, config files, and starter templates appropriate for the chosen technology.

Follow this execution flow:

### 1. Load Constitution (FR-056)

Read `.doit/memory/constitution.md` and extract:

- **Tech Stack**: Languages, Frameworks, Libraries
- **Infrastructure**: Hosting platform, Cloud provider, Database
- **Deployment**: CI/CD pipeline, Strategy, Environments

If constitution doesn't exist or has incomplete tech stack info, proceed to step 2.

### 2. Tech Stack Clarification (FR-057)

If tech stack is not fully defined, prompt the user:

- "What is your primary programming language?" (e.g., Python, TypeScript, Go, Java, C#)
- "What framework are you using?" (e.g., React, FastAPI, .NET, Spring Boot)
- "Is this a frontend, backend, or full-stack project?"
- "Do you need containerization (Docker)?"

### 3. Structure Generation

Based on detected/provided tech stack, generate the appropriate folder structure:

#### React/TypeScript Frontend (FR-055)

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

#### .NET/C# Backend (FR-056)

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

#### Node.js/Express Backend (FR-057)

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

#### Python/FastAPI Backend (FR-058)

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

#### Go Backend (FR-059)

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

#### Vue.js Frontend (FR-060)

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

#### Angular Frontend (FR-061)

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

#### Java/Spring Boot Backend (FR-062)

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

### 4. Config File Generation (FR-059)

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

### 5. Starter Files Generation (FR-060)

Create minimal starter files:

- `README.md` with project name, description, and setup instructions
- `.editorconfig` for consistent coding styles
- Appropriate `.gitkeep` files in empty directories

### 6. Docker Support (FR-061)

If containerization is required (from constitution or user input):

- Create `Dockerfile` appropriate for the tech stack
- Create `docker-compose.yml` for local development
- Create `.dockerignore`

### 7. .gitignore Generation (FR-062)

Generate comprehensive `.gitignore` based on tech stack:

- Language-specific ignores (node_modules, __pycache__, bin/obj, etc.)
- IDE ignores (.idea, .vscode settings, etc.)
- Environment files (.env, .env.local)
- Build artifacts (dist, build, target)

### 8. Doit Commands Generation (FR-066)

Generate the doit command suite for the new project:

1. Create `.claude/commands/` directory in the target project
2. Copy all 9 doit command templates from `.doit/templates/commands/`:
   - `doit.checkin.md` - Feature completion and PR creation
   - `doit.constitution.md` - Project constitution management
   - `doit.implement.md` - Task implementation execution
   - `doit.plan.md` - Implementation planning
   - `doit.review.md` - Code review workflow
   - `doit.scaffold.md` - Project scaffolding
   - `doit.specify.md` - Feature specification
   - `doit.tasks.md` - Task generation
   - `doit.test.md` - Test execution

This enables new projects to immediately use the full doit workflow without manual setup.

### 9. Multi-Stack Support (FR-063)

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

### 11. Output Summary

After scaffolding, provide:

- List of created directories and files
- Confirmation that doit commands were generated (9 files in `.claude/commands/`)
- Next steps for the user
- Suggested commands to run (e.g., `npm install`, `pip install -r requirements.txt`)
- Reminder to run `/doit.specit` to create feature specifications

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
