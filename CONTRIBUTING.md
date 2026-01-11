# Contributing to DoIt

Thank you for considering contributing to DoIt! We appreciate your interest in making this project better. This document provides guidelines and instructions for contributing.

## 🎯 Our Values

- **Specification First** - Everything starts with clear specifications
- **Quality Over Speed** - Well-tested code matters more than fast code
- **Team Collaboration** - We believe in inclusive decision-making
- **Documentation** - Clear docs are as important as clear code
- **Accessibility** - Our tools should work for everyone

## 🚀 Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/doit.git
cd doit
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Follow our branch naming convention:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements
- `chore/` - Maintenance tasks

## 📝 Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/

# Run specific test file
pytest tests/test_specit.py

# Run in watch mode
ptw
```

### Code Quality Checks

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/

# Linting
pylint src/

# All checks (same as CI)
make check
```

### Building Documentation

```bash
# Build docs locally
cd docs/
sphinx-build -b html . _build/

# View in browser
open _build/index.html
```

## 📋 Commit Guidelines

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
- **style** - Code style changes (formatting, missing semicolons, etc.)
- **refactor** - Code refactoring without feature changes
- **perf** - Performance improvements
- **test** - Adding or updating tests
- **chore** - Build process, dependencies, tooling

## 🧪 Testing Requirements

All contributions should include tests:

```python
# tests/commands/test_specit.py
import pytest
from doit.commands.specit import SpecIt

def test_specit_basic():
    """Test basic spec creation."""
    cmd = SpecIt()
    result = cmd.run(spec="A task management app")
    
    assert result.success
    assert result.diagram_type == "user_journey"
    assert "task" in result.spec_file.lower()

def test_specit_with_entities():
    """Test spec with entity extraction."""
    cmd = SpecIt()
    result = cmd.run(
        spec="Users manage projects containing tasks",
        extract_entities=True
    )
    
    assert len(result.entities) == 3  # Users, Projects, Tasks
    assert "relationships" in result.output
```

**Coverage Requirements:**
- Minimum 80% overall coverage
- 100% for critical paths (command execution, memory system)
- All public APIs must have tests

## 📚 Documentation

### Code Documentation

```python
def planit(specification: str, ai_agent: Optional[str] = None) -> ArchitecturePlan:
    """
    Create a technical architecture plan from a specification.
    
    Auto-generates architecture diagram showing system components, 
    boundaries, and dependencies. Suggests component breakdown and 
    identifies potential issues.
    
    Args:
        specification: The project specification to plan
        ai_agent: Optional AI agent to use for enhancement suggestions
        
    Returns:
        ArchitecturePlan object containing:
            - diagram (Mermaid): Architecture diagram
            - components: Identified components
            - dependencies: Component relationships
            - suggestions: AI enhancement suggestions
            
    Raises:
        SpecificationError: If spec is invalid
        ArchitectureError: If architecture can't be determined
        
    Examples:
        >>> plan = planit("REST API with microservices")
        >>> print(plan.diagram)
        >>> for comp in plan.components:
        ...     print(f"{comp.name}: {comp.description}")
    """
```

### Docstring Style

