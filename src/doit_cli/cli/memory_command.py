"""CLI commands for memory search and query functionality.

This module provides the `doit memory` subcommand group for searching
across project context files.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..exit_codes import ExitCode
from ..models.search_models import QueryType, SourceFilter
from ..services.memory_search import MemorySearchService

# Create the memory app
memory_app = typer.Typer(
    name="memory",
    help=(
        "Project memory commands: search the memory files, enrich "
        "placeholder stubs, and run shape migrations. "
        "Subcommands: `search`, `history`, `schema`, `enrich <file>`, "
        "`migrate`."
    ),
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
    for parent in [current, *list(current.parents)]:
        if (parent / ".doit").is_dir():
            return parent

    console.print("[red]Error:[/red] Not in a doit project. Run 'doit init' to initialize.")
    raise typer.Exit(code=ExitCode.FAILURE)


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
        raise typer.Exit(code=ExitCode.FAILURE) from None

    # If regex flag is set, override query type
    if use_regex:
        qt = QueryType.REGEX

    # Validate and convert source filter
    try:
        sf = SourceFilter(source.lower())
    except ValueError:
        console.print(
            f"[red]Error:[/red] Invalid source filter '{source}'. Use: all, governance, specs"
        )
        raise typer.Exit(code=ExitCode.FAILURE) from None

    # Validate max results
    if not 1 <= max_results <= 100:
        console.print("[red]Error:[/red] Max results must be between 1 and 100")
        raise typer.Exit(code=ExitCode.FAILURE)

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
        raise typer.Exit(code=ExitCode.PROVIDER_ERROR) from e

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Output results
    if json_output:
        output = service.format_results_json(results, sources, search_query, execution_time_ms)
        console.print_json(json.dumps(output, indent=2))
        return

    # Rich output
    if not results:
        console.print("\n[yellow]No results found.[/yellow]")
        console.print(f"\nSearched {len(sources)} files in {execution_time_ms}ms")
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

    console.print(f"Sources: {sf.value} | Found: {len(results)} results")
    console.print()

    # Display results
    source_map = {s.id: s for s in sources}
    for result in results:
        panel = service.format_result_rich(result, source_map, query)
        console.print(panel)
        console.print()

    # Footer
    console.print(f"Searched {len(sources)} files in {execution_time_ms}ms")


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
        console.print("\nRun 'doit memory search <query>' to start searching.")
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
        query_display = (
            entry.query_text[:27] + "..." if len(entry.query_text) > 30 else entry.query_text
        )
        table.add_row(
            str(i),
            time_str,
            query_display,
            entry.query_type.value,
        )

    console.print(table)
    console.print()
    console.print(f"{len(history.entries)} queries this session")


# ---------------------------------------------------------------------------
# `doit memory schema` — expose the JSON Schema for constitution frontmatter
#
# Downstream generators (e.g. platform-docs-site/tools/gen-data) can consume
# this instead of hand-maintaining a second copy of the schema.
# ---------------------------------------------------------------------------


@memory_app.command(name="schema")
def schema_command(
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Print the schema without surrounding formatting (machine-readable).",
    ),
) -> None:
    """Print the JSON Schema for constitution.md frontmatter."""
    from importlib.resources import files

    try:
        schema_bytes = (
            files("doit_cli").joinpath("schemas/frontmatter.schema.json").read_bytes()
        )
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] schema file missing — "
            "run `pip install --upgrade doit-toolkit-cli`.",
        )
        raise typer.Exit(code=ExitCode.FAILURE)

    schema = json.loads(schema_bytes)
    if raw:
        # typer.echo avoids Rich's automatic word wrap so the stdout is
        # byte-for-byte the canonical schema.
        typer.echo(json.dumps(schema, indent=2))
    else:
        console.print_json(json.dumps(schema))


# ---------------------------------------------------------------------------
# Spec 060: `doit memory enrich <file>` and `doit memory migrate`.

enrich_app = typer.Typer(
    name="enrich",
    help="Deterministic enrichment of placeholder-stubbed memory files.",
    add_completion=False,
)
memory_app.add_typer(enrich_app, name="enrich")


def _emit_enrichment_result(result: object, json_output: bool) -> None:
    from ..services.constitution_enricher import EnrichmentAction, EnrichmentResult

    assert isinstance(result, EnrichmentResult)
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "path": str(result.path),
                    "action": result.action.value,
                    "enriched_fields": list(result.enriched_fields),
                    "unresolved_fields": list(result.unresolved_fields),
                    "error": str(result.error) if result.error else None,
                },
                indent=2,
            )
        )
    else:
        if result.action is EnrichmentAction.NO_OP:
            console.print(
                "[green]Nothing to enrich[/green] — no placeholders detected."
            )
        elif result.action is EnrichmentAction.ERROR:
            console.print(f"[red]Enrichment failed:[/red] {result.error}")
        else:
            table = Table(
                show_header=True,
                header_style="bold cyan",
                title=f"Enrichment: {result.path}",
            )
            table.add_column("Status", width=12)
            table.add_column("Field", width=16)
            for key in result.enriched_fields:
                table.add_row("[green]✓ filled[/green]", key)
            for key in result.unresolved_fields:
                table.add_row("[yellow]! unresolved[/yellow]", key)
            console.print(table)
            if result.unresolved_fields:
                console.print(
                    "[yellow]Unresolved:[/yellow] "
                    + ", ".join(result.unresolved_fields)
                )


@enrich_app.command("tech-stack")
def enrich_tech_stack_cmd(
    path: Path | None = typer.Argument(
        None,
        help="Project root directory (default: current directory)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Emit the enrichment result as JSON",
    ),
) -> None:
    """Populate placeholder-stubbed tech-stack.md subsections from the constitution.

    Exit codes: 0 = ENRICHED or NO_OP; 1 = PARTIAL (some fields unresolved);
    2 = VALIDATION / file error.
    """

    from ..services.constitution_enricher import EnrichmentAction
    from ..services.tech_stack_enricher import enrich_tech_stack

    project_root = path or Path.cwd()
    target = project_root / ".doit" / "memory" / "tech-stack.md"
    result = enrich_tech_stack(target, project_root=project_root)
    _emit_enrichment_result(result, json_output)

    if result.action is EnrichmentAction.ERROR:
        raise typer.Exit(code=ExitCode.VALIDATION_ERROR)
    if result.action is EnrichmentAction.PARTIAL:
        raise typer.Exit(code=ExitCode.FAILURE)


@enrich_app.command("roadmap")
def enrich_roadmap_cmd(
    path: Path | None = typer.Argument(
        None,
        help="Project root directory (default: current directory)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Emit the enrichment result as JSON",
    ),
) -> None:
    """Seed roadmap.md Vision + completed-items hint from other memory files.

    Vision is replaced from the constitution's Project Purpose; completed items
    are extracted from `.doit/memory/completed_roadmap.md`. Priority subsections
    (P1/P2/P3/P4) are intentionally left alone — that's product judgment.

    Exit codes: 0 = ENRICHED or NO_OP; 1 = PARTIAL; 2 = VALIDATION / file error.
    """

    from ..services.constitution_enricher import EnrichmentAction
    from ..services.roadmap_enricher import enrich_roadmap

    project_root = path or Path.cwd()
    target = project_root / ".doit" / "memory" / "roadmap.md"
    result = enrich_roadmap(target, project_root=project_root)
    _emit_enrichment_result(result, json_output)

    if result.action is EnrichmentAction.ERROR:
        raise typer.Exit(code=ExitCode.VALIDATION_ERROR)
    if result.action is EnrichmentAction.PARTIAL:
        raise typer.Exit(code=ExitCode.FAILURE)


@enrich_app.command("personas")
def enrich_personas_cmd(
    path: Path | None = typer.Argument(
        None,
        help="Project root directory (default: current directory)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Emit the enrichment result as JSON",
    ),
) -> None:
    """Report placeholder state in .doit/memory/personas.md (linter mode).

    Unlike the other enrichers, this one NEVER modifies the file — persona
    content (names, roles, goals) is intrinsically project-specific and
    belongs to `/doit.roadmapit` or `/doit.researchit`. When placeholders
    remain, the CLI exits 1 with a hint pointing at those skills.

    Exit codes: 0 = NO_OP (no file or no placeholders); 1 = PARTIAL
    (placeholders remain); 2 = VALIDATION / file error.
    """

    from ..services.constitution_enricher import EnrichmentAction
    from ..services.personas_enricher import enrich_personas

    project_root = path or Path.cwd()
    target = project_root / ".doit" / "memory" / "personas.md"
    result = enrich_personas(target)
    _emit_enrichment_result(result, json_output)

    if result.action is EnrichmentAction.ERROR:
        raise typer.Exit(code=ExitCode.VALIDATION_ERROR)
    if result.action is EnrichmentAction.PARTIAL:
        # Personas-specific remediation hint (linter mode — no auto-fill).
        if not json_output:
            console.print(
                "[dim]Run [cyan]/doit.roadmapit[/cyan] or "
                "[cyan]/doit.researchit[/cyan] to populate personas "
                "interactively.[/dim]"
            )
        raise typer.Exit(code=ExitCode.FAILURE)


@memory_app.command("migrate")
def migrate_memory_cmd(
    path: Path | None = typer.Argument(
        None,
        help="Project root directory (default: current directory)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Emit the migration results as JSON",
    ),
) -> None:
    """Run constitution + roadmap + tech-stack + personas migrators in sequence.

    Equivalent to the memory-shape migration block that `doit update` runs
    internally. In normal workflows `doit update` handles this automatically;
    run `doit memory migrate` directly when you want to:

    - **Diagnose**: see a per-file migration report without `doit init --update`
      touching command templates, scripts, or hooks.
    - **Re-run**: apply migration without re-copying memory templates.
    - **Audit in CI**: `--json` emits a machine-readable summary.

    Exits with the first non-zero code any migrator produced
    (`VALIDATION_ERROR` for validation failures, `FAILURE` for other
    errors). Atomic per file: a failing migrator leaves its target file
    byte-identical to its pre-run state.
    """

    from ..errors import DoitValidationError
    from ..services.constitution_migrator import (
        MigrationAction,
        migrate_constitution,
    )
    from ..services.personas_migrator import migrate_personas
    from ..services.roadmap_migrator import migrate_roadmap
    from ..services.tech_stack_migrator import migrate_tech_stack

    project_root = path or Path.cwd()
    memory_dir = project_root / ".doit" / "memory"

    steps = (
        ("constitution.md", migrate_constitution),
        ("roadmap.md", migrate_roadmap),
        ("tech-stack.md", migrate_tech_stack),
        ("personas.md", migrate_personas),
    )

    results = []
    first_error_code: int | None = None
    for filename, migrator in steps:
        mig = migrator(memory_dir / filename)
        results.append((filename, mig))
        if mig.action is MigrationAction.ERROR and mig.error is not None:
            first_error_code = (
                ExitCode.VALIDATION_ERROR
                if isinstance(mig.error, DoitValidationError)
                else ExitCode.FAILURE
            )
            break

    if json_output:
        payload = [
            {
                "path": str(r.path),
                "file": filename,
                "action": r.action.value,
                "added_fields": list(r.added_fields),
                "error": str(r.error) if r.error else None,
            }
            for filename, r in results
        ]
        typer.echo(json.dumps(payload, indent=2))
    else:
        table = Table(
            show_header=True,
            header_style="bold cyan",
            title="Memory migration",
        )
        table.add_column("File", width=20)
        table.add_column("Action", width=12)
        table.add_column("Details")
        for filename, r in results:
            if r.action is MigrationAction.NO_OP:
                status, detail = "[dim]no-op[/dim]", "already valid-shape"
            elif r.action is MigrationAction.PREPENDED:
                status, detail = (
                    "[yellow]prepended[/yellow]",
                    f"added: {', '.join(r.added_fields)}",
                )
            elif r.action is MigrationAction.PATCHED:
                status, detail = (
                    "[yellow]patched[/yellow]",
                    f"added: {', '.join(r.added_fields)}",
                )
            else:
                status, detail = "[red]error[/red]", str(r.error or "")
            table.add_row(filename, status, detail)
        console.print(table)

    if first_error_code is not None:
        raise typer.Exit(code=first_error_code)
