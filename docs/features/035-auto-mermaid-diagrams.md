# Feature: Automatic Mermaid Diagram Generation

**Completed**: 2026-01-16
**Branch**: `035-auto-mermaid-diagrams`
**Epic**: #441
**Spec**: [spec.md](../../specs/035-auto-mermaid-diagrams/spec.md)

## Overview

Automatic generation of Mermaid diagrams from specification content, fulfilling Constitution Principle III: "Diagrams MUST be generated automatically from specifications using Mermaid syntax."

The feature includes:
- **User Journey Flowcharts**: Generated from user stories with subgraphs per story
- **Entity Relationship Diagrams**: Generated from Key Entities section with cardinality
- **Architecture Diagrams**: Generated from plan.md Project Structure
- **Syntax Validation**: Regex-based validation with optional strict mode
- **CLI Integration**: `doit diagram generate` and `doit diagram validate` commands

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Parse user stories → flowcharts | Done |
| FR-002 | Parse Key Entities → ER diagrams | Done |
| FR-003 | Insert within AUTO-GENERATED markers | Done |
| FR-004 | Replace existing content on regeneration | Done |
| FR-005 | Preserve content outside blocks | Done |
| FR-006 | Subgraph per user story | Done |
| FR-007 | Nodes from Given/When/Then | Done |
| FR-008 | Flow arrows between nodes | Done |
| FR-009 | Decision diamonds for branches | Done |
| FR-010 | Unique node IDs (US1_A, US1_B) | Done |
| FR-011 | Entity box per Key Entity | Done |
| FR-012 | Attributes in entity box | Done |
| FR-013 | Infer relationships from text | Done |
| FR-014 | Cardinality support (1:1, 1:N, N:M) | Done |
| FR-015 | PK/FK markers | Done |
| FR-016 | `doit diagram generate` CLI | Done |
| FR-017 | Specit integration | Deferred |
| FR-018 | `--no-insert` flag | Done |
| FR-019 | plan.md architecture support | Done |
| FR-020 | Validate Mermaid syntax | Done |
| FR-021 | Report syntax errors | Done |
| FR-022 | `--strict` flag | Done |
| FR-023 | Log warnings for unparseable content | Done |
| FR-024 | Handle missing markers gracefully | Done |
| FR-025 | Continue when stories fail to parse | Done |
| FR-026 | Preserve original on failure | Done |

## Technical Details

### Architecture

```
src/doit_cli/
├── models/
│   └── diagram_models.py       # DiagramType, ParsedUserStory, etc.
├── services/
│   ├── diagram_service.py      # Main orchestrator
│   ├── user_story_parser.py    # Parse user stories
│   ├── entity_parser.py        # Parse Key Entities
│   ├── section_parser.py       # Parse AUTO-GENERATED sections
│   ├── user_journey_generator.py   # Generate flowcharts
│   ├── er_diagram_generator.py     # Generate ER diagrams
│   ├── mermaid_validator.py    # Syntax validation
│   └── architecture_generator.py   # Architecture diagrams
└── cli/
    └── diagram_command.py      # CLI subcommands
```

### Key Decisions

1. **Regex-based Parsing**: Uses regex patterns rather than external markdown parser for predictable structure
2. **Two-tier Validation**: Basic regex validation (default) + optional mermaid-cli (strict mode)
3. **Atomic File Writes**: Read → modify in memory → write atomically with backup on failure
4. **Unique Node IDs**: Format `US{story}_S{scenario}_{step}` prevents collisions

## Files Changed

### Models (1 file)
- `src/doit_cli/models/diagram_models.py`

### Services (8 files)
- `src/doit_cli/services/diagram_service.py`
- `src/doit_cli/services/user_story_parser.py`
- `src/doit_cli/services/entity_parser.py`
- `src/doit_cli/services/section_parser.py`
- `src/doit_cli/services/user_journey_generator.py`
- `src/doit_cli/services/er_diagram_generator.py`
- `src/doit_cli/services/mermaid_validator.py`
- `src/doit_cli/services/architecture_generator.py`

### CLI (1 file)
- `src/doit_cli/cli/diagram_command.py`

### Tests (9 files)
- `tests/unit/test_user_story_parser.py`
- `tests/unit/test_entity_parser.py`
- `tests/unit/test_user_journey_generator.py`
- `tests/unit/test_er_diagram_generator.py`
- `tests/unit/test_mermaid_validator.py`
- `tests/unit/test_diagram_service.py`
- `tests/unit/test_architecture_generator.py`
- `tests/integration/test_diagram_command.py`
- `tests/integration/test_diagram_workflow.py`

## Testing

### Automated Tests
- **121 tests** total (all passing)
- Unit tests: 85
- Integration tests: 36
- Test duration: 0.26s

### Manual Tests Verified
- US1: User journey flowchart generation ✅
- US2: ER diagram generation ✅
- US3: Regeneration preserves content ✅
- US4: CLI commands functional ✅
- US5: Syntax validation works ✅
- US6: Architecture diagrams from plan.md ✅

## Usage

### Generate Diagrams
```bash
# Generate all diagrams for a spec
doit diagram generate specs/my-feature/spec.md

# Generate specific diagram type
doit diagram generate spec.md --type user-journey

# Preview without inserting
doit diagram generate spec.md --no-insert

# Strict validation mode
doit diagram generate spec.md --strict
```

### Validate Diagrams
```bash
# Validate existing diagrams
doit diagram validate spec.md

# Strict validation
doit diagram validate spec.md --strict
```

## Related Issues

- **Epic**: #441 - [EPIC] 035 - Automatic Mermaid Diagram Generation
- **Features**: #442 (US1), #443 (US2), #444 (US3), #445 (US4), #446 (US5), #447 (US6)
- **Tasks**: #448-#471 (T001-T024)

## Future Enhancements

1. Integrate `doit diagram generate` as post-hook in specit workflow
2. Add mermaid-cli integration for strict validation
3. Add diagram type auto-detection based on file content

---

*Generated by `/doit.checkin` on 2026-01-16*
