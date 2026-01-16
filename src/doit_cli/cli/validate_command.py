"""Validate command for spec file linting and quality checking."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from ..models.validation_models import ValidationConfig
from ..services.report_generator import ReportGenerator
from ..services.validation_service import ValidationService


console = Console()

# Type aliases for CLI options
JsonFlag = Annotated[
    bool,
    typer.Option(
        "--json", "-j",
        help="Output results as JSON"
    )
]

AllFlag = Annotated[
    bool,
    typer.Option(
        "--all", "-a",
        help="Validate all specs in specs/ directory"
    )
]

VerboseFlag = Annotated[
    bool,
    typer.Option(
        "--verbose", "-v",
        help="Show detailed output including all issues"
    )
]


def validate_command(
    path: Annotated[
        Optional[Path],
        typer.Argument(
            help="Spec file or directory to validate (defaults to current directory)"
        )
    ] = None,
    all_specs: AllFlag = False,
    json_output: JsonFlag = False,
    verbose: VerboseFlag = False,
) -> None:
    """Validate spec files for quality and standards compliance.

    Checks spec files against validation rules including:
    - Required sections (User Scenarios, Requirements, Success Criteria)
    - Naming conventions (FR-XXX, SC-XXX patterns)
    - Acceptance scenario format (Given/When/Then)
    - Clarity markers ([NEEDS CLARIFICATION], TODO)

    Custom rules can be configured via .doit/validation-rules.yaml:
    - disabled_rules: List of rule IDs to skip
    - overrides: Change severity of specific rules
    - custom_rules: Add project-specific pattern checks

    Examples:
        doit validate                        # Validate current spec
        doit validate specs/001-feature/     # Validate specific spec directory
        doit validate spec.md                # Validate specific file
        doit validate --all                  # Validate all specs
        doit validate --all --json           # Output as JSON
    """
    # Resolve path
    project_root = Path.cwd()

    if path:
        target_path = path if path.is_absolute() else project_root / path
    else:
        target_path = project_root

    # Create services
    config = ValidationConfig.default()
    service = ValidationService(project_root=project_root, config=config)
    reporter = ReportGenerator(console=console)

    try:
        if all_specs:
            # Validate all specs in specs/ directory
            results = service.validate_all()

            if not results:
                if json_output:
                    print('{"error": "No spec files found in specs/ directory"}')
                else:
                    console.print("[yellow]No spec files found in specs/ directory[/yellow]")
                raise typer.Exit(1)

            summary = service.get_summary(results)

            if json_output:
                print(reporter.to_json_summary(results, summary))
            else:
                if verbose:
                    # Show each result in detail
                    for result in results:
                        reporter.display_result(result)
                        console.print()

                # Always show summary for --all
                reporter.display_summary(results, summary)

            # Exit with error if any specs failed
            if summary["failed"] > 0:
                raise typer.Exit(1)

        elif target_path.is_file():
            # Validate single file
            if not target_path.suffix.lower() == ".md":
                if json_output:
                    print('{"error": "Not a markdown file"}')
                else:
                    console.print(f"[red]Error:[/red] Not a markdown file: {target_path}")
                raise typer.Exit(1)

            result = service.validate_file(target_path)

            if json_output:
                print(reporter.to_json(result))
            else:
                reporter.display_result(result)

            # Exit with error if validation failed
            if result.error_count > 0:
                raise typer.Exit(1)

        elif target_path.is_dir():
            # Check if this is a spec directory (contains spec.md)
            spec_file = target_path / "spec.md"

            if spec_file.exists():
                # Validate single spec directory
                result = service.validate_file(spec_file)

                if json_output:
                    print(reporter.to_json(result))
                else:
                    reporter.display_result(result)

                if result.error_count > 0:
                    raise typer.Exit(1)
            else:
                # Validate all specs in the directory
                results = service.validate_directory(target_path)

                if not results:
                    if json_output:
                        print('{"error": "No spec files found in directory"}')
                    else:
                        console.print(f"[yellow]No spec files found in {target_path}[/yellow]")
                    raise typer.Exit(1)

                summary = service.get_summary(results)

                if json_output:
                    print(reporter.to_json_summary(results, summary))
                else:
                    if verbose:
                        for result in results:
                            reporter.display_result(result)
                            console.print()

                    reporter.display_summary(results, summary)

                if summary["failed"] > 0:
                    raise typer.Exit(1)

        else:
            if json_output:
                print(f'{{"error": "Path not found: {target_path}"}}')
            else:
                console.print(f"[red]Error:[/red] Path not found: {target_path}")
            raise typer.Exit(1)

    except FileNotFoundError as e:
        if json_output:
            print(f'{{"error": "{e}"}}')
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    except ValueError as e:
        if json_output:
            print(f'{{"error": "{e}"}}')
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
