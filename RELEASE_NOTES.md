# Release Notes - v0.1.17

**Release Date**: 2026-03-26

## Highlights

This release introduces **MCP server integration**, **project-level personas**, and **error recovery documentation** across all command templates — completing the persona pipeline and significantly improving developer experience.

## What's New

### MCP Server for doit Operations (#055)

Expose doit CLI operations as MCP (Model Context Protocol) tools, enabling AI assistants to call doit directly from the conversation.

**Key Features**:

- Tools exposed: `doit_validate`, `doit_status`, `doit_verify`, and more
- Built on official MCP Python SDK with FastMCP
- Zero-config auto-discovery in Claude Code via `.claude/settings.json`
- Structured JSON responses optimized for AI consumption

### Project-Level Personas with Context Injection (#056)

Personas are now a first-class context source in the doit workflow.

**Key Features**:

- Auto-generates `.doit/memory/personas.md` during `/doit.roadmapit`
- Registered in `context.yaml` at priority 3
- Automatically injected into `/doit.researchit`, `/doit.planit`, and `/doit.specit`

### Persona-Aware User Story Generation (#057)

`/doit.specit` now auto-maps user stories to the most relevant persona using P-NNN traceability IDs.

**Key Features**:

- Automatic persona matching from project-level or feature-level persona files
- Completes the full persona pipeline: templates (053) → context injection (056) → story mapping (057)

### Error Recovery Patterns in All Commands (#058)

All 13 command templates now include structured `## Error Recovery` sections.

**Key Features**:

- 3-5 documented error scenarios per command
- Severity indicators (ERROR/WARNING)
- Numbered recovery steps with verification commands
- Prevention tips and escalation paths

### Update/Upgrade Flow Improvements

- Fixed `doit init --update` to sync all commands to both Claude and Copilot

## Breaking Changes

None.

## Upgrade Instructions

1. Update to the latest version:

   ```bash
   pip install --upgrade doit-toolkit-cli
   ```

2. Run init update to get new templates and MCP server:

   ```bash
   doit init --update
   ```

3. Configure MCP server in your AI assistant (see docs for setup)

## Contributors

- Claude Code implementation assistance

## Full Changelog

See [CHANGELOG.md](./CHANGELOG.md) for complete release history.
