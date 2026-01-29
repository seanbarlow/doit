# macOS E2E Testing - Quick Start Guide

**Feature**: End-to-End Testing for macOS
**Branch**: `050-macos-e2e-tests`
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## Prerequisites

- **macOS**: 12+ (Monterey, Ventura, or Sonoma)
- **Python**: 3.11 or higher
- **Git**: Installed and configured
- **pytest**: Installed via pip

## Installation

```bash
# Install doit with dev dependencies
pip install -e ".[dev]"

# Install additional test dependencies
pip install pytest pytest-timeout pytest-xdist pytest-html
```

## Running macOS E2E Tests

### Run All macOS Tests

```bash
pytest tests/e2e/macos/ -v
```

### Run by User Story

```bash
# User Story 1: Core E2E workflows (P1 - MVP)
pytest tests/e2e/macos/test_*_workflow.py -v

# User Story 2: Filesystem features (P2)
pytest tests/e2e/macos/ -m filesystem -v

# User Story 3: Bash/BSD compatibility (P2)
pytest tests/e2e/macos/ -m bsd -v

# User Story 4: CI/CD integration (P3)
# (Runs automatically in GitHub Actions)
```

### Run by Test Marker

```bash
# Run only macOS-specific tests
pytest -m macos -v

# Run E2E tests
pytest -m "macos and e2e" -v

# Run filesystem tests
pytest -m "macos and filesystem" -v

# Run BSD utility tests
pytest -m "macos and bsd" -v

# Run Unicode handling tests
pytest -m "macos and unicode" -v

# Run CI-suitable tests only
pytest -m "macos and ci" -v
```

### Run with Coverage

```bash
pytest tests/e2e/macos/ --cov=src --cov-report=html --cov-report=term
```

### Run Tests in Parallel

```bash
pytest tests/e2e/macos/ -n auto  # Uses all CPU cores
pytest tests/e2e/macos/ -n 4     # Uses 4 workers
```

## Test Organization

### Test Files by User Story

**US1 - Core E2E Workflows (P1)**:
- [test_init_workflow.py](../../tests/e2e/macos/test_init_workflow.py) - doit init tests
- [test_specit_workflow.py](../../tests/e2e/macos/test_specit_workflow.py) - doit specit tests
- [test_planit_workflow.py](../../tests/e2e/macos/test_planit_workflow.py) - doit planit tests
- [test_taskit_workflow.py](../../tests/e2e/macos/test_taskit_workflow.py) - doit taskit tests
- [test_implementit_workflow.py](../../tests/e2e/macos/test_implementit_workflow.py) - doit implementit tests
- [test_checkin_workflow.py](../../tests/e2e/macos/test_checkin_workflow.py) - doit checkin tests
- [test_macos_basic_paths.py](../../tests/e2e/macos/test_macos_basic_paths.py) - Path handling tests
- [test_line_endings.py](../../tests/e2e/macos/test_line_endings.py) - Line ending tests

**US2 - Filesystem Features (P2)**:
- [test_case_sensitivity.py](../../tests/e2e/macos/test_case_sensitivity.py) - Case-sensitivity tests
- [test_unicode_normalization.py](../../tests/e2e/macos/test_unicode_normalization.py) - Unicode NFD/NFC tests
- [test_extended_attributes.py](../../tests/e2e/macos/test_extended_attributes.py) - xattr tests
- [test_symbolic_links.py](../../tests/e2e/macos/test_symbolic_links.py) - Symlink tests
- [test_ds_store_handling.py](../../tests/e2e/macos/test_ds_store_handling.py) - .DS_Store tests

**US3 - Bash/BSD Compatibility (P2)**:
- [test_bsd_commands.py](../../tests/e2e/macos/test_bsd_commands.py) - BSD utility tests
- [test_bash_vs_zsh.py](../../tests/e2e/macos/test_bash_vs_zsh.py) - Shell compatibility tests
- [test_macos_environment.py](../../tests/e2e/macos/test_macos_environment.py) - Environment variable tests
- [test_script_compatibility.py](../../tests/e2e/macos/test_script_compatibility.py) - Bash script tests

