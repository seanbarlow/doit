# Support

Looking for help with Do-It? This document will guide you to the right resources.

## Documentation

- **[README](README.md)** - Getting started, installation, and basic usage
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](CHANGELOG.md)** - Version history and changes
- **[Security Policy](SECURITY.md)** - How to report security issues

## Getting Help

### Before Asking for Help

1. **Check the documentation** - The README covers most common use cases
2. **Search existing issues** - Your question may already be answered
3. **Try the latest version** - `pip install --upgrade doit-toolkit-cli`

### Where to Get Help

#### GitHub Issues

For bug reports and feature requests:

- [Open an issue](https://github.com/seanbarlow/doit/issues/new)
- Search [existing issues](https://github.com/seanbarlow/doit/issues) first

**Good for:**

- Bug reports with reproduction steps
- Feature requests with use cases
- Documentation improvements

#### GitHub Discussions

For questions, ideas, and community conversations:

- [Start a discussion](https://github.com/seanbarlow/doit/discussions)

**Good for:**

- How-to questions
- Best practices discussions
- Showing off what you've built
- General feedback

## Reporting Issues

When reporting an issue, please include:

```markdown
**Environment**
- Do-It version: (run `doit --version`)
- Python version: (run `python --version`)
- Operating system:

**Description**
What happened vs. what you expected.

**Steps to Reproduce**
1. First step
2. Second step
3. ...

**Additional Context**
Any other relevant information.
```

## Common Issues

### Installation Problems

**Issue**: `pip install` fails

**Solutions**:

- Ensure Python 3.11+ is installed: `python --version`
- Try upgrading pip: `pip install --upgrade pip`
- Use a virtual environment: `python -m venv .venv && source .venv/bin/activate`

### Command Not Found

**Issue**: `doit` command not recognized after installation

**Solutions**:

- Ensure the package is installed: `pip show doit-toolkit-cli`
- Check if pip scripts are in your PATH
- Try running with python: `python -m doit_cli`

### Permission Errors

**Issue**: Permission denied when running `doit init`

**Solutions**:

- Check write permissions in the target directory
- Don't run with `sudo` - use a virtual environment instead

## Response Times

This is an open source project maintained by volunteers. Please be patient.

- **Bug reports**: We aim to triage within a week
- **Feature requests**: Reviewed periodically based on roadmap priorities
- **Pull requests**: Reviewed as time permits

## Commercial Support

There is no commercial support available for Do-It at this time. The project is maintained as open source.

## Contributing

The best way to support Do-It is to contribute! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- How to set up a development environment
- Coding guidelines
- How to submit pull requests

## Code of Conduct

Please be respectful in all interactions. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for our community guidelines.

---

Thank you for using Do-It!
