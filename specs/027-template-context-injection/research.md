# Research: Template Context Injection

**Feature**: 027-template-context-injection
**Date**: 2026-01-15

## Overview

This document captures research findings for adding context loading instructions to doit command templates.

## Research Questions

### 1. What is the current template structure?

**Finding**: Each template follows a consistent structure:

```markdown
---
description: [Command description]
handoffs:
  - label: [Next command label]
    agent: [Agent name]
    prompt: [Handoff prompt]
---

## User Input

```text
$ARGUMENTS
```

## Outline

[Main command instructions...]

## [Additional sections as needed]
```

**Decision**: Add context loading step after `## User Input` section and before `## Outline` section.
**Rationale**: This positions context loading early in execution while preserving YAML frontmatter and user input handling.

### 2. How should context loading failures be handled?

**Finding**: The `doit context show` command already handles missing files gracefully, returning warnings but not failing. Templates should mirror this behavior.

**Decision**: Instruct AI to continue without context if the command fails, noting the limitation.
**Rationale**: Non-blocking failures ensure commands work even without full doit setup.
**Alternatives considered**:
- Hard fail on missing context - rejected as too restrictive
- Skip context step entirely if doit not installed - rejected as not detectable in templates

### 3. Which templates need context loading?

**Finding**: All 11 command templates should include context loading:

| Template | Needs Context | Reason |
|----------|---------------|--------|
| doit.specit | Yes | Reference principles for spec alignment |
| doit.planit | Yes | Use tech stack for architecture decisions |
| doit.taskit | Yes | Consider related specs for dependencies |
| doit.implementit | Yes | Follow coding standards |
| doit.reviewit | Yes | Validate against principles |
| doit.checkin | Yes | Verify roadmap alignment |
| doit.constitution | Special | Creates context, but should load existing |
| doit.roadmapit | Yes | Load current roadmap for updates |
| doit.scaffoldit | Yes | Use tech stack for scaffolding |
| doit.documentit | Yes | Reference project context |
| doit.testit | Yes | Consider test requirements |

**Decision**: Add context loading to all 11 templates.
**Rationale**: Consistent behavior across all commands; even doit.constitution benefits from loading existing context.

### 4. What context should each command use?

**Finding**: Different commands benefit from different context sources:

| Command | Constitution | Roadmap | Current Spec | Related Specs |
|---------|-------------|---------|--------------|---------------|
| specit | High | Medium | N/A | High |
| planit | High | Medium | High | Medium |
| taskit | Medium | Low | High | High |
| implementit | High | Low | High | Medium |
| reviewit | High | Low | High | Medium |
| checkin | Medium | High | High | Low |
| constitution | Low | Low | N/A | N/A |
| roadmapit | Low | High | N/A | Low |
| scaffoldit | High | Low | N/A | Low |
| documentit | Medium | Medium | High | Medium |
| testit | High | Low | High | Medium |

**Decision**: Use default context loading (all sources) for all commands initially. Per-command customization is P3 feature.
**Rationale**: Simpler implementation; optimize later based on usage patterns.

### 5. What is the exact context loading instruction format?

**Finding**: AI agents need clear, actionable instructions. After reviewing Claude Code documentation, the recommended format is:

```markdown
## Load Project Context

Before proceeding, load the project context to inform your responses:

\`\`\`bash
doit context show
\`\`\`

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:
- Reference constitution principles when making decisions
- Consider roadmap priorities
- Identify connections to related specifications
```

**Decision**: Use the format above with minor template-specific variations.
**Rationale**: Clear instructions that work with multiple AI agents.

## Resolved Clarifications

No NEEDS CLARIFICATION items from specification - all requirements were well-defined.

## Conclusion

Research complete. Ready to proceed with Phase 1 design artifacts.
