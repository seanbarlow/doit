# Research: GitHub Copilot Prompts Synchronization

**Feature**: 023-copilot-prompts-sync
**Date**: 2026-01-15
**Status**: Complete
**Updated**: 2026-01-15 (revised based on official GitHub and AGENTS.md documentation)

## Research Questions

### RQ-001: GitHub Copilot Custom Instructions Architecture

**Question**: What file types does GitHub Copilot support for custom instructions?

**Decision**: Use prompt files (`*.prompt.md`) in `.github/prompts/` directory

**Rationale** (from GitHub documentation):

GitHub Copilot supports three types of custom instruction files:

| Type | Location | Scope | Auto-Applied |
| ---- | -------- | ----- | ------------ |
| Repository-wide | `.github/copilot-instructions.md` | All requests | Yes |
| Path-specific | `.github/instructions/*.instructions.md` | Matching file paths | Yes |
| Prompt files | `*.prompt.md` (preview) | Explicit reference | No |

**Key Finding**: Prompt files are in **public preview** and are:

- Available in VS Code, Visual Studio, JetBrains IDEs only
- Explicitly referenced per chat interaction (not auto-applied)
- Plain markdown format (no YAML frontmatter required)
- Subject to change as they're in preview

**Source**: [GitHub Copilot Response Customization](https://docs.github.com/en/copilot/concepts/prompting/response-customization)

---

### RQ-002: AGENTS.md Standard

**Question**: What is the AGENTS.md standard and how does it relate to this feature?

**Decision**: Consider AGENTS.md as a complementary format for broader AI tool support

**Rationale** (from [agents.md](https://agents.md/)):

AGENTS.md is a widely adopted open standard (60,000+ projects) described as "a README for agents." It provides a dedicated, predictable location for AI coding agent instructions.

**Tool Support**: AGENTS.md is recognized by 20+ tools including:

- GitHub Copilot's Coding Agent
- Google's Gemini CLI and Jules
- OpenAI Codex
- Cursor, VS Code, Zed
- Aider, Factory, Windsurf

**Key Characteristics**:

- Plain markdown with flexible headings
- No required fields or special format
- Hierarchical precedence (subdirectory files override root)
- Agents automatically parse and follow instructions

**Recommended Sections**:

- Project overview
- Build and test commands
- Code style guidelines
- Testing instructions
- PR/commit guidelines

**Relationship to Our Feature**:

| Aspect | AGENTS.md | Copilot Prompt Files |
| ------ | --------- | -------------------- |
| Purpose | Repository-wide context | Task-specific workflows |
| Scope | All AI tools | GitHub Copilot only |
| Auto-applied | Yes | No (explicit reference) |
| Adoption | 60,000+ projects | Preview feature |

**Source**: [https://agents.md/](https://agents.md/)

---

### RQ-003: Prompt File Format

**Question**: What format does GitHub Copilot expect for prompt files?

**Decision**: Plain markdown without YAML frontmatter

**Rationale**:

GitHub documentation examples show prompt files as simple markdown:

**Example from docs** (`New React form.prompt.md`):

```markdown
Your goal is to generate a new React form component.

Ask for the form name and fields if not provided.

Requirements for the form:
- Use form design system components
- Use `react-hook-form` for form state management
- Use `yup` for validation
```

**Example from docs** (`API security review.prompt.md`):

```markdown
Secure REST API review:
- Ensure endpoints protected by authentication
- Validate user inputs and sanitize data
- Implement rate limiting and throttling
- Implement logging and monitoring
```

**Key Finding**: No YAML frontmatter is used or documented for prompt files. The format is straightforward markdown with clear instructions.

---

### RQ-004: Command Template Structure Analysis

**Question**: What is the structure of existing doit command templates that need transformation?

**Decision**: Strip YAML frontmatter, preserve markdown body

**Rationale**:

Existing command templates in `.doit/templates/commands/` follow this structure:

```yaml
---
description: [Command description]
handoffs: (optional)
  - label: [Label]
    agent: [Agent name]
    prompt: [Handoff prompt]
---
```

Followed by markdown sections:

- `## User Input` - Placeholder for user arguments (`$ARGUMENTS`)
- `## Outline` - Step-by-step workflow instructions
- Additional sections (Key Rules, Notes, etc.)

**Transformation Required**:

| Source (Claude Code) | Target (Copilot Prompt) |
| -------------------- | ----------------------- |
| YAML frontmatter | Remove entirely |
| `$ARGUMENTS` | "the user's input" or remove |
| `## User Input` block | Simplify or adapt |
| `## Outline` | Preserve as main body |
| `## Key Rules` | Preserve |

---

### RQ-005: Content Transformation Rules

**Question**: What specific transformations are needed to convert Claude Code commands to Copilot prompts?

**Decision**: Strip frontmatter, simplify argument handling, preserve instructions

**Transformation Rules**:

1. **YAML Frontmatter**:
   - **Remove entirely** - Copilot prompt files don't use frontmatter
   - Optionally add description as first paragraph

2. **Argument Handling**:
   - Replace `$ARGUMENTS` with natural language: "the user's input"
   - Simplify `## User Input` section

3. **Script References**:
   - Keep `.doit/scripts/` paths as-is (they work in both contexts)
   - Copilot can execute bash scripts similarly

4. **Section Preservation**:
   - `## Outline` → Preserve as main instruction body
   - `## Key Rules` → Preserve
   - `## Notes` → Preserve

**Example Transformation**:

Source (`doit.checkin.md`):

```markdown
---
description: Finalize feature implementation...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding.

## Outline
1. Run setup script...
```

Target (`doit.checkin.prompt.md`):

```markdown
# Finalize Feature Implementation

Finalize feature implementation, close issues, update roadmaps, and create pull request.

## User Input

Consider any arguments or options the user provides.

## Outline
1. Run setup script...
```

---

### RQ-006: Drift Detection Strategy

**Question**: How should we detect when command templates and prompts are out of sync?

**Decision**: Compare file modification timestamps + content hash

**Rationale**:

- File modification time (`os.path.getmtime()`) provides quick check
- Content hash (MD5/SHA256) provides definitive sync status
- Two-tier approach: timestamp for quick scan, hash for verification

**Implementation**:

```python
def is_out_of_sync(command_path: Path, prompt_path: Path) -> bool:
    if not prompt_path.exists():
        return True  # Missing prompt

    # Quick check: timestamp comparison
    if command_path.stat().st_mtime > prompt_path.stat().st_mtime:
        return True

    # Detailed check: content-based (optional)
    return False
```

---

### RQ-007: Existing CLI Command Patterns

**Question**: How do existing doit CLI commands handle file operations?

**Decision**: Follow existing patterns in `src/doit_cli/commands/`

**Rationale**:

- Commands use `typer.Typer()` app with `@app.command()` decorators
- Rich console for formatted output
- Pathlib for file operations
- Consistent error handling with `rich.console.print()` for errors

**Pattern to Follow**:

```python
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def sync(
    command_name: Optional[str] = typer.Argument(None, help="Specific command to sync"),
    check_only: bool = typer.Option(False, "--check", "-c", help="Check sync status only"),
):
    """Synchronize GitHub Copilot prompts with doit commands."""
    ...
```

---

## Summary

All research questions resolved based on official documentation.

| Question | Status | Decision |
| -------- | ------ | -------- |
| RQ-001 | ✅ Resolved | Use `*.prompt.md` in `.github/prompts/` |
| RQ-002 | ✅ Resolved | AGENTS.md is complementary, broader tool support |
| RQ-003 | ✅ Resolved | Plain markdown, no YAML frontmatter |
| RQ-004 | ✅ Resolved | Strip frontmatter, preserve markdown body |
| RQ-005 | ✅ Resolved | Remove frontmatter, simplify arguments, preserve instructions |
| RQ-006 | ✅ Resolved | Timestamp + content comparison |
| RQ-007 | ✅ Resolved | Follow existing CLI patterns |

## Key Findings

1. **No YAML frontmatter** - Copilot prompt files are plain markdown
2. **Preview feature** - Prompt files are in public preview (VS Code, Visual Studio, JetBrains only)
3. **Explicit reference** - Prompt files are explicitly invoked, not auto-applied
4. **AGENTS.md standard** - Widely adopted (60,000+ projects), broader tool support
5. **Simpler format** - Just clear markdown instructions for both formats

## Architectural Recommendation

Given the research findings, consider a two-pronged approach:

1. **Primary**: Generate `*.prompt.md` files in `.github/prompts/` for Copilot-specific workflows
2. **Future**: Consider AGENTS.md for repository-wide context applicable to all AI tools

This feature focuses on prompt file generation. AGENTS.md integration could be a follow-up feature.

## Next Steps

Proceed to `/doit.taskit` for task breakdown
