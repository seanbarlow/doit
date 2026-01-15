"""Main CLI application for doit-cli new commands (init, verify)."""

import typer

from .cli.context_command import context_app
from .cli.hooks_command import hooks_app
from .cli.init_command import init_command
from .cli.sync_prompts_command import sync_prompts_command
from .cli.verify_command import verify_command


# Create a new typer app for the refactored commands
app = typer.Typer(
    name="doit",
    help="Doit CLI - Setup tool for Doit spec-driven development projects",
    add_completion=False,
)

# Register commands
app.command(name="init")(init_command)
app.command(name="sync-prompts")(sync_prompts_command)
app.command(name="verify")(verify_command)

# Register subcommand groups
app.add_typer(context_app, name="context")
app.add_typer(hooks_app, name="hooks")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
