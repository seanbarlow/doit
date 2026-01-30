# Research: Research Command for Product Owners

**Feature**: 052-researchit-command
**Date**: 2026-01-29
**Status**: Complete

## Research Summary

This document captures technical research and design decisions for the `/doit.researchit` command.

## Key Decisions

### 1. Interactive Q&A Implementation

**Decision**: Use Rich library's Prompt and Console for interactive Q&A sessions.

**Rationale**:
- Rich is already in the tech stack and provides excellent terminal formatting
- `rich.prompt.Prompt` handles user input with validation
- `rich.console.Console` provides formatted output with colors and panels
- Consistent with existing doit commands (e.g., constitution wizard)

**Alternatives Considered**:
- readchar for low-level input: Too primitive for multi-line answers
- questionary library: Would add new dependency, Rich is sufficient
- Click prompts: Typer already wraps Rich, unnecessary layer

### 2. Research Artifact Structure

**Decision**: Generate four markdown files with standardized structure.

**Rationale**:
- Markdown is the universal format for doit (AI-native design principle)
- Four files (research.md, user-stories.md, interview-notes.md, competitive-analysis.md) allow independent consumption
- Consistent with existing spec folder structure

**Alternatives Considered**:
- Single combined file: Would be too large and harder to navigate
- YAML/JSON for structured data: Less readable for Product Owners
- Database storage: Violates file-based storage principle

### 3. Session State Management

**Decision**: Store session state as JSON in `.doit/state/research-draft-{feature}.json`.

**Rationale**:
- JSON is easy to serialize/deserialize with Python stdlib
- Follows existing pattern (`.doit/state/` for transient data)
- Draft files are automatically cleaned after completion (FR-018)

**Alternatives Considered**:
- Save partial markdown files: Would create incomplete artifacts
- Memory-only state: Would lose progress on interruption

### 4. User Story Derivation

**Decision**: Extract user stories from structured Q&A responses using template-based generation.

**Rationale**:
- Templates ensure consistent Given/When/Then format
- AI-assisted but user-driven (user provides content, system structures it)
- Matches existing user story format in spec-template.md

**Alternatives Considered**:
- AI-generated stories: Out of scope per spec (user provides all content)
- Free-form stories: Would lose structure for specit handoff

### 5. Specit Integration

**Decision**: Store research artifacts in specs/{feature}/ and have specit check for existing artifacts.

**Rationale**:
- Same directory structure as spec.md keeps related files together
- specit already reads from SPECS_DIR, minimal modification needed
- Research artifacts become part of feature version control

**Alternatives Considered**:
- Separate research/ directory: Would complicate feature organization
- Context injection via CLI flag: Extra step for users

## Q&A Question Set

Based on research, the following questions will guide Product Owners:

### Phase 1: Problem Understanding
1. What problem are you trying to solve?
2. Who currently experiences this problem?
3. What happens today without this solution?

### Phase 2: Users and Goals
4. Who are the primary users of this feature?
5. What does success look like for these users?
6. Are there different types of users with different needs?

### Phase 3: Requirements and Constraints
7. What must this feature absolutely do? (Must-haves)
8. What would be nice to have but isn't essential?
9. What should this feature NOT do? (Explicit exclusions)
10. Are there any constraints (timeline, budget, compliance)?

### Phase 4: Success Metrics
11. How will you measure if this feature is successful?
12. What would failure look like?

## Technical Dependencies

| Component | Library | Purpose |
|-----------|---------|---------|
| CLI Command | Typer | Command registration |
| Terminal UI | Rich | Prompts, panels, formatting |
| State Storage | JSON (stdlib) | Session persistence |
| File I/O | pathlib | Cross-platform paths |

## Integration Points

### Input
- Feature name from CLI argument
- User responses from interactive prompts

### Output
- `specs/{feature}/research.md`
- `specs/{feature}/user-stories.md`
- `specs/{feature}/interview-notes.md`
- `specs/{feature}/competitive-analysis.md`

### Consumed By
- `/doit.specit` - Reads research artifacts as context

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User abandons mid-session | Medium | Low | Draft auto-save on interrupt |
| Minimal answers provided | Medium | Medium | Prompts include examples and guidance |
| Research doesn't map to spec | Low | High | Q&A structure mirrors spec sections |
