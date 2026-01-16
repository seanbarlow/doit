# CLI Interface Contract: Diagram Command

**Feature**: 035-auto-mermaid-diagrams
**Date**: 2026-01-16

## Command Structure

```
doit diagram <subcommand> [OPTIONS] [ARGS]
```

## Subcommands

### `generate`

Generate Mermaid diagrams for a specification or plan file.

```
doit diagram generate [FILE] [OPTIONS]
```

**Arguments:**
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `FILE` | path | No | auto-detect | Path to spec.md or plan.md file |

**Options:**
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--strict` | `-s` | flag | False | Fail on validation errors |
| `--no-insert` | | flag | False | Output diagrams without inserting into file |
| `--type` | `-t` | choice | all | Diagram type: user-journey, er-diagram, architecture, all |
| `--output` | `-o` | path | None | Write diagrams to separate file |

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | Success - diagrams generated |
| 1 | Error - file not found or invalid |
| 2 | Validation failed (strict mode) |
| 3 | No content to diagram |

**Examples:**
```bash
# Generate all diagrams for current branch spec
doit diagram generate

# Generate for specific file
doit diagram generate specs/035-auto-mermaid-diagrams/spec.md

# Generate only ER diagram with strict validation
doit diagram generate --type er-diagram --strict

# Output diagrams to separate file without modifying source
doit diagram generate --no-insert --output diagrams.md
```

### `validate`

Validate Mermaid syntax in a file.

```
doit diagram validate [FILE] [OPTIONS]
```

**Arguments:**
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `FILE` | path | No | auto-detect | Path to file containing Mermaid diagrams |

**Options:**
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--strict` | `-s` | flag | False | Use mermaid-cli for canonical validation |

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | All diagrams valid |
| 1 | Validation errors found |
| 2 | File not found |

**Examples:**
```bash
# Validate diagrams in spec
doit diagram validate specs/035-auto-mermaid-diagrams/spec.md

# Strict validation using mermaid-cli
doit diagram validate --strict
```

## Output Formats

### Terminal Output (Rich)

```
Generating diagrams for: specs/035-auto-mermaid-diagrams/spec.md

┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Diagram Type   ┃ Status       ┃ Nodes    ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ User Journey   │ ✅ Generated │ 12       │
│ ER Diagram     │ ✅ Generated │ 6        │
└────────────────┴──────────────┴──────────┘

✅ Diagrams inserted into spec.md
```

### Validation Output

```
Validating diagrams in: specs/035-auto-mermaid-diagrams/spec.md

┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Diagram Type   ┃ Status       ┃ Issues                          ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ User Journey   │ ✅ Valid     │ None                            │
│ ER Diagram     │ ⚠️ Warning   │ Orphan entity: "TempData"       │
└────────────────┴──────────────┴─────────────────────────────────┘
```

## Service Interface

### DiagramService

```python
class DiagramService:
    """Service for generating Mermaid diagrams from specs."""

    def generate(
        self,
        file_path: Path,
        diagram_types: list[DiagramType] | None = None,
        strict: bool = False,
    ) -> DiagramResult:
        """Generate diagrams for a file.

        Args:
            file_path: Path to spec.md or plan.md
            diagram_types: Types to generate (default: all applicable)
            strict: If True, fail on validation errors

        Returns:
            DiagramResult with generated diagrams and status
        """
        ...

    def validate(
        self,
        content: str,
        diagram_type: DiagramType,
        strict: bool = False,
    ) -> ValidationResult:
        """Validate Mermaid diagram syntax.

        Args:
            content: Mermaid diagram content
            diagram_type: Type of diagram
            strict: If True, use mermaid-cli for canonical validation

        Returns:
            ValidationResult with pass/fail and any errors
        """
        ...

    def insert_diagram(
        self,
        file_path: Path,
        section_name: str,
        diagram_content: str,
    ) -> bool:
        """Insert or replace diagram in AUTO-GENERATED section.

        Args:
            file_path: Path to target file
            section_name: Section identifier (e.g., "user-journey")
            diagram_content: Mermaid diagram to insert

        Returns:
            True if successful, False if markers not found
        """
        ...
```

### Parser Interfaces

```python
class UserStoryParser:
    """Parses user stories from spec.md content."""

    def parse(self, content: str) -> list[ParsedUserStory]:
        """Parse all user stories from spec content."""
        ...

class EntityParser:
    """Parses Key Entities section from spec.md."""

    def parse(self, content: str) -> list[ParsedEntity]:
        """Parse all entities from spec content."""
        ...

class SectionParser:
    """Parses AUTO-GENERATED sections from files."""

    def find_sections(self, content: str) -> list[DiagramSection]:
        """Find all AUTO-GENERATED sections in content."""
        ...
```

### Generator Interfaces

```python
class UserJourneyGenerator:
    """Generates flowchart diagrams from user stories."""

    def generate(self, stories: list[ParsedUserStory]) -> str:
        """Generate Mermaid flowchart from user stories."""
        ...

class ERDiagramGenerator:
    """Generates ER diagrams from parsed entities."""

    def generate(self, entities: list[ParsedEntity]) -> str:
        """Generate Mermaid erDiagram from entities."""
        ...
```

## Error Messages

| Code | Message | Cause |
|------|---------|-------|
| E001 | "File not found: {path}" | Target file doesn't exist |
| E002 | "Not a spec or plan file: {path}" | File doesn't match expected format |
| E003 | "No user stories found" | User Stories section empty or malformed |
| E004 | "No entities found" | Key Entities section missing |
| E005 | "Validation failed: {errors}" | Mermaid syntax errors (strict mode) |
| E006 | "Section markers not found: {section}" | AUTO-GENERATED markers missing |
| W001 | "Skipped malformed story: {title}" | User story couldn't be parsed |
| W002 | "Orphan entity: {name}" | Entity has no relationships |
| W003 | "Diagram exceeds node limit: {count}" | Over 20 nodes (rendering may fail) |
