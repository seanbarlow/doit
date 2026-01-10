# Doit CLI

A CLI tool to bootstrap your projects for Spec-Driven Development (SDD).

## Installation

```bash
pip install doit-cli
```

Or with uv:

```bash
uvx doit-cli
```

## Commands

### `doit init`

Initialize a new doit project with bundled templates.

```bash
# Initialize in current directory
doit init .

# Initialize with specific agent
doit init . --agent claude
doit init . --agent copilot
doit init . --agent claude,copilot  # Both agents

# Update existing project templates
doit init . --update

# Custom template source
doit init . --templates /path/to/custom/templates
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--agent` | `-a` | Target agent(s): `claude`, `copilot`, or `claude,copilot` for both |
| `--templates` | `-t` | Custom template directory path |
| `--update` | `-u` | Update existing project, preserving custom files |
| `--force` | `-f` | Overwrite existing files without backup |
| `--yes` | `-y` | Skip confirmation prompts |

#### What it creates

For Claude Code:
```
.doit/
  memory/           # Project memory files
  templates/        # Template files
  scripts/          # Helper scripts
.claude/
  commands/         # Claude Code slash commands
    doit-specit.md
    doit-planit.md
    doit-taskit.md
    doit-implementit.md
    doit-testit.md
    doit-reviewit.md
    doit-checkin.md
    doit-constitution.md
    doit-scaffoldit.md
    doit-roadmapit.md
    doit-documentit.md
```

For GitHub Copilot:
```
.doit/
  memory/
  templates/
  scripts/
.github/
  prompts/          # Copilot prompt files
    doit-specit.prompt.md
    doit-planit.prompt.md
    ...
  copilot-instructions.md  # Updated with doit section
```

### `doit verify`

Verify doit project setup and report status.

```bash
# Verify current directory
doit verify .

# Check only Claude setup
doit verify . --agent claude

# Output as JSON
doit verify . --json
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--agent` | `-a` | Specific agent to check: `claude`, `copilot`, or `both` |
| `--json` | `-j` | Output results as JSON |

#### Checks performed

- `.doit/` folder structure exists
- Agent command directories exist
- Command template files are present
- Project constitution exists
- Project roadmap exists
- Copilot instructions file exists (for Copilot agent)

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test file
pytest tests/unit/test_scaffolder.py
```

### Project Structure

```
src/doit_cli/
  cli/
    init_command.py      # Init command implementation
    verify_command.py    # Verify command implementation
  models/
    agent.py             # Agent enum (CLAUDE, COPILOT)
    project.py           # Project dataclass
    template.py          # Template dataclass
    results.py           # InitResult, VerifyResult
  services/
    agent_detector.py    # Detect installed agents
    backup_service.py    # Backup management
    scaffolder.py        # Create project structure
    template_manager.py  # Manage templates
    validator.py         # Project validation
templates/
  commands/              # Claude command templates
  prompts/               # Copilot prompt templates
```

## License

MIT
