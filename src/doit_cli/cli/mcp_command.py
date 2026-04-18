"""MCP server command for exposing doit operations to AI assistants."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="MCP server for AI assistant integration")
console = Console()


@app.command(name="serve")
def serve_command() -> None:
    """Start the doit MCP server (stdio transport).

    The server exposes doit operations as MCP tools that can be called
    by AI assistants like Claude Code and GitHub Copilot.

    Configure in your AI assistant settings:

        {
          "mcpServers": {
            "doit": {
              "command": "doit",
              "args": ["mcp", "serve"]
            }
          }
        }
    """
    from ..mcp import MCP_AVAILABLE

    if not MCP_AVAILABLE:
        console.print(
            "[red]Error: MCP dependencies not installed.[/red]\n"
            "Install with: pip install doit-toolkit-cli[mcp]"
        )
        raise typer.Exit(code=1)

    try:
        from ..mcp.server import create_server

        server = create_server()
        server.run(transport="stdio")
    except ImportError as e:
        console.print(f"[red]Failed to import MCP dependencies: {e}[/red]")
        console.print("Install with: pip install doit-toolkit-cli[mcp]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]MCP server error: {e}[/red]")
        raise typer.Exit(code=1)
