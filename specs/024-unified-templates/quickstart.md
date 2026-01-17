# Quickstart: Unified Template Management

**Feature**: 024-unified-templates
**Date**: 2026-01-15

## Prerequisites

- Python 3.11+
- pytest installed
- Development environment set up with `pip install -e .`

## Implementation Steps

### Step 1: Modify Agent Model (5 minutes)

Update `src/doit_cli/models/agent.py`:

```python
@property
def template_directory(self) -> str:
    """All agents now use commands/ as single source."""
    return "commands"

@property
def needs_transformation(self) -> bool:
    """Copilot requires transformation, Claude does not."""
    return self == Agent.COPILOT
```

**Verify**: Run `pytest tests/unit/test_agent.py -v`

---

### Step 2: Update TemplateManager (10 minutes)

Update `src/doit_cli/services/template_manager.py`:

```python
def copy_templates_for_agent(self, agent: Agent) -> None:
    """Copy or transform templates based on agent type."""
    source_path = self.get_template_source_path(agent)

    if agent.needs_transformation:
        # Transform command templates to Copilot prompt format
        self._transform_and_write_templates(source_path, agent)
    else:
        # Direct copy for Claude
        self._copy_templates(source_path, agent)
```

**Verify**: Run `pytest tests/unit/test_template_manager.py -v`

---

### Step 3: Add Transformation Integration (10 minutes)

Create helper method in TemplateManager:

```python
def _transform_and_write_templates(self, source_path: Path, agent: Agent) -> None:
    """Transform command templates to agent-specific format."""
    from doit_cli.services.prompt_transformer import PromptTransformer

    transformer = PromptTransformer()
    for template in source_path.glob("doit.*.md"):
        content = template.read_text()
        transformed = transformer.transform(content)
        output_name = self._get_output_filename(template.name, agent)
        output_path = self._get_agent_output_path(agent) / output_name
        output_path.write_text(transformed)
```

**Verify**: Run `pytest tests/unit/test_prompt_transformer.py -v`

---

### Step 4: Update Tests (15 minutes)

Update test fixtures and assertions:

1. Update `tests/conftest.py` - Ensure fixtures use correct paths
2. Update `tests/unit/test_agent.py` - Add tests for `needs_transformation`
3. Update `tests/integration/test_init_command.py` - Verify both agents work

**Verify**: Run full test suite `pytest -v`

---

### Step 5: Remove Duplicate Templates (5 minutes)

```bash
# Verify prompts directory is unused
grep -r "templates/prompts" src/

# Remove duplicate directory
rm -rf templates/prompts/
```

**Verify**: Run `pytest -v` to ensure nothing breaks

---

### Step 6: Manual Verification (5 minutes)

```bash
# Test Claude initialization
cd /tmp && mkdir test-claude && cd test-claude
doit init --agent claude --yes
ls -la .claude/commands/

# Test Copilot initialization
cd /tmp && mkdir test-copilot && cd test-copilot
doit init --agent copilot --yes
ls -la .github/prompts/

# Test sync-prompts
doit sync-prompts --check
```

---

## Quick Validation Checklist

- [ ] `Agent.template_directory` returns "commands" for both agents
- [ ] `Agent.needs_transformation` returns `True` for Copilot, `False` for Claude
- [ ] `doit init --agent claude` copies templates directly
- [ ] `doit init --agent copilot` transforms templates
- [ ] `doit sync-prompts` generates prompts from command templates
- [ ] `templates/prompts/` directory removed
- [ ] All tests pass

## Common Issues

### Issue: Tests fail after removing prompts directory

**Solution**: Update any test fixtures that reference `templates/prompts/`

### Issue: PromptTransformer not found

**Solution**: Ensure import path is correct: `from doit_cli.services.prompt_transformer import PromptTransformer`

### Issue: File naming mismatch

**Solution**: Use agent's `file_pattern` property for correct naming:
- Claude: `doit.{name}.md`
- Copilot: `doit-{name}.prompt.md`
