# CLI Conventions

This guide describes the conventions doit commands follow so that new commands
stay consistent with existing ones and so shell pipelines see a uniform
contract.

## Exit codes

Every `typer.Exit(code=…)` call site must use a constant from
[`doit_cli.exit_codes.ExitCode`](../../src/doit_cli/exit_codes.py). Numeric
literals (`raise typer.Exit(code=2)`) obscure intent and make it impossible
to reason about CLI contract compatibility across versions.

| Code | Constant | Use it when |
|-----:|:---------|:-------|
| `0` | `ExitCode.SUCCESS` | Command completed successfully. |
| `1` | `ExitCode.FAILURE` | Generic failure; a condition was false, or an operation didn't complete but the reason doesn't warrant a dedicated code. |
| `2` | `ExitCode.VALIDATION_ERROR` | Input was invalid before any remote call was made (bad args, malformed YAML/JSON, failed spec validation). |
| `3` | `ExitCode.PROVIDER_ERROR` | A remote provider (GitHub, GitLab, Azure DevOps) returned an error or was unreachable. Distinct from `FAILURE` so CI can retry selectively. |
| `4` | `ExitCode.AUTH_ERROR` | Authentication with a provider failed or is missing. |
| `5` | `ExitCode.STATE_ERROR` | Persisted state in `.doit/state/` is corrupt or incompatible. |
| `130` | `ExitCode.USER_CANCEL` | User aborted (Ctrl+C or explicit decline). Matches the SIGINT convention (128 + 2). |

### Example

```python
from doit_cli.exit_codes import ExitCode

if report.blocking_count > 0:
    raise typer.Exit(code=ExitCode.FAILURE)
raise typer.Exit(code=ExitCode.SUCCESS)
```

## `--format / -f` flag

Commands that produce a report accept a `--format / -f` option built via
[`doit_cli.cli.output.format_option`](../../src/doit_cli/cli/output.py).
Using the shared helper gets you:

- Consistent naming (`--format / -f` everywhere)
- A canonical set of values (`OutputFormat` enum)
- Built-in validation against per-command allowed sets
- Case-insensitive parsing

### Supported formats

| Value | Use it for |
|:------|:-----------|
| `rich` | Default; human-readable Rich-styled terminal output |
| `json` | Machine-readable; pipe to `jq`, other doit commands, or CI |
| `markdown` | Markdown suitable for PR bodies or docs |
| `table` | Plain tabular text; stable for downstream tools that don't speak Rich |
| `yaml` | Config-shaped data |
| `csv` | Analytics reports |

Commands pick the subset they support:

```python
from doit_cli.cli.output import OutputFormat, format_option, resolve_format

_MY_FORMATS = (OutputFormat.RICH, OutputFormat.JSON, OutputFormat.MARKDOWN)

def my_command(
    output_format: str = format_option(
        default=OutputFormat.RICH,
        allowed=_MY_FORMATS,
    ),
) -> None:
    fmt = resolve_format(output_format, _MY_FORMATS)
    if fmt is OutputFormat.JSON:
        ...
```

### `--output / -o` flag

Separately from `--format`, use `--output / -o` to accept a file path
for commands that can redirect their report to disk. The two flags are
independent: `--format` picks the rendering, `--output` picks the
destination.

```bash
doit status --format markdown --output report.md
```

## Errors at boundaries

Raise a subclass of [`DoitError`](../../src/doit_cli/errors.py) at every
boundary where a command can fail — validation failures, provider calls,
state reads. Inside `except` blocks, chain the original with
`raise X(...) from e`; ruff B904 fails CI on bare re-raises.

```python
from doit_cli.errors import ProviderError

try:
    client.fetch_epics()
except HTTPError as e:
    raise ProviderError("GitHub epic fetch failed") from e
```

The hierarchy pairs naturally with `ExitCode`: a `ValidationError`
surfaces as `ExitCode.VALIDATION_ERROR`, a `ProviderError` as
`ExitCode.PROVIDER_ERROR`, and so on. Callers in `src/doit_cli/cli/` map
them in one place; service code should raise and let the mapping handle
exit.

## Shared Rich console

Every command uses `rich.console.Console()` at the module level. Keep these
instances module-local rather than creating a new `Console()` inside every
function; Rich re-reads the terminal capabilities on each construction and
that adds noticeable latency on slow terminals.

## Migration status

As of 0.2.0, the infrastructure for these conventions lives in:

- [`src/doit_cli/errors.py`](../../src/doit_cli/errors.py) — `DoitError`
  hierarchy
- [`src/doit_cli/exit_codes.py`](../../src/doit_cli/exit_codes.py) —
  `ExitCode` constants
- [`src/doit_cli/cli/output.py`](../../src/doit_cli/cli/output.py) —
  `format_option()` + `OutputFormat`

`doit status` ([status_command.py](../../src/doit_cli/cli/status_command.py))
and every `doit fixit` subcommand are fully migrated and serve as
reference implementations. Other commands adopt the shared helpers as
they're next edited — adoption is opt-in per call site, so partial
migration is safe.
