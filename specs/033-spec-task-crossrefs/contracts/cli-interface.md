# CLI Contract: Cross-Reference Commands

**Feature**: 033-spec-task-crossrefs
**Date**: 2026-01-16

## Command Group: `doit xref`

### `doit xref coverage`

Generate a coverage report showing requirement-to-task mapping.

**Usage**:
```bash
doit xref coverage [OPTIONS] [SPEC_NAME]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| SPEC_NAME | string | No | Spec directory name (default: auto-detect from branch) |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| --format | choice | rich | Output format: rich, json, markdown |
| --strict | flag | false | Treat uncovered requirements as errors |
| --output | path | - | Write output to file instead of stdout |

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | All requirements covered |
| 1 | Uncovered requirements (with --strict) or errors |
| 2 | Spec not found or invalid |

**Example Output (rich)**:
```
Requirement Coverage: 033-spec-task-crossrefs
═══════════════════════════════════════════════

 Requirement │ Tasks │ Status
─────────────┼───────┼────────────
 FR-001      │ 2     │ ✓ Covered
 FR-002      │ 1     │ ✓ Covered
 FR-003      │ 0     │ ⚠ Uncovered

Coverage: 67% (2/3)
```

**Example Output (json)**:
```json
{
  "spec": "033-spec-task-crossrefs",
  "requirements": [
    {"id": "FR-001", "task_count": 2, "covered": true},
    {"id": "FR-002", "task_count": 1, "covered": true},
    {"id": "FR-003", "task_count": 0, "covered": false}
  ],
  "coverage_percent": 67,
  "covered_count": 2,
  "total_count": 3
}
```

---

### `doit xref locate`

Find the definition of a requirement in spec.md.

**Usage**:
```bash
doit xref locate <REQUIREMENT_ID> [OPTIONS]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| REQUIREMENT_ID | string | Yes | Requirement ID (e.g., FR-001) |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| --spec | path | - | Spec file path (default: auto-detect) |
| --format | choice | rich | Output format: rich, json, line |

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Requirement found |
| 1 | Requirement not found |
| 2 | Spec file not found |

**Example Output (rich)**:
```
FR-001: System MUST support cross-reference syntax...
Location: specs/033-spec-task-crossrefs/spec.md:149
```

**Example Output (line)** (for IDE integration):
```
specs/033-spec-task-crossrefs/spec.md:149
```

---

### `doit xref tasks`

List all tasks that implement a specific requirement.

**Usage**:
```bash
doit xref tasks <REQUIREMENT_ID> [OPTIONS]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| REQUIREMENT_ID | string | Yes | Requirement ID (e.g., FR-001) |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| --spec | path | - | Spec directory (default: auto-detect) |
| --format | choice | rich | Output format: rich, json, markdown |

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Tasks found |
| 1 | No tasks found for requirement |
| 2 | Requirement or spec not found |

**Example Output (rich)**:
```
Tasks implementing FR-001:

 Line │ Status │ Description
──────┼────────┼─────────────────────────────────────
 12   │ [ ]    │ Add RequirementParser class
 15   │ [x]    │ Define Requirement dataclass

Found 2 tasks (1 complete, 1 pending)
```

---

### `doit xref validate`

Validate cross-reference integrity between spec and tasks.

**Usage**:
```bash
doit xref validate [OPTIONS] [SPEC_NAME]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| SPEC_NAME | string | No | Spec directory name (default: auto-detect) |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| --strict | flag | false | Treat warnings as errors |
| --format | choice | rich | Output format: rich, json |

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | All cross-references valid |
| 1 | Validation errors found |
| 2 | Files not found |

**Example Output**:
```
Cross-Reference Validation: 033-spec-task-crossrefs
═══════════════════════════════════════════════════

✓ All 10 requirement references are valid
⚠ 2 requirements have no linked tasks: FR-003, FR-007

Validation: WARN (0 errors, 2 warnings)
```

---

## Integration with Existing Commands

### `doit validate` Integration

The existing `doit validate` command will include cross-reference rules when both spec.md and tasks.md exist:

```bash
doit validate specs/033-spec-task-crossrefs/spec.md
```

**Additional Output**:
```
Cross-Reference Issues:
  ⚠ Warning: FR-003 has no linked tasks (uncovered-requirement)
  ✗ Error: Task references FR-099 which doesn't exist (orphaned-task-reference)
```

### `doit status` Integration

The status dashboard will show cross-reference coverage in the spec summary:

```
specs/033-spec-task-crossrefs
  Status: In Progress
  Validation: 95/100
  XRef Coverage: 67% (2/3)  ← New field
```
