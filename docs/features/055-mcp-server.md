# MCP Server for doit Operations

**Completed**: 2026-03-26
**Branch**: `055-mcp-server`
**Epic**: #721

## Overview

Exposes doit CLI operations as an MCP (Model Context Protocol) server, allowing AI assistants like Claude Code and GitHub Copilot to call doit tools directly from the conversation without context-switching to the terminal.

## Key Features

- **MCP tool exposure**: `doit_validate`, `doit_status`, `doit_verify`, and other core operations available as MCP tools
- **FastMCP integration**: Built on the official MCP Python SDK with FastMCP for streamlined server implementation
- **Structured results**: All tool responses return structured data (JSON) for AI consumption
- **Zero config for Claude Code**: Auto-discoverable via `.claude/settings.json` MCP server configuration
- **Spec validation from chat**: Developers can validate specs without leaving the AI conversation
- **Status dashboard access**: Query project status, spec progress, and verification results inline

## Technology

- Python 3.11+ with `mcp` (official MCP Python SDK with FastMCP)
- Typer CLI integration for command dispatch
- Rich output adapted for structured MCP responses

## Related Features

- [Spec Validation and Linting](./029-spec-validation-linting.md)
- [Spec Status Dashboard](./032-status-dashboard.md)
- [AI Context Injection](./026-ai-context-injection.md)
