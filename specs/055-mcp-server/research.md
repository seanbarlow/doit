# Research: MCP Server for doit Operations

**Feature**: 055-mcp-server
**Date**: 2026-03-26

## R1: MCP Python SDK Selection

**Decision**: Use the official `mcp` Python SDK (which includes FastMCP)

**Rationale**: FastMCP was incorporated into the official MCP Python SDK and is the recommended way to build MCP servers in Python. It auto-generates JSON schemas from type hints and docstrings, handles protocol negotiation, and supports stdio transport out of the box.

**Alternatives considered**:

- `fastmcp` standalone package: Now merged into `mcp` SDK, would be a redundant dependency
- Raw MCP protocol implementation: Unnecessary complexity, FastMCP handles all boilerplate
- HTTP-based custom API: Not compatible with AI assistant MCP integration patterns

## R2: Transport Protocol

**Decision**: stdio transport only for MVP

**Rationale**: stdio is the standard transport for local AI assistant integration. Both Claude Code and GitHub Copilot spawn MCP servers as subprocesses communicating over stdin/stdout. SSE/HTTP transport would add complexity without immediate benefit since all target consumers use stdio.

**Alternatives considered**:

- SSE (Server-Sent Events): Useful for remote/shared servers, not needed for local CLI tool
- Streamable HTTP: Newer transport, but stdio is more widely supported and simpler

## R3: Dependency Strategy

**Decision**: Add `mcp` as an optional dependency under `[mcp]` extra

**Rationale**: Not all doit users need MCP server functionality. Making it optional keeps the core CLI lightweight. Users who want MCP install via `pip install doit-toolkit-cli[mcp]`.

**Alternatives considered**:

- Required dependency: Would add ~5MB+ to every install for a feature many won't use
- Separate package (`doit-mcp`): Over-engineering for a single module, harder to maintain

## R4: Tool Response Format

**Decision**: Return structured JSON dicts as MCP text content

**Rationale**: AI assistants parse structured data more effectively than formatted terminal output. Each tool returns a Python dict that gets serialized to JSON by the MCP SDK. This enables AI assistants to extract specific fields, compare values, and present data in their preferred format.

**Alternatives considered**:

- Rich terminal output: Not parseable by AI assistants
- MCP embedded resources: Overly complex for simple data returns
- Markdown formatted strings: Less structured, harder for AI to extract specific values

## R5: Server Architecture

**Decision**: Single `server.py` with per-tool modules in `mcp/tools/`

**Rationale**: Each tool file is a thin wrapper (20-50 lines) that instantiates the appropriate service, calls its methods, and converts results. The server module imports all tools and registers them with FastMCP. This keeps each file focused and independently testable.

**Alternatives considered**:

- All tools in one file: Would become unwieldy as tools grow
- Plugin architecture: Over-engineering for 6 fixed tools
- Service subclass pattern: Unnecessary abstraction when simple functions suffice

## R6: Project Root Detection

**Decision**: Use `Path.cwd()` as default project root in all tools

**Rationale**: MCP servers are spawned by AI assistants in the project's working directory. The AI assistant sets the cwd before launching the server. This matches how the existing CLI commands discover the project root.

**Alternatives considered**:

- Accept project_root as a tool parameter: Adds complexity to every tool call
- Environment variable: Less discoverable, not standard for MCP servers
- Search upward for `.doit/`: Fragile if cwd is in a subdirectory
