# Quickstart: CLI Project Setup & Template Generation

**Feature**: 010-cli-project-setup | **Date**: 2026-01-10

## Overview

The `doit init` command sets up your project for the Doit workflow. It creates the necessary directory structure and copies command templates for your AI coding agent (Claude Code or GitHub Copilot).

## Prerequisites

- Python 3.11 or higher
- Doit CLI installed (`pip install doit-cli` or from source)
- A project directory to initialize

## Quick Start

### Initialize a New Project

```bash
# Navigate to your project
cd my-project

# Initialize for Claude Code (auto-detected if .claude/ exists)
doit init

# Or explicitly specify the agent
doit init --agent claude

# Initialize for GitHub Copilot
doit init --agent copilot

# Initialize for both agents
doit init --agent claude,copilot
```

### Verify Your Setup

```bash
# Check if everything is set up correctly
doit verify

# Verify specific agent setup
doit verify --agent claude
```

## What Gets Created

### For Claude Code (`--agent claude`)

```
my-project/
├── .doit/
│   ├── memory/          # Project memory (preserved on updates)
│   ├── templates/       # Local template overrides
│   └── scripts/         # Helper scripts
└── .claude/
    └── commands/        # Doit slash commands
        ├── doit.checkin.md
        ├── doit.constitution.md
        ├── doit.documentit.md
        ├── doit.implementit.md
        ├── doit.planit.md
        ├── doit.reviewit.md
        ├── doit.roadmapit.md
        ├── doit.scaffoldit.md
        ├── doit.specit.md
        ├── doit.taskit.md
        └── doit.testit.md
```

### For GitHub Copilot (`--agent copilot`)

```
my-project/
├── .doit/
│   ├── memory/
│   ├── templates/
│   └── scripts/
└── .github/
    ├── copilot-instructions.md   # Updated with doit instructions
    └── prompts/                   # Doit prompt files
        ├── doit-checkin.prompt.md
        ├── doit-constitution.prompt.md
        ├── doit-documentit.prompt.md
        ├── doit-implementit.prompt.md
        ├── doit-planit.prompt.md
        ├── doit-reviewit.prompt.md
        ├── doit-roadmapit.prompt.md
        ├── doit-scaffoldit.prompt.md
        ├── doit-specit.prompt.md
        ├── doit-taskit.prompt.md
        └── doit-testit.prompt.md
```

## Common Operations

### Update Existing Installation

When a new version of doit is released with updated templates:

```bash
# Update templates while preserving custom files
doit init --update

# Force update, overwriting all files (creates backup)
doit init --update --force
```

The update command:
- Creates a backup in `.doit/backups/{timestamp}/`
- Updates all `doit.*` command files to latest versions
- Preserves your custom commands and `.doit/memory/` contents

### Use Custom Templates

Organizations can maintain custom templates:

```bash
# Initialize using custom template directory
doit init --templates /path/to/custom/templates

# Custom templates must have the same structure:
# /path/to/custom/templates/
# ├── commands/    # Claude templates
# └── prompts/     # Copilot templates
```

### Non-Interactive Mode

For scripts and CI/CD:

```bash
# Skip all prompts, use defaults
doit init --yes

# Specify agent and skip prompts
doit init --agent claude --yes
```

## Using the Commands

### Claude Code

After initialization, use slash commands in Claude Code:

```
/doit.specit create a user authentication feature
/doit.planit
/doit.taskit
/doit.implementit
```

### GitHub Copilot

After initialization, use prompts in GitHub Copilot:

```
#doit-specit create a user authentication feature
#doit-planit
#doit-taskit
#doit-implementit
```

Or use agent mode:

```
@workspace /doit-specit create a user authentication feature
```

## Troubleshooting

### "No write permission" Error

```
Error: No write permission to /path/to/project
```

**Solution**: Check directory permissions or run with appropriate privileges.

### "Cannot initialize in system directory" Warning

```
Warning: You are about to initialize doit in /home/user
```

**Solution**: Navigate to a project directory first, or use `--force` if intentional.

### "Missing templates" Error

```
Error: Template directory not found
```

**Solution**: Reinstall doit CLI (`pip install --upgrade doit-cli`).

### Verification Fails

```
Doit project verification: FAILED
  [FAIL] Missing doit commands: doit.specit.md
```

**Solution**: Run `doit init --update` to restore missing files.

## Next Steps

After initialization:

1. **Set up your constitution**: Run `/doit.constitution` (Claude) or `#doit-constitution` (Copilot) to define your project guidelines.

2. **Create your first specification**: Run `/doit.specit` or `#doit-specit` to create a feature specification.

3. **Generate an implementation plan**: Run `/doit.planit` or `#doit-planit` to create a detailed implementation plan.

## Reference

| Command | Description |
|---------|-------------|
| `doit init` | Initialize project for doit workflow |
| `doit init --agent claude` | Initialize for Claude Code |
| `doit init --agent copilot` | Initialize for GitHub Copilot |
| `doit init --agent claude,copilot` | Initialize for both agents |
| `doit init --update` | Update templates in existing project |
| `doit init --templates PATH` | Use custom templates |
| `doit verify` | Verify project setup |
| `doit verify --json` | Output verification as JSON |

For full command reference, see [contracts/cli-contract.md](./contracts/cli-contract.md).
