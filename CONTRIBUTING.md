# Contributing to Do-It

Thank you for considering contributing to Do-It! We appreciate your interest in making this project better. This document provides guidelines and instructions for contributing.

## Our Values

- **Specification First** - Everything starts with clear specifications
- **Quality Over Speed** - Well-tested code matters more than fast code
- **Team Collaboration** - We believe in inclusive decision-making
- **Documentation** - Clear docs are as important as clear code
- **Accessibility** - Our tools should work for everyone

## Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/seanbarlow/doit.git
cd doit
# You'll be on the 'develop' branch by default
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### 3. Create a Feature Branch

We use numbered feature branches for tracking:

```bash
git checkout -b ###-feature-name develop
```

Branch naming convention:

- `###-feature-name` - Numbered feature branches (e.g., `017-roadmap-template-cleanup`)
- Numbers are sequential and help track features in the project

## Development Workflow

### Using Do-It Commands (Spec-Driven Development)

This project uses spec-driven development with the `/doit.*` slash commands in Claude Code:

1. **`/doit.specit`** - Create a feature specification from a description
2. **`/doit.planit`** - Generate an implementation plan from the spec
3. **`/doit.taskit`** - Create actionable tasks from the plan
4. **`/doit.implementit`** - Execute the implementation tasks
5. **`/doit.reviewit`** - Review the implementation against requirements
6. **`/doit.checkin`** - Finalize the feature, close issues, create PR

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_example.py

# Run specific test
pytest tests/unit/test_example.py::test_function_name
```

### Code Quality

We recommend using `ruff` for linting and formatting:

```bash
# Install ruff
pip install ruff

# Check code style
ruff check src/

# Format code
ruff format src/
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

### Examples

```
feat(specit): add support for state machines in diagrams

fix(roadmapit): prevent duplicate items when deferring

docs(architecture): clarify memory system behavior

test(documentit): add coverage for cleanup command

refactor(core): extract common diagram logic
```

### Types

- **feat** - A new feature
- **fix** - A bug fix
- **docs** - Documentation changes
- **style** - Code style changes (formatting, etc.)
- **refactor** - Code refactoring without feature changes
- **perf** - Performance improvements
- **test** - Adding or updating tests
- **chore** - Build process, dependencies, tooling

### Co-Author Attribution

When working with AI assistants, include co-author attribution:

```
feat(feature): description

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Testing Requirements

All contributions should include tests when applicable:

```python
# tests/unit/test_example.py
import pytest
from doit_cli.example import example_function

def test_example_basic():
    """Test basic functionality."""
    result = example_function("input")
    assert result is not None
```

**Guidelines:**

- Add tests for new functionality
- Maintain or improve existing coverage
- Critical paths should have thorough test coverage

## Documentation

### Code Documentation

We use Google-style docstrings:

```python
def example_function(param: str) -> dict:
    """Brief description of the function.

    Args:
        param: Description of the parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param is invalid
    """
```

### Comments

```python
# For complex logic, explain the WHY, not the WHAT
# Example: We cache this result because the operation is expensive
# and the data rarely changes during a session
cached_result = expensive_operation()
```

## Bug Reports

Found a bug? Please report it!

### Before Reporting

1. Check [existing issues](https://github.com/seanbarlow/doit/issues)
2. Test with the latest version
3. Verify it's a Do-It bug, not a configuration issue

### When Reporting

Include:

```
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command: `doit init`
2. Observe: ...
3. Expected: ...

**Environment**
- Do-It version: `doit --version`
- Python version: `python --version`
- OS: Windows/Mac/Linux
- Shell: bash/zsh/powershell

**Additional context**
Any other context about the problem.
```

## Feature Requests

Have an idea for a new feature?

### Before Requesting

1. Check [existing issues](https://github.com/seanbarlow/doit/issues)
2. Review the project roadmap in `.doit/memory/roadmap.md`
3. Consider the scope and maintenance burden

### When Requesting

```
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
How should it work?

**Describe alternatives you've considered**
Other possible approaches.

**Why should Do-It have this feature?**
Who benefits? What problems does it solve?
```

## Code Review Process

1. **Automated Checks** - CI runs tests
2. **Peer Review** - At least one maintainer reviews code
3. **Feedback** - Changes requested or approved
4. **Merge** - Approved PRs are merged to main

### What We Look For

- Tests included and passing
- Documentation updated (if applicable)
- Code follows project conventions
- Commit messages are clear
- No breaking changes (or justified)

## Pull Request Process

1. **Create Branch** - From latest `develop` using numbered convention
2. **Make Changes** - Include tests where applicable
3. **Run Tests** - `pytest` passes locally
4. **Commit** - Follow conventional commits
5. **Push** - To your fork
6. **Create PR** - Include description of changes
7. **Address Review** - Respond to feedback
8. **Merge** - Maintainer merges when approved

### PR Template

```markdown
## Summary
Brief description of changes.

## Changes
- Change 1
- Change 2

## Testing
- [ ] Tests added/updated
- [ ] All tests pass

## Related Issues
Closes #123
```

## Release Process (Maintainers)

This project uses a two-branch workflow:

- **`develop`** - Default branch for feature integration
- **`main`** - Production-ready releases only

### Releasing to Production

1. Ensure all desired features are merged to `develop`
2. Create a PR from `develop` to `main`:

   ```bash
   gh pr create --base main --head develop --title "Release vX.Y.Z"
   ```

3. Review and merge the PR
4. Tag the release:

   ```bash
   git checkout main
   git pull origin main
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

### Hotfix Process

For urgent production fixes:

1. Branch from `main`: `git checkout -b hotfix-description main`
2. Make the fix and create PR to `main`
3. After merging to `main`, also merge or cherry-pick to `develop`

## Project Structure

```
doit/
├── src/doit_cli/       # Main package source
├── tests/              # Test files
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── templates/          # Template files for doit init
├── .doit/              # Do-It configuration and templates
│   ├── memory/         # Project memory (roadmap, constitution)
│   ├── templates/      # Reference templates
│   └── scripts/        # Helper scripts
├── docs/               # Documentation
│   └── features/       # Feature documentation
└── specs/              # Feature specifications (gitignored)
```

## Priority Areas for Contributions

Looking for where to start?

### Good for First-Time Contributors

- Documentation improvements
- Test coverage expansion
- Bug fixes with clear reproduction steps
- Template improvements

### Higher Priority

- New `/doit.*` command enhancements
- Better error messages
- Cross-platform compatibility (Windows)

## Getting Help

- **Questions & Issues** - [GitHub Issues](https://github.com/seanbarlow/doit/issues)
- **Discussions** - [GitHub Discussions](https://github.com/seanbarlow/doit/discussions)

## Code of Conduct

This project is committed to creating an inclusive, welcoming environment. See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the same MIT license as the project.

---

**Thank you for contributing to Do-It!**
