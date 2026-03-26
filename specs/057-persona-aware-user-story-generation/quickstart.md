# Quickstart: Persona-Aware User Story Generation

## Overview

This feature enhances `/doit.specit` to automatically map generated user stories to personas using P-NNN traceability IDs. All changes are template-level — no Python code modifications.

## Prerequisites

- Spec 056 (persona-context-injection) must be complete and merged
- Personas must exist in either `.doit/memory/personas.md` (project-level) or `specs/{feature}/personas.md` (feature-level)

## What Changes

### 3 Source Template Files

1. **`src/doit_cli/templates/commands/doit.specit.md`** — Add persona matching rules, traceability table update instructions, and coverage report output
2. **`src/doit_cli/templates/spec-template.md`** — Add `| Persona: P-NNN` to user story header format
3. **`src/doit_cli/templates/user-stories-template.md`** — Add persona ID to story format

### 2 Synced Files (via `doit sync-prompts`)

- `.claude/commands/doit.specit.md`
- `.github/prompts/doit.specit.prompt.md`

## How It Works

1. `/doit.specit` loads persona context (already done by spec 056)
2. When generating each user story, the AI applies matching rules to find the best persona
3. The persona ID is added to the story header: `### User Story N - Title (Priority: PN) | Persona: P-NNN`
4. After all stories, the traceability table in `personas.md` is updated
5. A coverage report is displayed showing story counts per persona

## Verification

After implementation, verify with:

```bash
# Run specit on a feature with personas defined
# Check that each story header contains | Persona: P-NNN
# Check that personas.md traceability table is updated
# Check that coverage report is displayed

# Verify backward compatibility — run specit without personas
# Should generate stories without persona tags, no errors
```

## Matching Rules (Priority Order)

1. Direct goal match → High confidence
2. Pain point match → High confidence
3. Usage context match → Medium confidence
4. Role/archetype match → Medium confidence
5. Multi-persona → List all relevant IDs
6. No match → Generate without tag, flag in coverage report
