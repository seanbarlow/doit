"""Contract: every CLI command uses ExitCode constants, never numeric literals.

Numeric `typer.Exit(code=N)` calls obscure intent and make the CLI
contract hard to reason about across versions. Every new or edited
command must pull codes from `doit_cli.exit_codes.ExitCode` instead.
"""

from __future__ import annotations

import re
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parents[2] / "src" / "doit_cli" / "cli"

# Matches typer.Exit(code=N) or typer.Exit(N) where N is a literal.
# Allows the ternary form: typer.Exit(code=ExitCode.X if cond else ExitCode.Y)
# by anchoring on an integer right after the paren.
NUMERIC_EXIT_PATTERN = re.compile(
    r"typer\.Exit\s*\(\s*(?:code\s*=\s*)?(\d+)\b"
)


def test_no_numeric_typer_exit_in_cli() -> None:
    violations: list[str] = []

    for py in sorted(CLI_DIR.glob("*.py")):
        text = py.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            match = NUMERIC_EXIT_PATTERN.search(line)
            if match:
                violations.append(
                    f"{py.name}:{lineno}: uses numeric exit code "
                    f"{match.group(1)} — use ExitCode.X instead"
                )

    assert not violations, (
        "CLI files must use doit_cli.exit_codes.ExitCode constants:\n"
        + "\n".join(violations)
    )
