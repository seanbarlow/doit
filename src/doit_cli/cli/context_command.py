"""CLI commands for AI context management."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..models.context_config import ContextConfig
from ..services.context_loader import ContextLoader

console = Console()

# Create the context command group
context_app = typer.Typer(
    name="context",
    help="Manage AI context injection for doit commands.",
    no_args_is_help=True,
)


@context_app.command("show")
def show_context(
    command: str = typer.Option(
        None, "--command", "-c", help="Show context for specific command (applies overrides)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show full content of each source"
    ),
) -> None:
    """Show what context would be loaded for commands."""
    project_root = Path.cwd()

    # Load configuration
    config = ContextConfig.load_from_project(project_root)

    console.print("[bold]AI Context Status[/bold]")
    console.print("=" * 50)

    # Show global status
    if not config.enabled:
        console.print("\n[yellow]Context loading is disabled globally.[/yellow]")
        console.print("Enable in .doit/config/context.yaml by setting 'enabled: true'")
        return

    console.print(f"\n[bold]Global Settings:[/bold]")
    console.print(f"  Enabled: [green]yes[/green]")
    console.print(f"  Max tokens per source: {config.max_tokens_per_source:,}")
    console.print(f"  Total max tokens: {config.total_max_tokens:,}")

    # Show summarization settings
    if config.summarization.enabled:
        soft_threshold = int(config.total_max_tokens * (config.summarization.threshold_percentage / 100.0))
        console.print(f"\n[bold]Summarization:[/bold]")
        console.print(f"  Enabled: [green]yes[/green]")
        console.print(f"  Soft threshold: {soft_threshold:,} tokens ({config.summarization.threshold_percentage}%)")
        console.print(f"  Fallback to truncation: {'yes' if config.summarization.fallback_to_truncation else 'no'}")

    # Load context
    loader = ContextLoader(
        project_root=project_root,
        config=config,
        command=command,
    )

    try:
        context = loader.load()
    except Exception as e:
        console.print(f"\n[red]Error loading context: {e}[/red]")
        raise typer.Exit(1)

    # Show command-specific info
    if command:
        console.print(f"\n[bold]Context for command:[/bold] {command}")
        if command in config.commands:
            console.print("  [dim]Command-specific overrides applied[/dim]")

    # Create source table
    console.print(f"\n[bold]Loaded Sources:[/bold]")

    if not context.sources:
        console.print("  [dim]No sources loaded[/dim]")
        console.print("\n[dim]Check that .doit/memory/ contains constitution.md or roadmap.md[/dim]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Source", style="cyan")
    table.add_column("Path", style="dim")
    table.add_column("Tokens", justify="right")
    table.add_column("Status")

    for source in context.sources:
        # Truncate path for display
        path_str = str(source.path)
        if len(path_str) > 40:
            path_str = "..." + path_str[-37:]

        # Status indicator
        if source.truncated:
            status = f"[yellow]truncated ({source.original_tokens:,} -> {source.token_count:,})[/yellow]"
        elif source.source_type == "roadmap" and config.summarization.enabled:
            status = "[cyan]summarized[/cyan]"
        elif source.source_type == "completed_roadmap":
            status = "[cyan]formatted[/cyan]"
        else:
            status = "[green]complete[/green]"

        table.add_row(
            source.source_type,
            path_str,
            f"{source.token_count:,}",
            status,
        )

    console.print(table)

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total sources: {len(context.sources)}")
    console.print(f"  Total tokens: {context.total_tokens:,}")

    if context.any_truncated:
        console.print("  [yellow]Some sources were truncated to fit token limits[/yellow]")

    # Check for guidance prompt (indicates context was condensed)
    if hasattr(context, '_guidance_prompt') and context._guidance_prompt:
        console.print("  [cyan]AI guidance prompt included (context condensed)[/cyan]")

    # Show verbose content
    if verbose:
        console.print(f"\n[bold]Source Content Preview:[/bold]")
        for source in context.sources:
            console.print(f"\n[cyan]--- {source.source_type} ---[/cyan]")
            # Show first 500 chars
            preview = source.content[:500]
            if len(source.content) > 500:
                preview += "\n... [truncated for display]"
            console.print(preview)


@context_app.command("status")
def context_status() -> None:
    """Show context configuration and file availability."""
    project_root = Path.cwd()

    console.print("[bold]Context Configuration Status[/bold]")
    console.print("=" * 50)

    # Check config file
    config_path = project_root / ".doit" / "config" / "context.yaml"
    console.print(f"\n[bold]Configuration:[/bold]")

    if config_path.exists():
        console.print(f"  [green]\u2713[/green] Config file: {config_path}")
        config = ContextConfig.load_from_project(project_root)
    else:
        console.print(f"  [dim]\u2717[/dim] Config file: {config_path} [dim](using defaults)[/dim]")
        config = ContextConfig.load_default()

    # Show source availability
    console.print(f"\n[bold]Source Files:[/bold]")

    memory_dir = project_root / ".doit" / "memory"
    specs_dir = project_root / "specs"

    sources = [
        ("constitution", memory_dir / "constitution.md"),
        ("roadmap", memory_dir / "roadmap.md"),
        ("completed_roadmap", memory_dir / "completed_roadmap.md"),
    ]

    for name, path in sources:
        source_config = config.get_source_config(name)
        enabled = source_config.enabled if source_config else True

        if path.exists():
            if enabled:
                console.print(f"  [green]\u2713[/green] {name}: {path}")
            else:
                console.print(f"  [yellow]\u2713[/yellow] {name}: {path} [dim](disabled)[/dim]")
        else:
            console.print(f"  [dim]\u2717[/dim] {name}: {path} [dim](not found)[/dim]")

    # Check specs directory
    if specs_dir.exists():
        spec_count = len(list(specs_dir.glob("*/")))
        console.print(f"  [green]\u2713[/green] specs directory: {spec_count} feature(s)")
    else:
        console.print(f"  [dim]\u2717[/dim] specs directory: [dim](not found)[/dim]")

    # Show current branch info
    console.print(f"\n[bold]Git Branch:[/bold]")
    loader = ContextLoader(project_root=project_root, config=config)
    branch = loader.get_current_branch()

    if branch:
        console.print(f"  Current: {branch}")
        feature = loader.extract_feature_name(branch)
        if feature:
            console.print(f"  Feature: {feature}")
            spec_path = specs_dir / feature
            if spec_path.exists():
                console.print(f"  [green]\u2713[/green] Current spec: {spec_path}")
            else:
                console.print(f"  [dim]\u2717[/dim] Current spec: [dim](no matching spec)[/dim]")
        else:
            console.print(f"  [dim]Not a feature branch (pattern: NNN-feature-name)[/dim]")
    else:
        console.print(f"  [dim]Not in a git repository or git not available[/dim]")

    # Usage hints
    console.print(f"\n[dim]Use 'doit context show' to see loaded context[/dim]")
    console.print(f"[dim]Use 'doit context show --command specit' to see command-specific context[/dim]")


@context_app.command("audit")
def audit_context(
    templates_dir: Path = typer.Option(
        None,
        "--templates-dir",
        "-d",
        help="Directory containing command templates (default: templates/commands/)",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, or markdown",
    ),
    output_file: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Write report to file instead of stdout",
    ),
    severity: str = typer.Option(
        None,
        "--severity",
        "-s",
        help="Filter findings by severity: critical, major, minor",
    ),
) -> None:
    """Audit templates for context injection issues like double-injection patterns."""
    from ..services.context_auditor import ContextAuditor

    # Validate format option
    valid_formats = ["table", "json", "markdown"]
    if output_format not in valid_formats:
        console.print(f"[red]Invalid format '{output_format}'. Use one of: {', '.join(valid_formats)}[/red]")
        raise typer.Exit(1)

    # Validate severity option
    valid_severities = ["critical", "major", "minor"]
    if severity and severity not in valid_severities:
        console.print(f"[red]Invalid severity '{severity}'. Use one of: {', '.join(valid_severities)}[/red]")
        raise typer.Exit(1)

    # Create auditor
    auditor = ContextAuditor(templates_dir=templates_dir)

    if not auditor.templates_dir.exists():
        console.print(f"[red]Templates directory not found: {auditor.templates_dir}[/red]")
        console.print("[dim]Run this command from the repository root or specify --templates-dir[/dim]")
        raise typer.Exit(1)

    console.print(f"[bold]Auditing templates in:[/bold] {auditor.templates_dir}")
    console.print("")

    # Run audit
    report = auditor.audit_all_templates()

    # Filter by severity if requested
    if severity:
        report.findings = [f for f in report.findings if f.severity == severity]
        report.total_findings = len(report.findings)

    # Format report
    formatted = auditor.format_report(report, output_format)

    # Output
    if output_file:
        output_file.write_text(formatted, encoding="utf-8")
        console.print(f"[green]Report written to: {output_file}[/green]")
    else:
        console.print(formatted)

    # Summary with color-coded status
    if report.double_injection_count > 0:
        console.print(f"\n[yellow]⚠ Found {report.double_injection_count} templates with double-injection patterns[/yellow]")
        console.print(f"[dim]Estimated token waste: ~{report.token_waste_estimate:,} tokens[/dim]")
    else:
        console.print(f"\n[green]✓ No double-injection patterns found[/green]")

    if report.total_findings > 0:
        console.print(f"\n[dim]Total findings: {report.total_findings}[/dim]")
        raise typer.Exit(1)
    else:
        console.print(f"[green]✓ All templates pass audit[/green]")
