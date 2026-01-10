# Research: Doit Roadmapit Command

**Feature**: 008-doit-roadmapit-command
**Date**: 2026-01-10

## Research Questions

### Q1: What is the best structure for a roadmap file?

**Decision**: Use a three-section structure: Vision, Active Requirements, Deferred Items

**Rationale**:
- Vision provides context for prioritization decisions
- Active Requirements organized by priority (P1-P4) enables clear focus
- Deferred Items preserve context without cluttering active work
- This mirrors successful roadmap patterns from product management

**Alternatives Considered**:
- Flat list with tags: Rejected - harder to scan and prioritize
- Kanban-style columns: Rejected - markdown doesn't render well
- Timeline-based: Rejected - too implementation-focused

### Q2: How should items be prioritized by business value?

**Decision**: Use P1-P4 priority scale with business value rationale

**Rationale**:
- P1: Critical - must have for MVP or blocking
- P2: High - significant business value, near-term
- P3: Medium - valuable but can wait
- P4: Low - nice to have, backlog
- Each item includes rationale explaining the priority

**Alternatives Considered**:
- MoSCoW (Must/Should/Could/Won't): Rejected - less granular
- Numeric scores (1-100): Rejected - false precision
- T-shirt sizes: Rejected - not orderable enough

### Q3: How should the checkin command archive completed items?

**Decision**: Match roadmap items to feature branches via naming convention

**Rationale**:
- Feature branches follow `###-feature-name` pattern
- Roadmap items can include `[###-feature-name]` reference
- On successful checkin, scan roadmap for matching references
- Move matched items to completed_roadmap.md with metadata

**Alternatives Considered**:
- Manual archive: Rejected - too easy to forget
- Issue tracking integration: Rejected - adds external dependency
- Automatic by title match: Rejected - too fragile

### Q4: What clarifying questions should the command ask?

**Decision**: Use progressive disclosure with 3-5 targeted questions

**Rationale**:
- Start with vision/purpose question
- Follow with priority clarification for ambiguous items
- End with enhancement suggestions
- Present options as multiple choice where possible

**Alternatives Considered**:
- Long questionnaire upfront: Rejected - overwhelming
- No questions (AI guesses): Rejected - misses user intent
- Free-form questions: Rejected - harder to process

### Q5: How should AI suggestions be generated?

**Decision**: Analyze project context and suggest 2-5 complementary features

**Rationale**:
- Read constitution for project principles
- Read existing roadmap for gaps
- Suggest features that complement existing items
- Include rationale for each suggestion

**Alternatives Considered**:
- Generic suggestions: Rejected - not valuable
- Many suggestions (10+): Rejected - overwhelming
- No suggestions: Rejected - misses opportunity to add value

## Existing Pattern Analysis

### Command Template Structure

Analyzed existing commands in `.claude/commands/`:
- YAML frontmatter with `description` and optional `handoffs`
- `## User Input` section capturing `$ARGUMENTS`
- `## Outline` section with numbered execution steps
- Consistent use of conditional logic for file existence

### Memory File Patterns

Analyzed `.doit/memory/constitution.md`:
- Structured markdown with clear sections
- Placeholders in `[BRACKETS]` for user-specific content
- Comments providing guidance
- Version tracking in governance section

### Scaffold Integration Pattern

Analyzed `doit.scaffoldit.md`:
- Section 8 copies command templates
- Explicit list of 9 command files
- Uses `.doit/templates/commands/` as source

## Conclusions

1. **Template structure is well-established** - follow existing patterns exactly
2. **Memory file location is `.doit/memory/`** - use same directory
3. **Scaffold updates require explicit file list** - add new command to list
4. **Checkin integration via branch matching** - safest approach
5. **Priority system P1-P4 is consistent** - with spec.md user stories