We use Google-style docstrings. See [Google Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

### Comments

```python
# For complex logic, explain the WHY, not the WHAT
# The specification can auto-generate entity relationships by parsing
# noun phrases, but we need semantic understanding to catch implicit
# relationships (e.g., "User logs in" implies User <-> Auth Service)
relationships = extract_semantic_relationships(spec)
```

## 🐛 Bug Reports

Found a bug? Please report it!

### Before Reporting

1. Check [existing issues](https://github.com/doit-toolkit/doit/issues)
2. Test with the latest version
3. Verify it's a DoIt bug, not a configuration issue

### When Reporting

Include:

```
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command: `doit specit "..."`
2. Observe: ...
3. Expected: ...

**Environment**
- DoIt version: `doit --version`
- Python version: `python --version`
- OS: Windows/Mac/Linux
- Shell: bash/zsh/powershell

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

Have an idea for a new feature?

### Before Requesting

1. Check [existing discussions](https://github.com/doit-toolkit/doit/discussions)
2. Verify it aligns with [project roadmap](./ROADMAP.md)
3. Consider the scope and maintenance burden

### When Requesting

```
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
How should it work?

**Describe alternatives you've considered**
Other possible approaches.

**Why should DoIt have this feature?**
Who benefits? What problems does it solve?

**Examples**
Show usage examples.
```

## 🔍 Code Review Process

1. **Automated Checks** - CI/CD runs tests, coverage, linting
2. **Peer Review** - At least one maintainer reviews code
3. **Feedback** - Changes requested or approved
4. **Merge** - Approved PRs are merged to main

### What We Look For

- ✅ Tests included and passing
- ✅ Documentation updated
- ✅ Code follows style guidelines
- ✅ Commit messages are clear
- ✅ No breaking changes (or justified)
- ✅ Performance acceptable
- ✅ Security considered

### Helpful Review Comments

When reviewing others' code:

```
# Good
"This would be clearer as a generator since we iterate multiple times"

# Bad
"This is wrong"

---

# Good
"Have you considered caching this result? It might be slow for large specs"

# Bad
"This is inefficient"
```

## 📦 Pull Request Process

1. **Create Branch** - From latest `main`
2. **Make Changes** - Include tests and docs
3. **Run Tests** - `pytest` passes locally
4. **Commit** - Follow conventional commits
5. **Push** - To your fork
6. **Create PR** - Use the template (auto-filled)
7. **Address Review** - Respond to feedback
8. **Merge** - Maintainer merges when approved

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
Describe testing done.

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Code follows style guidelines
- [ ] All tests pass
```

## 🎯 Priority Areas for Contributions

Looking for where to start? These areas need help:

### High Priority

- **Diagram Enhancements** - New diagram types, better layout algorithms
- **AI Integration** - Additional agent support (Claude, Llama, etc.)
- **Performance** - Optimize for large projects (10k+ items)
- **Windows Support** - Better Windows compatibility

### Medium Priority

- **Documentation** - Expand guides, add more examples
- **Error Messages** - Make error messages more helpful
- **Plugin System** - Allow custom commands
- **Integrations** - GitHub, GitLab, Jira, Linear, etc.

### Good for First-Time Contributors

- Documentation improvements
- Test coverage expansion
- Bug fixes with clear reproduction steps
- Code style improvements
- Small feature requests

## 💬 Communication

### Before Starting Major Work

For significant features or changes, please open a discussion first:

```
1. Create GitHub Issue or Discussion
2. Describe the change you want to make
3. Wait for maintainer feedback
4. Start implementation after discussion
```

This prevents duplicate work and ensures alignment.

### Getting Help

- **Questions** - [GitHub Discussions](https://github.com/doit-toolkit/doit/discussions)
- **Chat** - [Discord Community](https://discord.gg/doit)
- **Issues** - [GitHub Issues](https://github.com/doit-toolkit/doit/issues)

## 📖 Resources

- **[Architecture Guide](./docs/architecture.md)** - How DoIt works internally
- **[Code Structure](./docs/code-structure.md)** - Where to find things
- **[Adding Commands](./docs/adding-commands.md)** - How to add new commands
- **[Testing Guide](./docs/testing-guide.md)** - How to write tests

## 🎓 Learning Path for Contributors

1. **Read** the main README and ARCHITECTURE
2. **Explore** the codebase structure
3. **Run** existing tests to understand patterns
4. **Pick** a small issue and make a PR
5. **Get** feedback and learn
6. **Grow** to larger contributions

## 🎖️ Recognition

Contributors are recognized in:

- **README.md** - All contributors listed
- **CHANGELOG.md** - Feature/fix attributions
- **Release Notes** - Special thanks to major contributors
- **Website** - Contributors page on doit-toolkit.dev

## ⚖️ Code of Conduct

This project is committed to creating an inclusive, welcoming environment. See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## 📝 License

By contributing, you agree that your contributions will be licensed under the same MIT license as the project.

## ❓ Questions?

- Ask in [GitHub Discussions](https://github.com/doit-toolkit/doit/discussions)
- Chat in [Discord](https://discord.gg/doit)
- Email [contributors@doit-toolkit.dev](mailto:contributors@doit-toolkit.dev)

---

**Thank you for contributing to DoIt! 🙏**
