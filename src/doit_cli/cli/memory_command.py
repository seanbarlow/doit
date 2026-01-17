"""CLI commands for memory search and query functionality.

This module provides the `doit memory` subcommand group for searching
across project context files.
"""

import json
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..models.search_models import QueryType, SourceFilter
from ..services.memory_search import MemorySearchService

# Create the memory app
memory_app = typer.Typer(
    name="memory",
    help="Search and query project memory (constitution, roadmap, specs)",
    add_completion=False,
)

console = Console()


def get_project_root() -> Path:
    """Get the project root directory.

    Walks up from current directory looking for .doit directory.

    Returns:
        Path to project root.

    Raises:
        typer.Exit: If no .doit directory found.
    """
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".doit").is_dir():
            return parent

    console.print(
        "[red]Error:[/red] Not in a doit project. "
        "Run 'doit init' to initialize."
    )
    raise typer.Exit(1)


@memory_app.command(name="search")
def search_command(
    query: str = typer.Argument(
        ...,
        help="Search term, phrase, or natural language question",
    ),
    query_type: str = typer.Option(
        "keyword",
        "--type",
        "-t",
        help="Query type: keyword, phrase, natural, regex",
    ),
    source: str = typer.Option(
        "all",
        "--source",
        "-s",
        help="Source filter: all, governance, specs",
    ),
    max_results: int = typer.Option(
        20,
        "--max",
        "-m",
        help="Maximum results to return (1-100)",
    ),
    case_sensitive: bool = typer.Option(
        False,
        "--case-sensitive",
        "-c",
        help="Enable case-sensitive matching",
    ),
    use_regex: bool = typer.Option(
        False,
        "--regex",
        "-r",
        help="Interpret query as regular expression",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output results as JSON",
    ),
):
    """Search across project memory files.

    Search the constitution, roadmap, and spec files for keywords,
    phrases, or ask natural language questions.

    Examples:
        doit memory search authentication
        doit memory search -t phrase "user story"
        doit memory search -t natural "what is the project vision?"
        doit memory search -s specs "FR-001"
    """
    project_root = get_project_root()

    # Validate and convert query type
    try:
        qt = QueryType(query_type.lower())
    except ValueError:
        console.print(
            f"[red]Error:[/red] Invalid query type '{query_type}'. "
            "Use: keyword, phrase, natural, regex"
        )
        raise typer.Exit(1)

    # If regex flag is set, override query type
    if use_regex:
        qt = QueryType.REGEX

    # Validate and convert source filter
    try:
        sf = SourceFilter(source.lower())
    except ValueError:
        console.print(
            f"[red]Error:[/red] Invalid source filter '{source}'. "
            "Use: all, governance, specs"
        )
        raise typer.Exit(1)

    # Validate max results
    if not 1 <= max_results <= 100:
        console.print(
            "[red]Error:[/red] Max results must be between 1 and 100"
        )
        raise typer.Exit(1)

    # Create service and search
    service = MemorySearchService(project_root, console)

    start_time = time.time()
    try:
        results, sources, search_query = service.search(
            query_text=query,
            query_type=qt,
            source_filter=sf,
            max_results=max_results,
            case_sensitive=case_sensitive,
            use_regex=use_regex,
        )
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(3)

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Output results
    if json_output:
        output = service.format_results_json(
            results, sources, search_query, execution_time_ms
        )
        console.print_json(json.dumps(output, indent=2))
        return

    # Rich output
    if not results:
        console.print("\n[yellow]No results found.[/yellow]")
        console.print(
            f"\nSearched {len(sources)} files in {execution_time_ms}ms"
        )
        return

    # Header
    console.print()
    console.print("[bold]Memory Search Results[/bold]")
    console.print()

    # Show interpretation info for natural language queries
    if qt == QueryType.NATURAL and hasattr(search_query, "_interpreted"):
        interpreted = search_query._interpreted
        console.print(f'Query: "{query}" ({qt.value})')
        console.print(f"  ↳ Type: {interpreted.question_type.value}")
        console.print(f"  ↳ Keywords: {', '.join(interpreted.keywords[:5])}")
        if interpreted.section_hints:
            console.print(f"  ↳ Sections: {', '.join(interpreted.section_hints[:3])}")
        console.print(f"  ↳ Confidence: {interpreted.confidence:.0%}")
    else:
        console.print(f'Query: "{query}" ({qt.value})')

    console.print(
        f"Sources: {sf.value} | Found: {len(results)} results"
    )
    console.print()

    # Display results
    source_map = {s.id: s for s in sources}
    for result in results:
        panel = service.format_result_rich(result, source_map, query)
        console.print(panel)
        console.print()

    # Footer
    console.print(
        f"Searched {len(sources)} files in {execution_time_ms}ms"
    )


@memory_app.command(name="history")
def history_command(
    clear: bool = typer.Option(
        False,
        "--clear",
        "-c",
        help="Clear search history",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output history as JSON",
    ),
):
    """View or clear search history.

    Shows recent searches from the current session.

    Examples:
        doit memory history
        doit memory history --clear
        doit memory history --json
    """
    project_root = get_project_root()
    service = MemorySearchService(project_root, console)

    if clear:
        service.clear_history()
        console.print("[green]Search history cleared.[/green]")
        return

    history = service.get_history()
    entries = history.get_recent(10)

    if json_output:
        output = {
            "session_id": history.session_id,
            "session_start": history.session_start.isoformat(),
            "entries": [
                {
                    "query_text": q.query_text,
                    "query_type": q.query_type.value,
                    "timestamp": q.timestamp.isoformat(),
                }
                for q in entries
            ],
            "total_entries": len(history.entries),
        }
        console.print_json(json.dumps(output, indent=2))
        return

    if not entries:
        console.print("\n[yellow]No search history.[/yellow]")
        console.print(
            "\nRun 'doit memory search <query>' to start searching."
        )
        return

    console.print()
    console.print("[bold]Search History (Session)[/bold]")
    console.print()
    console.print(f"Started: {history.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print()

    # Create table
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", justify="right", width=3)
    table.add_column("Time", width=10)
    table.add_column("Query", width=30)
    table.add_column("Type", width=10)

    for i, entry in enumerate(entries, 1):
        time_str = entry.timestamp.strftime("%H:%M:%S")
        query_display = entry.query_text[:27] + "..." if len(entry.query_text) > 30 else entry.query_text
        table.add_row(
            str(i),
            time_str,
            query_display,
            entry.query_type.value,
        )

    console.print(table)
    console.print()
    console.print(f"{len(history.entries)} queries this session")
