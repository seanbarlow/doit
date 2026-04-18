"""doit-toolkit-cli package.

The CLI entry point is `doit_cli.main:main` (registered as `doit` in
`pyproject.toml`'s `[project.scripts]`). Historically this module held a
second Typer app and a large body of legacy helpers; those were
superseded by `doit_cli.cli.*` and `doit_cli.services.*` during the
April 2026 modernization and have been removed.

If you're looking for the code that used to live here:

- Commands are now in `doit_cli.cli.<name>_command`.
- Scaffolding logic lives in `doit_cli.services.scaffolder`.
- Interactive prompts and progress display live in `doit_cli.prompts`.
- GitHub-CLI and template-download helpers live in `doit_cli.utils`.

The only public symbol this module is guaranteed to expose is
`__version__`, sourced from installed package metadata.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("doit-toolkit-cli")
except PackageNotFoundError:  # pragma: no cover - editable install in a fresh checkout
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
