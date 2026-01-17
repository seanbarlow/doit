# Cross-Reference Support Between Specs and Tasks

**Completed**: 2026-01-16
**Branch**: 033-spec-task-crossrefs
**Feature**: Bidirectional traceability between specification requirements and implementation tasks

## Overview

This feature enables bidirectional linking between specification requirements (FR-XXX) and implementation tasks, providing full traceability from requirements through implementation. Users can see which requirements are covered by tasks, which tasks implement specific requirements, and navigate seamlessly between related artifacts.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Support cross-reference syntax `[FR-XXX]` in tasks | Done |
| FR-002 | Parse `[FR-XXX]` references from task descriptions | Done |
| FR-003 | Generate coverage reports showing requirement-to-task mapping | Done |
| FR-004 | Calculate coverage percentage for spec requirements | Done |
| FR-005 | Identify and report uncovered requirements | Done |
| FR-006 | Detect orphaned task references (invalid FR-XXX IDs) | Done |
| FR-007 | Provide CLI command to locate requirement definitions | Done |
| FR-008 | Provide CLI command to list tasks for a requirement | Done |
| FR-009 | Support multiple references per task `[FR-001, FR-002]` | Done |
| FR-010 | Integrate with validation system via traceability rules | Done |

## Technical Details

### Architecture

- **CLI Layer**: `xref_command.py` - Typer-based commands for coverage, locate, tasks, validate
- **Service Layer**:
  - `CrossReferenceService` - Unified API for cross-reference operations
  - `RequirementParser` - Extracts FR-XXX requirements from spec.md files
  - `TaskParser` - Parses tasks.md and extracts `[FR-XXX]` references
  - `CoverageCalculator` - Computes coverage metrics and identifies gaps
- **Model Layer**: `crossref_models.py` - Requirement, Task, CrossReference, CoverageReport
- **Validation Rules**: Traceability rules in `builtin_rules.py`

### Key Decisions

1. **Regex-based parsing** - Uses `^\\s*-\\s*\\*\\*(?P<id>FR-\\d{3})\\*\\*:` pattern for requirements and `\\[FR-\\d{3}(,\\s*FR-\\d{3})*\\]` for references
2. **Coverage calculation** - Requirements are "covered" if at least one task references them
3. **Validation severity** - Orphaned references are ERROR severity; uncovered requirements are WARNING
4. **Line numbers** - Both requirements and references track source line numbers for IDE navigation

## Files Changed

### New Files
- `src/doit_cli/models/crossref_models.py` - Data models (Requirement, Task, CrossReference, RequirementCoverage, CoverageReport)
- `src/doit_cli/services/requirement_parser.py` - Parses requirements from spec.md
- `src/doit_cli/services/task_parser.py` - Parses tasks with cross-references from tasks.md
- `src/doit_cli/services/coverage_calculator.py` - Calculates coverage metrics
- `src/doit_cli/services/crossref_service.py` - Orchestrates cross-reference operations
- `src/doit_cli/cli/xref_command.py` - CLI commands (coverage, locate, tasks, validate)
- `tests/unit/services/test_requirement_parser.py` - Unit tests for requirement parsing
- `tests/unit/services/test_task_parser.py` - Unit tests for task parsing
- `tests/unit/services/test_coverage_calculator.py` - Unit tests for coverage calculation
- `tests/unit/services/test_crossref_service.py` - Unit tests for service layer
- `tests/integration/test_xref_integration.py` - End-to-end integration tests

### Modified Files
- `src/doit_cli/main.py` - Registered xref command group
- `src/doit_cli/models/__init__.py` - Added crossref model exports
- `src/doit_cli/services/__init__.py` - Added crossref service exports
- `src/doit_cli/rules/builtin_rules.py` - Added traceability validation rules
- `src/doit_cli/services/rule_engine.py` - Integrated traceability rules

## Testing

- **Unit tests**: 92 feature-specific tests covering all components
- **Integration tests**: End-to-end CLI command tests
- **Manual tests**: 8 manual tests, all passed
- **Total suite**: 729 tests, all passing

## Usage Examples

```bash
# View coverage report for a specification
doit xref coverage --spec 033-spec-task-crossrefs

# Locate a requirement definition
doit xref locate FR-001 --spec 033-spec-task-crossrefs

# List tasks implementing a requirement
doit xref tasks FR-001 --spec 033-spec-task-crossrefs

# Validate cross-references (check for orphans/uncovered)
doit xref validate --spec 033-spec-task-crossrefs

# JSON output for machine processing
doit xref coverage --spec 033-spec-task-crossrefs --format json

# Strict mode - treats uncovered requirements as errors
doit xref validate --spec 033-spec-task-crossrefs --strict

# Line format for IDE integration
doit xref locate FR-001 --spec 033-spec-task-crossrefs --format line
```

## Validation Rules

Two new traceability rules are included:

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `orphaned-task-reference` | ERROR | Task references non-existent requirement ID |
| `uncovered-requirement` | WARNING | Requirement has no implementing tasks |

---
Generated by `/doit.checkin`
