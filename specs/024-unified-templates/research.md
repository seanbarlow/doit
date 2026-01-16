# Research: Unified Template Management

**Feature**: 024-unified-templates
**Date**: 2026-01-15

## Research Questions

### Q1: How does TemplateManager currently handle Copilot templates?

**Investigation**: Reviewed `src/doit_cli/services/template_manager.py`

**Findings**:

- `get_template_source_path(agent)` uses `agent.template_directory` to determine source
- For Copilot, this returns `templates/prompts/` (from `Agent.template_directory`)
- Templates are copied directly without transformation in `copy_templates_for_agent()`

**Decision**: Modify `Agent.template_directory` to always return "commands" and add transformation step for Copilot.

**Rationale**: Centralizes template source while maintaining agent-specific output format.

**Alternatives Rejected**:

- Keep separate directories with sync script: Introduces maintenance burden and drift risk
- Merge into single format: Would break agent-specific conventions

---

### Q2: Does PromptTransformer support all required conversions?

**Investigation**: Reviewed `src/doit_cli/services/prompt_transformer.py`

**Findings**:

The existing `PromptTransformer` class already handles:

- YAML frontmatter stripping (`strip_yaml_frontmatter()`)
- `$ARGUMENTS` placeholder replacement (`replace_arguments_placeholder()`)
- Full template transformation (`transform()`)

**Decision**: Reuse existing PromptTransformer without modification.

**Rationale**: The transformer was designed for exactly this purpose during spec 023 implementation.

**Alternatives Rejected**:

- Create new transformer: Unnecessary duplication of existing functionality

---

### Q3: What changes are needed to Agent model?

**Investigation**: Reviewed `src/doit_cli/models/agent.py`

**Findings**:

Current `template_directory` property:

```python
@property
def template_directory(self) -> str:
    directories = {
        Agent.CLAUDE: "commands",
        Agent.COPILOT: "prompts",
    }
    return directories[self]
```

**Decision**: Change both agents to return "commands" and add new `needs_transformation` property.

**Rationale**: Simplest change that enables single source while preserving output format differences.

**Implementation**:

```python
@property
def template_directory(self) -> str:
    return "commands"  # Single source for all agents

@property
def needs_transformation(self) -> bool:
    return self == Agent.COPILOT
```

---

### Q4: How will sync-prompts command be affected?

**Investigation**: Reviewed `src/doit_cli/services/template_reader.py`

**Findings**:

- `TemplateReader` already reads from `templates/commands/` as primary source
- It falls back to `.doit/templates/commands/` for end-user projects
- The `sync-prompts` command already sources from commands/, no changes needed

**Decision**: No changes required to sync-prompts command.

**Rationale**: The sync-prompts infrastructure was designed for this exact use case.

---

### Q5: What files reference templates/prompts/?

**Investigation**: Searched codebase for references

**Findings**:

```bash
grep -r "templates/prompts" src/
# No matches in src/ directory

grep -r "prompts" src/doit_cli/models/agent.py
# Line 35: Agent.COPILOT: "prompts"
```

Only `Agent.template_directory` references the prompts directory.

**Decision**: Single point of change required - modify Agent model only.

**Rationale**: Clean separation of concerns makes this change low-risk.

---

## Summary

| Question | Decision | Risk Level |
| -------- | -------- | ---------- |
| Template source | Modify Agent.template_directory | Low |
| Transformation | Reuse existing PromptTransformer | Low |
| Agent model | Add needs_transformation property | Low |
| sync-prompts | No changes needed | None |
| File references | Single change point in agent.py | Low |

**Overall Risk Assessment**: LOW - Changes are isolated and well-understood.

**Prerequisites Resolved**: All NEEDS CLARIFICATION items from spec resolved through code investigation.
