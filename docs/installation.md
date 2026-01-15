# Installation Guide

## Prerequisites

- **Linux/macOS** (or Windows; PowerShell scripts now supported without WSL)
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code) or [GitHub Copilot](https://code.visualstudio.com/)
- [uv](https://docs.astral.sh/uv/) for package management
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## Installation

### Initialize a New Project

The easiest way to get started is to initialize a new project:

```bash
uvx doit-toolkit-cli init <PROJECT_NAME>
```

Or initialize in the current directory:

```bash
uvx doit-toolkit-cli init .
# or use the --here flag
uvx doit-toolkit-cli init --here
```

### Specify AI Agent

You can proactively specify your AI agent during initialization:

```bash
uvx doit-toolkit-cli init <project_name> --ai claude
uvx doit-toolkit-cli init <project_name> --ai copilot
```

### Specify Script Type (Shell vs PowerShell)

All automation scripts now have both Bash (`.sh`) and PowerShell (`.ps1`) variants.

Auto behavior:

- Windows default: `ps`
- Other OS default: `sh`
- Interactive mode: you'll be prompted unless you pass `--script`

Force a specific script type:

```bash
uvx doit-toolkit-cli init <project_name> --script sh
uvx doit-toolkit-cli init <project_name> --script ps
```

### Ignore Agent Tools Check

If you prefer to get the templates without checking for the right tools:

```bash
uvx doit-toolkit-cli init <project_name> --ai claude --ignore-agent-tools
```

## Verification

After initialization, you should see the following slash commands available in your AI agent:

- `/doit.constitution` - Create or update project constitution
- `/doit.scaffoldit` - Generate project folder structure and starter files
- `/doit.documentit` - Organize and enhance project documentation
- `/doit.specit` - Create feature specifications from descriptions
- `/doit.planit` - Generate implementation plans
- `/doit.taskit` - Break down plans into actionable tasks
- `/doit.implementit` - Execute implementation tasks
- `/doit.testit` - Run automated tests and generate reports
- `/doit.reviewit` - Review code for quality and completeness
- `/doit.checkin` - Finalize features and create pull requests
- `/doit.roadmapit` - Create or update project roadmap

You can also verify CLI commands work by running:

```bash
doit --help
```

This should show available CLI commands including:

- `doit init` - Initialize Do-It in a project
- `doit verify` - Verify project structure
- `doit sync-prompts` - Sync templates to AI agents
- `doit context show` - Display loaded project context
- `doit hooks install` - Install git hooks for workflow enforcement
- `doit hooks validate` - Validate branch meets requirements

The `.doit/scripts` directory will contain both `.sh` and `.ps1` scripts.

## Troubleshooting

### Git Credential Manager on Linux

If you're having issues with Git authentication on Linux, you can install Git Credential Manager:

```bash
#!/usr/bin/env bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb
```
