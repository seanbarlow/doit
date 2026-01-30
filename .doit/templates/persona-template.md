# Persona Template

> **Standalone Usage**: This template can be used independently of `/doit.researchit` for brownfield projects.
>
> **How to use**:
> 1. Copy this file to your feature's specs directory: `specs/{feature}/personas.md`
> 2. Fill in the placeholders (marked with `{...}`) with your persona details
> 3. For multiple personas, duplicate the entire persona section below
> 4. Validate using the checklist at the bottom
>
> **For multi-persona documents**: Use the [personas-output-template.md](personas-output-template.md) format which includes a summary table.

---

## Persona: {ID}

> Replace `{ID}` with a unique identifier like `P-001`, `P-002`, etc.

### Identity

- **Name**: {Persona Name - e.g., "Developer Dana", "Manager Mike"}
- **Role**: {Job Title / Role - e.g., "Senior Software Engineer", "Product Manager"}
- **Archetype**: {Power User | Casual User | Administrator | Approver | Observer}

### Demographics

- **Experience Level**: {Junior | Mid | Senior | Executive}
- **Team Size**: {Solo | Small Team (2-5) | Large Team (6-20) | Enterprise (20+)}
- **Domain Expertise**: {Description of their domain knowledge and expertise areas}

### Goals

**Primary Goal**: {Main objective this persona wants to achieve}

**Secondary Goals**:
- {Goal 1 - Nice-to-have objective}
- {Goal 2 - Nice-to-have objective}

### Pain Points (prioritized)

1. {Most critical pain point - the biggest frustration}
2. {Second pain point}
3. {Third pain point}

### Behavioral Patterns

- **Technology Proficiency**: {Low | Medium | High}
- **Work Style**: {Description of how they typically work - e.g., "Prefers quick iterations", "Methodical and thorough"}
- **Decision Making**: {How they make decisions - e.g., "Data-driven", "Consensus-seeking", "Quick and intuitive"}

### Success Criteria

{What does success look like for this persona? How will they know the feature is working for them?}

### Usage Context

{When and where do they encounter this problem? What is their typical workflow?}

### Relationships

| Related Persona | Relationship Type | Context |
|-----------------|-------------------|---------|
| {P-002} | {manages \| reports_to \| collaborates \| approves \| blocks} | {Description of the relationship dynamic} |
| {P-003} | {relationship type} | {Description} |

> If no direct relationships: "No direct relationships identified"

### Conflicts & Tensions

{Document any conflicting goals with other personas. What tradeoffs might need to be made?}

> If no conflicts: "No known conflicts with other personas"

---

## Validation Checklist

Before finalizing your persona, verify:

- [ ] ID follows format P-NNN (e.g., P-001, P-002)
- [ ] Name is memorable and descriptive
- [ ] Role clearly describes their job function
- [ ] Archetype is one of: Power User, Casual User, Administrator, Approver, Observer
- [ ] At least one primary goal is defined
- [ ] At least three pain points are listed in priority order
- [ ] Technology proficiency level is specified
- [ ] Success criteria are measurable
- [ ] Usage context describes real-world scenarios
- [ ] Relationships reference valid persona IDs (if applicable)

---

## Archetype Reference

| Archetype | Description |
|-----------|-------------|
| **Power User** | Frequent user with advanced needs, wants efficiency and shortcuts |
| **Casual User** | Occasional user with basic needs, values simplicity |
| **Administrator** | Manages system configuration and user access |
| **Approver** | Decision-maker who reviews and approves work |
| **Observer** | Stakeholder who views but doesn't interact directly |

---

## Relationship Types Reference

| Type | Direction | Meaning |
|------|-----------|---------|
| **manages** | A → B | A has authority over B's work |
| **reports_to** | A → B | A reports to B (inverse of manages) |
| **collaborates** | A ↔ B | A and B work together as peers |
| **approves** | A → B | A must approve B's work before it proceeds |
| **blocks** | A → B | A's work blocks B from proceeding |