**US4 - CI/CD Integration (P3)**:
- [.github/workflows/macos-e2e-tests.yml](../../.github/workflows/macos-e2e-tests.yml) - GitHub Actions workflow

**Cross-Cutting**:
- [test_cross_platform_parity.py](../../tests/e2e/macos/test_cross_platform_parity.py) - Cross-platform comparison
- [test_macos_edge_cases.py](../../tests/e2e/macos/test_macos_edge_cases.py) - Edge case handling

### Test Utilities

All test utilities are in [tests/utils/macos/](../../tests/utils/macos/):

- **filesystem_utils.py** - APFS, case-sensitivity detection
- **unicode_utils.py** - NFD/NFC normalization
- **bsd_utils.py** - BSD command wrappers
- **xattr_utils.py** - Extended attribute handling
- **comparison_utils.py** - Cross-platform output comparison

### Test Fixtures

Shared pytest fixtures are in [tests/e2e/macos/conftest.py](../../tests/e2e/macos/conftest.py):

- `macos_test_env` - Environment information
- `temp_project_dir` - Temporary project directory
- `case_sensitive_volume` - Case-sensitivity detection
- `unicode_test_files` - Unicode test files
- `bsd_command_wrapper` - BSD command wrapper
- `xattr_handler` - Extended attribute handler
- `comparison_tools` - Comparison utilities

## Debugging Failed Tests

### Verbose Output

```bash
pytest tests/e2e/macos/ -v -s
```

### Run Specific Test

```bash
pytest tests/e2e/macos/test_macos_filesystem.py::test_case_sensitivity -v
```

### Show Full Traceback

```bash
pytest tests/e2e/macos/ -v --tb=long
```

### Drop into Debugger on Failure

```bash
pytest tests/e2e/macos/ --pdb
```

### Show Test Duration

```bash
pytest tests/e2e/macos/ --durations=10
```

## Common Issues

### Issue: Tests Skip on Non-macOS

**Symptom**: All tests show as "SKIPPED"

**Cause**: Tests marked with `@pytest.mark.macos` only run on macOS

**Solution**: This is expected behavior. Run tests on a macOS machine.

### Issue: Case-Sensitive Tests Skip

**Symptom**: Tests marked with `@pytest.mark.case_sensitive` skip

**Cause**: Your volume is case-insensitive (default macOS behavior)

**Solution**: This is expected. Case-sensitive tests require a case-sensitive APFS volume.

### Issue: BSD Command Tests Fail

**Symptom**: Tests in test_bsd_commands.py fail

**Cause**: May be using GNU utilities installed via Homebrew

**Solution**: Tests should handle both BSD and GNU utilities. Check test output for details.

### Issue: Unicode Tests Fail

**Symptom**: Tests in test_unicode_normalization.py fail

**Cause**: Unicode normalization differences

**Solution**: Ensure you're running on macOS. The filesystem handles NFD normalization automatically.

## CI/CD Integration

Tests run automatically in GitHub Actions on:
- Pull requests to `main` or `develop`
- Pushes to `main` or `develop`
- Manual workflow dispatch

### Matrix Configuration

- **macOS versions**: 12, 13, 14
- **Python versions**: 3.11, 3.12
- **Total combinations**: 6

### View CI Results

1. Go to the Actions tab in GitHub
2. Select "macOS E2E Tests" workflow
3. View test results, artifacts, and logs

## Performance Expectations

- **Full test suite**: < 10 minutes in CI
- **Individual test**: < 30 seconds
- **MVP tests (US1)**: < 5 minutes

## Next Steps

1. **Run MVP tests**: `pytest tests/e2e/macos/test_*_workflow.py -v`
2. **Run all tests**: `pytest tests/e2e/macos/ -v`
3. **Check coverage**: `pytest tests/e2e/macos/ --cov=src --cov-report=html`
4. **View HTML report**: Open `htmlcov/index.html`

## Support

- **Spec**: [spec.md](spec.md) - Feature requirements
- **Plan**: [plan.md](plan.md) - Implementation details
- **Tasks**: [tasks.md](tasks.md) - Implementation tasks
- **Main README**: [../../README.md](../../README.md) - Project overview
