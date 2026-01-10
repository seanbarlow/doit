# Research: CLI Project Setup & Template Generation

**Feature**: 010-cli-project-setup | **Date**: 2026-01-10 | **Phase**: 0

## Purpose

Document technical decisions, resolved clarifications, and research findings for the CLI project setup feature. This research informs the implementation plan and design artifacts.

## Technical Decisions

### TD-001: Agent Detection Strategy

**Decision**: Use file-based detection with fallback to interactive prompt.

**Detection Order**:
1. Check for `--agent` CLI flag (explicit selection)
2. Check for existing `.claude/` directory → Claude agent
3. Check for existing `.github/copilot-instructions.md` → Copilot agent
4. Check for existing `.github/prompts/` directory → Copilot agent
5. If no indicators found, prompt user interactively

**Rationale**: File-based detection is reliable and doesn't require parsing configuration files. The order prioritizes explicit user choice, then existing Claude setup (more specific indicator), then Copilot setup.

### TD-002: Template Storage Location

**Decision**: Bundle templates within the installed Python package using `importlib.resources`.

**Structure**:
```
doit/
├── templates/
│   ├── commands/           # Claude templates (11 files)
│   │   ├── doit.checkin.md
│   │   ├── doit.constitution.md
│   │   └── ... (9 more)
│   └── prompts/            # Copilot templates (11 files)
│       ├── doit-checkin.prompt.md
│       ├── doit-constitution.prompt.md
│       └── ... (9 more)
```

**Rationale**: Using `importlib.resources` ensures templates are accessible regardless of installation method (pip, pipx, editable install). This is the modern Python approach for bundled data files.

### TD-003: Copilot Prompt File Format

**Decision**: Use `.prompt.md` extension with YAML frontmatter for Copilot prompts.

**Format**:
```markdown
---
mode: agent
description: Brief description for prompt picker
---

# Prompt content here
```

**Rationale**: GitHub Copilot recognizes `.prompt.md` files in `.github/prompts/` as reusable prompts. The YAML frontmatter allows specifying mode (agent vs ask) and description for the prompt picker UI.

### TD-004: Template Naming Convention

**Decision**: Different naming conventions per agent for compatibility.

| Agent | Directory | File Pattern | Example |
|-------|-----------|--------------|---------|
| Claude | `.claude/commands/` | `doit.{command}.md` | `doit.specit.md` |
| Copilot | `.github/prompts/` | `doit-{command}.prompt.md` | `doit-specit.prompt.md` |

**Rationale**: Claude Code uses dot notation for slash commands (`/doit.specit`). GitHub Copilot uses the `#` prefix with filename-based invocation (`#doit-specit`). Each format follows the native conventions of the respective agent.

### TD-005: Backup Strategy for Updates

**Decision**: Create timestamped backups in `.doit/backups/` before overwriting files.

**Backup Path Pattern**: `.doit/backups/{timestamp}/{relative-path}`

**Example**:
```
.doit/backups/
└── 2026-01-10T143022/
    └── .claude/commands/
        ├── doit.specit.md
        └── doit.planit.md
```

**Rationale**: Timestamped directories allow multiple backups without collision. Preserving the relative path structure makes it easy to understand and restore specific files.

### TD-006: Multi-Agent Initialization

**Decision**: Support initializing for multiple agents in a single command using `--agent` flag with comma-separated values.

**Examples**:
- `doit init --agent claude` - Claude only
- `doit init --agent copilot` - Copilot only
- `doit init --agent claude,copilot` - Both agents
- `doit init` (with prompt) - User selects one or both

**Rationale**: Many developers use both Claude and Copilot depending on context. Supporting multi-agent initialization reduces friction for these users.

## Resolved Clarifications

### RC-001: What constitutes a "doit-prefixed" file?

**Resolution**: Files matching the pattern `doit.*.md` (Claude) or `doit-*.prompt.md` (Copilot) are considered doit-managed. All other files in the command/prompt directories are user-managed and preserved during updates.

### RC-002: How to handle copilot-instructions.md?

**Resolution**: Create `.github/copilot-instructions.md` if it doesn't exist. If it exists, append doit-specific instructions in a clearly marked section:

```markdown
<!-- DOIT INSTRUCTIONS START -->
## Doit Workflow Commands

This project uses the Doit workflow. Use the prompts in `.github/prompts/` prefixed with `doit-` for structured development tasks.

Available commands: #doit-specit, #doit-planit, #doit-taskit, #doit-implementit, #doit-testit, #doit-reviewit, #doit-checkin, #doit-constitution, #doit-scaffoldit, #doit-roadmapit, #doit-documentit
<!-- DOIT INSTRUCTIONS END -->
```

The marked section allows updates to replace only doit-specific content without affecting user-added instructions.

### RC-003: Safe directory detection?

**Resolution**: Warn and require `--force` or interactive confirmation when initializing in:
- Home directory (`~` or `$HOME`)
- Root directory (`/`)
- System directories (`/usr`, `/etc`, `/var`, `/opt`, `/bin`, `/sbin`)
- Common workspace roots (`/workspace`, `/workspaces`)

**Implementation**: Check if `cwd.resolve()` matches any of these patterns.

### RC-004: Rollback on failure?

**Resolution**: Use a transaction-like approach:
1. Create all directories first (reversible)
2. Copy all files to a staging area (`.doit/.staging/`)
3. Move files from staging to final location (atomic on most filesystems)
4. On failure, delete staging area and any created directories

This ensures partial initialization doesn't leave the project in an inconsistent state.

## Existing Pattern Analysis

### Existing CLI Commands (from 001-doit-command-refactor)

The project already has CLI infrastructure using typer:
- `src/doit/cli/main.py` - Main CLI entry point
- Commands use rich for terminal output
- Standard typer patterns for options and arguments

### Existing Template Structure

Current templates in `templates/commands/`:
```
doit.checkin.md      doit.planit.md       doit.scaffoldit.md
doit.constitution.md doit.reviewit.md     doit.specit.md
doit.documentit.md   doit.roadmapit.md    doit.taskit.md
doit.implementit.md                        doit.testit.md
```

All templates follow the same markdown structure with YAML-like metadata block.

## Technology Compatibility

### Claude Code Requirements
- Directory: `.claude/commands/`
- File extension: `.md`
- Invocation: `/doit.{command}` (slash command)
- Recognition: Automatic from directory placement

### GitHub Copilot Requirements
- Directory: `.github/prompts/`
- File extension: `.prompt.md`
- Invocation: `#{filename}` (without extension)
- Recognition: Requires `.github/copilot-instructions.md` for project context
- Mode: `agent` mode recommended for multi-step workflows

## Dependencies

### Runtime Dependencies
- typer >= 0.9.0 (CLI framework)
- rich >= 13.0.0 (terminal output)
- Python 3.11+ (pathlib improvements, importlib.resources)

### Development Dependencies
- pytest >= 7.0.0 (testing)
- pytest-tmp-files >= 0.0.2 (file system fixtures)

## Open Questions (None)

All clarifications have been resolved. The feature is ready for Phase 1 design.
