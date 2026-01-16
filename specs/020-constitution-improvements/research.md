# Research: Constitution Command Improvements

**Feature**: 020-constitution-improvements
**Date**: 2026-01-13

## Overview

This document captures research findings for implementing dotfile exclusion, greenfield detection, and interactive questioning in the `/doit.constitution` command.

## Research Topics

### 1. Dotfile Exclusion Patterns

**Decision**: Exclude all paths starting with `.` from project scanning

**Rationale**:

- Dotfiles/dotfolders are conventionally used for configuration, caches, and IDE settings
- Including them leads to incorrect tech stack inference (e.g., `.vscode/settings.json` suggesting VS Code is part of the project)
- Standard tools (find, glob, ls) commonly exclude dotfiles by default

**Common Dotfolders to Exclude**:

| Directory | Purpose |
| --------- | ------- |
| `.git` | Git version control |
| `.doit` | DoIt configuration and memory |
| `.vscode` | VS Code settings |
| `.idea` | JetBrains IDE settings |
| `.env` | Environment variables |
| `.config` | Application config |
| `.cache` | Cache files |
| `.npm`, `.yarn` | Package manager caches |
| `node_modules` | Note: Not a dotfolder, but should also be excluded |

**Alternatives Considered**:

- Explicit allowlist of folders to scan → Rejected: Too restrictive, requires maintenance
- Configurable exclusion list → Rejected: Adds complexity, dotfile convention is universal

### 2. Greenfield Detection Criteria

**Decision**: Project is greenfield when zero source files exist outside dotfolders

**Rationale**:

- Simple binary check: has code or doesn't
- Common source extensions cover 95%+ of projects
- Non-source files (README, LICENSE) shouldn't trigger inference mode

**Source File Extensions**:

```text
.py, .js, .ts, .jsx, .tsx, .java, .go, .rs, .rb, .php, .cs, .cpp, .c, .h, .swift, .kt, .scala, .clj, .ex, .exs
```

**Files NOT Counted as Source**:

- `README.md`, `LICENSE`, `CHANGELOG.md`
- `*.json`, `*.yaml`, `*.yml` (config files)
- `*.md` (documentation)
- `Makefile`, `Dockerfile` (build files)

**Alternatives Considered**:

- Check for package manager files (package.json, requirements.txt) → Rejected: Some projects have these before any code
- Threshold-based (< 5 files = greenfield) → Rejected: Arbitrary, complex edge cases

### 3. Interactive Questioning Flow

**Decision**: Sequential prompts using AI agent's native conversation capabilities

**Rationale**:

- No custom UI needed - leverages existing chat interface
- Questions map directly to constitution template placeholders
- Arguments can pre-fill to skip questions

**Question Flow Design**:

```text
1. Purpose & Goals (mandatory)
   → Maps to: [PROJECT_PURPOSE], [SUCCESS_CRITERIA]

2. Primary Language (mandatory)
   → Maps to: [PRIMARY_LANGUAGE]

3. Frameworks (optional - Enter to skip)
   → Maps to: [FRAMEWORKS]

4. Key Libraries (optional - Enter to skip)
   → Maps to: [KEY_LIBRARIES]

5. Hosting Platform (optional)
   → Maps to: [HOSTING_PLATFORM]

6. Database (optional - includes "none")
   → Maps to: [DATABASE]

7. CI/CD (optional)
   → Maps to: [CICD_PIPELINE]
```

**Alternatives Considered**:

- Single form-like prompt → Rejected: Too overwhelming, hard to validate
- Wizard-style with back/forward → Rejected: Adds complexity, chat is linear anyway

### 4. Argument Pre-fill Parsing

**Decision**: Parse space-separated arguments and match to known categories

**Rationale**:

- Common pattern: `/doit.constitution Python FastAPI PostgreSQL`
- Keywords can be matched to question categories
- Unknown arguments treated as principles/description

**Keyword Categories**:

| Category | Example Keywords |
| -------- | ---------------- |
| Language | Python, JavaScript, TypeScript, Go, Rust, Java |
| Framework | FastAPI, Django, React, Vue, Express, Spring |
| Database | PostgreSQL, MySQL, MongoDB, Redis, SQLite, DynamoDB |
| Hosting | AWS, GCP, Azure, Vercel, Netlify, Heroku |
| CI/CD | GitHub Actions, GitLab CI, Jenkins, CircleCI |

## Implementation Recommendations

1. **Dotfile Exclusion**: Add explicit instruction in command template to filter paths starting with `.`

2. **Greenfield Detection**: Add step after scanning to count source files and branch to interactive mode if zero

3. **Interactive Mode**: Use structured prompts with clear skip instructions for optional fields

4. **Pre-fill Logic**: Parse arguments before starting questions, skip answered fields

## References

- Unix dotfile convention: Hidden files/directories
- Common IDE folder patterns
- DoIt constitution template structure
