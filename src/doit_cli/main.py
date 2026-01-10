"""Main CLI application for doit-cli new commands (init, verify)."""

import typer

from .cli.init_command import init_command
from .cli.verify_command import verify_command


# Create a new typer app for the refactored commands
app = typer.Typer(
    name="doit",
    help="Doit CLI - Setup tool for Doit spec-driven development projects",
    add_completion=False,
)

# Register commands
app.command(name="init")(init_command)
app.command(name="verify")(verify_command)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
