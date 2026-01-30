# Personas: {FEATURE_NAME}

**Feature Branch**: `{BRANCH_NAME}`
**Created**: {DATE}
**Derived From**: `/doit.researchit` Q&A session

---

## Persona Summary

| ID | Name | Role | Archetype | Primary Goal |
|----|------|------|-----------|--------------|
| P-001 | {Name} | {Role} | {Archetype} | {Primary Goal} |
| P-002 | {Name} | {Role} | {Archetype} | {Primary Goal} |

---

## Detailed Profiles

### Persona: P-001

#### Identity

- **Name**: {Persona Name}
- **Role**: {Job Title / Role}
- **Archetype**: {Power User | Casual User | Administrator | Approver | Observer}

#### Demographics

- **Experience Level**: {Junior | Mid | Senior | Executive}
- **Team Size**: {Solo | Small Team | Large Team | Enterprise}
- **Domain Expertise**: {Description}

#### Goals

**Primary Goal**: {Main objective}

**Secondary Goals**:
- {Goal 1}
- {Goal 2}

#### Pain Points (prioritized)

1. {Most critical pain point}
2. {Second pain point}
3. {Third pain point}

#### Behavioral Patterns

- **Technology Proficiency**: {Low | Medium | High}
- **Work Style**: {Description}
- **Decision Making**: {Description}

#### Success Criteria

{What success looks like for this persona}

#### Usage Context

{When and where they encounter this problem}

#### Relationships

| Related Persona | Relationship Type | Context |
|-----------------|-------------------|---------|
| P-002 | {relationship} | {context} |

#### Conflicts & Tensions

{Any conflicting goals with other personas}

---

### Persona: P-002

#### Identity

- **Name**: {Persona Name}
- **Role**: {Job Title / Role}
- **Archetype**: {Power User | Casual User | Administrator | Approver | Observer}

#### Demographics

- **Experience Level**: {Junior | Mid | Senior | Executive}
- **Team Size**: {Solo | Small Team | Large Team | Enterprise}
- **Domain Expertise**: {Description}

#### Goals

**Primary Goal**: {Main objective}

**Secondary Goals**:
- {Goal 1}
- {Goal 2}

#### Pain Points (prioritized)

1. {Most critical pain point}
2. {Second pain point}
3. {Third pain point}

#### Behavioral Patterns

- **Technology Proficiency**: {Low | Medium | High}
- **Work Style**: {Description}
- **Decision Making**: {Description}

#### Success Criteria

{What success looks like for this persona}

#### Usage Context

{When and where they encounter this problem}

#### Relationships

| Related Persona | Relationship Type | Context |
|-----------------|-------------------|---------|
| P-001 | {relationship} | {context} |

#### Conflicts & Tensions

{Any conflicting goals with other personas}

---

## Relationship Map

```mermaid
flowchart LR
    P001[P-001: {Name}]
    P002[P-002: {Name}]

    P001 -->|{relationship}| P002
```

> This diagram shows how personas relate to each other. Arrows indicate the direction of the relationship (e.g., manages, approves).

---

## Conflicts & Tensions Summary

| Personas | Conflict | Resolution Strategy |
|----------|----------|---------------------|
| P-001 vs P-002 | {Brief conflict description} | {How to resolve or balance} |

> Document any competing goals between personas that may require tradeoffs during feature design.

---

## Traceability

### Persona Coverage

| Persona | User Stories Addressing | Primary Focus |
|---------|------------------------|---------------|
| P-001 | US-001, US-003 | {Main use case} |
| P-002 | US-002, US-004 | {Main use case} |

> This table shows which user stories address each persona's needs. Updated by `/doit.specit`.

---

## Next Steps

After personas are complete:

1. Run `/doit.specit` to create a technical specification
2. The specit command will automatically load this `personas.md` file
3. Each generated user story will reference the appropriate persona ID
