---
mode: agent
description: Generate project folder structure and starter files based on tech stack
---

# Doit Scaffoldit - Project Scaffolder

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

Based on detected/provided tech stack, generate the appropriate folder structure.

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

### 4. Config File Generation (FR-059)

Generate appropriate config files based on tech stack:

| Tech Stack | Config Files |
|------------|--------------|
| React/TypeScript | `tsconfig.json`, `package.json`, `vite.config.ts` |
| .NET | `*.csproj`, `appsettings.json`, `appsettings.Development.json` |
| Node.js | `package.json`, `tsconfig.json` (if TS), `.eslintrc.js` |
| Python | `pyproject.toml`, `requirements.txt`, `.python-version` |
| Go | `go.mod`, `go.sum` |

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

1. Create `.claude/commands/` directory OR `.github/prompts/` directory based on detected agent
2. Copy all 11 doit command templates

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

### 11. Tech Stack Documentation (FR-015 to FR-018)

After tech stack is determined, generate `.doit/memory/tech-stack.md`:

1. Read `.doit/templates/tech-stack-template.md` for structure
2. Populate with captured tech stack information
3. If `tech-stack.md` already exists, preserve "Custom Notes" section

### 12. Output Summary

After scaffolding, provide:

- List of created directories and files
- Confirmation that doit commands were generated
- Confirmation that tech-stack.md was created in `.doit/memory/`
- Next steps for the user
- Suggested commands to run (e.g., `npm install`, `pip install -r requirements.txt`)
- Reminder to run `#doit-specit` to create feature specifications
- Reminder to run `#doit-documentit` to organize documentation

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
