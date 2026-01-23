# Do-It Tech Stack

> **See also**: [Constitution](constitution.md) for project principles and governance.

## Tech Stack

### Languages

Python 3.11+ (primary)

### Frameworks

- Typer (CLI framework)
- pytest (testing framework)
- Hatchling (build system)

### Libraries

- Rich (terminal formatting and output)
- httpx (HTTP client with SOCKS support)
- platformdirs (cross-platform directories)
- readchar (keyboard input)
- truststore (certificate handling)

## Infrastructure

### Hosting

PyPI (Python Package Index) - distributed as `doit-toolkit-cli`

### Cloud Provider

None (local CLI tool, no cloud infrastructure required)

### Database

None (file-based storage using markdown in `.doit/memory/`)

## Deployment

### CI/CD Pipeline

GitHub Actions

### Deployment Strategy

Manual release to PyPI via `hatch build` and `hatch publish`

### Environments

- Development (local)
- Production (PyPI)
