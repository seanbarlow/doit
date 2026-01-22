"""Main CLI application for doit-cli new commands (init, verify)."""

import typer

from .cli.analytics_command import app as analytics_app
from .cli.constitution_command import app as constitution_app
from .cli.context_command import context_app
from .cli.diagram_command import diagram_app
from .cli.fixit_command import app as fixit_app
from .cli.hooks_command import hooks_app
from .cli.init_command import init_command
from .cli.memory_command import memory_app
from .cli.provider_command import app as provider_app
from .cli.roadmapit_command import app as roadmapit_app
from .cli.status_command import status_command
from .cli.sync_prompts_command import sync_prompts_command
from .cli.team_command import app as team_app
from .cli.validate_command import validate_command
from .cli.verify_command import verify_command
from .cli.xref_command import xref_app


# Create a new typer app for the refactored commands
app = typer.Typer(
    name="doit",
    help="Doit CLI - Setup tool for Doit spec-driven development projects",
    add_completion=False,
)

# Register commands
app.command(name="init")(init_command)
app.command(name="status")(status_command)
app.command(name="sync-prompts")(sync_prompts_command)
app.command(name="validate")(validate_command)
app.command(name="verify")(verify_command)

# Register subcommand groups
app.add_typer(analytics_app, name="analytics")
app.add_typer(constitution_app, name="constitution")
app.add_typer(context_app, name="context")
app.add_typer(diagram_app, name="diagram")
app.add_typer(fixit_app, name="fixit")
app.add_typer(hooks_app, name="hooks")
app.add_typer(memory_app, name="memory")
app.add_typer(provider_app, name="provider")
app.add_typer(roadmapit_app, name="roadmapit")
app.add_typer(team_app, name="team")
app.add_typer(xref_app, name="xref")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
