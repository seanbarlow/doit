# doit.scaffoldit — detailed reference

This file continues the playbook in [SKILL.md](SKILL.md) for sections that don't need to sit in the main context at all times.

## Languages

| Language | Version | Purpose |
| -------- | ------- | ------- |
| TypeScript | 5.0+ | Primary |

## Frameworks

| Framework | Version | Purpose |
| --------- | ------- | ------- |
| React | 18.x | Frontend UI |
| FastAPI | 0.100+ | Backend API |

## Key Libraries

| Library | Version | Purpose | Why Chosen |
| ------- | ------- | ------- | ---------- |
| Tailwind | 3.x | Styling | Rapid prototyping |

<!-- BEGIN:AUTO-GENERATED section="scaffold-captured" -->
Captured during scaffold on 2026-01-10
<!-- END:AUTO-GENERATED -->

## Custom Notes

[User additions preserved here]
```

### 12. Output Summary

After scaffolding, provide:

- List of created directories and files
- Confirmation that doit commands were generated (11 files in `.claude/commands/`)
- Confirmation that tech-stack.md was created in `.doit/memory/`
- Next steps for the user
- Suggested commands to run (e.g., `npm install`, `pip install -r requirements.txt`)
- Reminder to run `/doit.specit` to create feature specifications
- Reminder to run `/doit.documentit` to organize documentation

## Validation

Before creating files:

- Confirm tech stack selection with user
- Check for existing files that would be overwritten
- Prompt for confirmation before creating structure

## Notes

- Always create `.gitkeep` files in empty directories
- Use appropriate naming conventions for the tech stack (camelCase, snake_case, PascalCase)
- Include comments in generated config files explaining key settings
- Respect existing project structure when adding new directories

---

## Error Recovery

### Directory Creation Failure

The project structure could not be created due to permission or filesystem issues.

**ERROR** | If directory creation fails:

1. Check permissions on the target directory: `ls -la .`
2. Verify you have write access to the current directory
3. If permissions are insufficient, adjust them or choose a different location
4. Retry: re-run `/doit.scaffoldit`
5. Verify: `ls -la .doit/` confirms the directory structure was created

> Prevention: Ensure you have write permissions in the target directory before scaffolding

If the above steps don't resolve the issue: create the `.doit/` directory structure manually using `mkdir -p .doit/{templates,config,state,memory,scripts}`.

### Template Copy Failure

Template files could not be copied to the project directory.

**ERROR** | If template files fail to copy:

1. Check if the source templates exist: `python -c "import doit_cli; print(doit_cli.__file__)"`
2. Verify the package installation: `pip show doit-toolkit-cli`
3. If the package is corrupted, reinstall: `pip install --force-reinstall doit-toolkit-cli`
4. Retry: re-run `/doit.scaffoldit`
5. Verify: `ls .doit/templates/` shows template files

If the above steps don't resolve the issue: run `doit init --force` to reinitialize from scratch.

### Existing Project Conflict

The target directory already contains a doit project structure.

**WARNING** | If the directory already has a `.doit/` folder:

1. Check the existing structure: `ls -la .doit/`
2. If you want to preserve existing configuration, choose to merge rather than overwrite
3. If you want a fresh start, back up first: `cp -r .doit/ .doit.backup/`
4. Then reinitialize: `doit init --force`
5. Verify: `doit verify` confirms the project structure is valid

> Prevention: Check for existing `.doit/` directory before scaffolding a new project

If the above steps don't resolve the issue: manually merge the old and new configurations by comparing `.doit.backup/` with the new `.doit/`.

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (project scaffolded)

Display the following at the end of your output:

```markdown
---

## Next Steps

**Project structure created!**

**Recommended**: Run `/doit.specit [feature description]` to create your first feature specification.

**Alternative**: Run `/doit.documentit organize` to organize any existing documentation.
```

### On Existing Project (structure already exists)

If the project already has a structure:

```markdown
---

## Next Steps

**Project structure analyzed!**

**Recommended**: Run `/doit.specit [feature description]` to start developing a new feature.

**Alternative**: Run `/doit.documentit audit` to check documentation health.
```
