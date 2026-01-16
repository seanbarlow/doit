# Research: Auto-Mermaid Diagram Generation

**Feature**: 035-auto-mermaid-diagrams
**Date**: 2026-01-16

## Research Questions

### 1. Mermaid Syntax Validation in Python

**Question**: How to validate generated Mermaid syntax without external dependencies?

**Decision**: Use regex-based validation for common errors, with optional strict mode using mermaid-cli.

**Rationale**:
- No pure-Python Mermaid validator library exists
- Canonical validation requires Node.js-based mermaid-cli (heavy dependency)
- Regex validation catches 80%+ of common errors
- Constitution requires minimal external dependencies

**Alternatives Considered**:
- mermaid-py (Python wrapper) - requires Node.js runtime
- Mermaid Validator MCP Server - adds external dependency
- No validation - violates FR-020 requirement

### 2. User Story Parsing Patterns

**Question**: How to reliably parse user stories from spec.md markdown?

**Decision**: Use regex patterns matching the established template structure.

**Rationale**:
- Spec template has consistent format: `### User Story N - Title (Priority: PN)`
- Acceptance scenarios follow: `**Given** X, **When** Y, **Then** Z`
- Regex can reliably extract structure without markdown parser

**Patterns Identified**:
```regex
# User story header
^### User Story (\d+) - (.+?) \(Priority: (P\d+)\)$

# Acceptance scenario
^\d+\.\s+\*\*Given\*\*\s+(.+?),\s+\*\*When\*\*\s+(.+?),\s+\*\*Then\*\*\s+(.+)$
```

### 3. Entity Relationship Inference

**Question**: How to infer ER relationships from natural language entity descriptions?

**Decision**: Use keyword patterns to infer cardinality from Key Entities section.

**Rationale**:
- Key Entities use consistent descriptive patterns
- "has many" → 1:N, "belongs to" → N:1, "has one" → 1:1
- Conservative inference - skip ambiguous cases rather than guess wrong

**Keyword Patterns**:
| Pattern | Cardinality | Mermaid Syntax |
|---------|-------------|----------------|
| "has many", "contains" | 1:N | `\|\|--o{` |
| "has one", "owns" | 1:1 | `\|\|--\|\|` |
| "belongs to" | N:1 (reverse) | `}o--\|\|` |
| "many-to-many" | N:M | `}o--o{` |

### 4. AUTO-GENERATED Marker Handling

**Question**: How to safely replace content within markers without corrupting file?

**Decision**: Parse markers, extract boundaries, replace only bounded content.

**Rationale**:
- Markers clearly delimit auto-generated sections
- Must preserve all content outside markers (FR-005)
- Backup original before modification for safety

**Marker Format**:
```markdown
<!-- BEGIN:AUTO-GENERATED section="name" -->
[content to replace]
<!-- END:AUTO-GENERATED -->
```

### 5. Flowchart Node ID Generation

**Question**: How to generate unique, valid Mermaid node IDs?

**Decision**: Use prefix + incremental pattern: `US{story_num}_{letter}`.

**Rationale**:
- Mermaid requires alphanumeric IDs without spaces
- Prefix groups nodes by user story
- Letter suffix provides ordering within story

**Examples**:
- `US1_A` - First node in User Story 1
- `US1_B` - Second node in User Story 1
- `US2_A` - First node in User Story 2

## Key Implementation Decisions

### Validation Strategy (FR-020 - FR-023)

1. **Basic Validation** (always):
   - Check diagram type declaration present
   - Verify all brackets/braces are balanced
   - Check for common syntax pitfalls
   - Validate node ID format

2. **Strict Mode** (optional `--strict` flag):
   - Shell to mermaid-cli for canonical validation
   - Only when explicitly requested (performance)

### Error Handling Strategy (FR-024 - FR-026)

1. **Graceful Degradation**:
   - Skip malformed user stories, continue with valid ones
   - Log warnings, don't fail entire generation
   - Preserve original content on complete failure

2. **Missing Markers**:
   - Insert markers at standard locations
   - User Journey: after "## User Journey Visualization"
   - Entity Relationships: after "## Entity Relationships"

### Performance Considerations

- Target: <1 second for specs with up to 10 user stories (SC-004)
- Use compiled regex patterns (one-time compilation)
- Process user stories and entities in single pass

## Integration Points

### Specit Workflow Integration (US4)

The specit command template can call diagram generation by:
1. Write spec.md content
2. Call diagram generator service
3. Re-write spec.md with diagrams embedded

### Existing Services to Reuse

| Service | Purpose |
|---------|---------|
| `SpecScanner` | Pattern for parsing spec.md metadata |
| `ValidationService` | Pattern for rule-based validation |
| `status_models.py` | Pattern for dataclass models |

## Out of Scope for Initial Implementation

- Rendering diagrams to images (SVG/PNG) - use GitHub/VS Code native
- Complex NLP for relationship inference - use keyword matching only
- Real-time diagram preview - CLI is batch-oriented
