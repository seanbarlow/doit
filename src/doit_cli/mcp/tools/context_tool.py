"""MCP tool for project context loading."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_context_tool(mcp: FastMCP) -> None:
    """Register the doit_context tool with the MCP server."""

    @mcp.tool()
    def doit_context(sources: Optional[List[str]] = None) -> str:
        """Load project context (constitution, tech stack, roadmap).

        Args:
            sources: Filter to specific sources. Options:
                    constitution, tech_stack, roadmap, completed_roadmap.
                    If omitted, loads all available sources.

        Returns:
            JSON with source contents, token counts, and status.
        """
        from ...services.context_loader import ContextLoader

        project_root = Path.cwd()

        try:
            loader = ContextLoader(project_root=project_root)
        except FileNotFoundError as e:
            return json.dumps({
                "error": str(e),
                "message": "Project memory files not found. Run `doit init` first.",
            }, indent=2)
        except Exception as e:
            logger.error("Unexpected error loading context: %s", e)
            return json.dumps({
                "error": str(e),
                "message": "Failed to load context.",
            }, indent=2)

        loaded = loader.load()
        sources_data = []

        for source in loaded.sources:
            # Filter if sources parameter provided
            if sources and source.source_type not in sources:
                continue
            status = "truncated" if source.truncated else "complete"
            sources_data.append({
                "name": source.source_type,
                "path": str(source.path),
                "content": source.content,
                "tokens": source.token_count,
                "status": status,
            })

        return json.dumps({
            "sources": sources_data,
            "summary": {
                "total_sources": len(sources_data),
                "total_tokens": sum(s["tokens"] for s in sources_data),
            },
        }, indent=2)
