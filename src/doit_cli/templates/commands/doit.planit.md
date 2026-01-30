---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
handoffs: 
  - label: Create Tasks
    agent: doit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: doit.checklist
    prompt: Create a checklist for the following domain...
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

- Reference constitution principles when making decisions
- Consider roadmap priorities
- Identify connections to related specifications
- Use tech stack information (already included in constitution/tech-stack context)
- Review related_specs for integration points with other features

**DO NOT read these files again** (already in context above):

- `.doit/memory/constitution.md` - principles are in context
- `.doit/memory/tech-stack.md` - tech decisions are in context
- `.doit/memory/roadmap.md` - priorities are in context
- Current feature spec - available as current_spec in context

**Legitimate explicit reads** (NOT in context show):

- `specs/{feature}/research.md` - if research phase complete
- `specs/{feature}/data-model.md` - if already generated
- `specs/{feature}/contracts/*.yaml` - API contract files

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

1. **Setup**: Run `.doit/scripts/bash/setup-plan.sh --json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Load IMPL_PLAN template (already copied). Feature spec and constitution are already available from `doit context show` above.

3. **Extract Tech Stack from loaded context**:
   - Tech stack is already loaded in context (from tech-stack.md or constitution.md)
   - Extract: PRIMARY_LANGUAGE, FRAMEWORKS, KEY_LIBRARIES
   - Extract: HOSTING_PLATFORM, CLOUD_PROVIDER, DATABASE
   - Extract: CICD_PIPELINE, DEPLOYMENT_STRATEGY
   - Store these values for architecture alignment validation

4. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context using constitution tech stack as baseline
   - Flag any tech choices that deviate from constitution (require justification)
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified or tech stack misalignment)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

5. **Generate Mermaid Visualizations** (FR-004, FR-005, FR-006, FR-007):

   After filling the plan content, generate visual diagrams:

   a. **Architecture Overview**:
      - Parse Technical Context for: Language, Dependencies, Storage, Target Platform
      - Identify architectural layers from Project Type:
        - **single**: Presentation → Service → Data
        - **web**: Frontend → API → Services → Database
        - **mobile**: Mobile App → API → Services → Database
      - Generate flowchart with subgraphs for each layer
      - Replace content in `<!-- BEGIN:AUTO-GENERATED section="architecture" -->` markers

      ```mermaid
      flowchart TD
          subgraph "Presentation"
              UI[UI/CLI Layer]
          end
          subgraph "Application"
              API[API/Routes]
              SVC[Services]
          end
          subgraph "Data"
              DB[(Database)]
          end
          UI --> API --> SVC --> DB
      ```

   b. **Component Dependencies**:
      - Check if multiple services/components are defined in Project Structure
      - **IF multiple services defined**:
        - Parse service names from structure
        - Generate dependency flowchart showing relationships
        - Replace content in `<!-- BEGIN:AUTO-GENERATED section="component-dependencies" -->` markers
      - **IF single service only**:
        - **REMOVE the entire Component Dependencies section**
        - Do NOT leave empty placeholder

   c. **Data Model ER Diagram**:
      - When generating data-model.md, add ER diagram at the top
      - Parse entity definitions from the file
      - Generate erDiagram showing all entities and relationships
      - Insert in `<!-- BEGIN:AUTO-GENERATED section="er-diagram" -->` markers

      ```mermaid
      erDiagram
          ENTITY1 ||--o{ ENTITY2 : "relationship"
          ENTITY1 {
              uuid id PK
              string name
          }
      ```

   d. **State Machine Detection**:
      - Scan entities for fields named: `status`, `state`, `stage`, `phase`
      - For each entity with state field:
        - Parse possible state values from field type or comments
        - Generate stateDiagram-v2 showing transitions
        - Add after entity definition in data-model.md

      ```mermaid
      stateDiagram-v2
          [*] --> Initial
          Initial --> Active : activate
          Active --> Complete : finish
          Complete --> [*]
      ```

   e. **Diagram Validation**:
      - Verify mermaid syntax is valid
      - Check node count does not exceed limits (20 for flowchart, 10 for ER)
      - If exceeding limits, split into subgraphs by domain/layer

6. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `.doit/scripts/bash/update-agent-context.sh claude`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (plan and artifacts created)

Display the following at the end of your output:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────┐
│  Workflow Progress                                          │
│  ● specit → ● planit → ○ taskit → ○ implementit → ○ checkin │
└─────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.taskit` to create implementation tasks from this plan.
```

### On Success with Existing Tasks

If `tasks.md` already exists in the specs directory:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────┐
│  Workflow Progress                                          │
│  ● specit → ● planit → ● taskit → ○ implementit → ○ checkin │
└─────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.implementit` to begin executing the existing tasks.

**Alternative**: Run `/doit.taskit` to regenerate tasks based on the updated plan.
```

### On Error (missing spec.md)

If the command fails because spec.md is not found:

```markdown
---

## Next Steps

**Issue**: No feature specification found. The planit command requires spec.md to exist.

**Recommended**: Run `/doit.specit [feature description]` to create a feature specification first.
```

### On Error (other issues)

If the command fails for another reason:

```markdown
---

## Next Steps

**Issue**: [Brief description of what went wrong]

**Recommended**: [Specific recovery action based on the error]
```
