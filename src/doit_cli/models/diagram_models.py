"""Models for automatic Mermaid diagram generation."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class DiagramType(str, Enum):
    """Type of Mermaid diagram to generate.

    Values:
        USER_JOURNEY: Flowchart showing user story flows
        ER_DIAGRAM: Entity relationship diagram from Key Entities
        ARCHITECTURE: Architecture diagram from plan.md
    """

    USER_JOURNEY = "user-journey"
    ER_DIAGRAM = "er-diagram"
    ARCHITECTURE = "architecture"

    @classmethod
    def from_string(cls, value: str) -> "DiagramType":
        """Parse a diagram type string.

        Args:
            value: Type string (e.g., "user-journey", "er-diagram")

        Returns:
            Corresponding DiagramType enum value.

        Raises:
            ValueError: If value doesn't match any type.
        """
        normalized = value.lower().strip().replace("_", "-")
        mapping = {
            "user-journey": cls.USER_JOURNEY,
            "userjourney": cls.USER_JOURNEY,
            "flowchart": cls.USER_JOURNEY,
            "er-diagram": cls.ER_DIAGRAM,
            "erdiagram": cls.ER_DIAGRAM,
            "er": cls.ER_DIAGRAM,
            "architecture": cls.ARCHITECTURE,
            "arch": cls.ARCHITECTURE,
        }
        if normalized not in mapping:
            raise ValueError(f"Unknown diagram type: {value}")
        return mapping[normalized]


class Cardinality(str, Enum):
    """ER diagram relationship cardinality.

    Values map to Mermaid ER diagram notation.
    """

    ONE_TO_ONE = "||--||"
    ONE_TO_MANY = "||--o{"
    MANY_TO_ONE = "}o--||"
    MANY_TO_MANY = "}o--o{"
    ZERO_OR_ONE_TO_ONE = "|o--||"
    ONE_TO_ZERO_OR_ONE = "||--o|"
    ZERO_OR_ONE_TO_MANY = "|o--o{"
    ZERO_OR_MANY_TO_ONE = "}o--o|"

    @classmethod
    def from_keywords(cls, text: str) -> "Cardinality":
        """Infer cardinality from natural language keywords.

        Args:
            text: Description text containing relationship keywords

        Returns:
            Inferred Cardinality (defaults to ONE_TO_MANY if unclear)
        """
        text_lower = text.lower()

        # Check for many-to-many first
        if "many-to-many" in text_lower or "many to many" in text_lower:
            return cls.MANY_TO_MANY

        # Check for one-to-one
        if "has one" in text_lower or "one-to-one" in text_lower:
            return cls.ONE_TO_ONE

        # Check for belongs to (reverse relationship)
        if "belongs to" in text_lower:
            return cls.MANY_TO_ONE

        # Default for "has many", "contains", etc.
        if "has many" in text_lower or "contains" in text_lower or "owns" in text_lower:
            return cls.ONE_TO_MANY

        # Default to one-to-many for unrecognized patterns
        return cls.ONE_TO_MANY

    @property
    def mermaid_notation(self) -> str:
        """Return the Mermaid ER diagram notation."""
        return self.value


@dataclass
class AcceptanceScenario:
    """Represents a Given/When/Then acceptance scenario.

    Attributes:
        id: Unique ID (e.g., "US1_S1")
        scenario_number: Scenario number within story (1, 2, 3...)
        given_clause: Initial state condition
        when_clause: Action or trigger
        then_clause: Expected outcome
        raw_text: Original text from spec
    """

    id: str
    scenario_number: int
    given_clause: str
    when_clause: str
    then_clause: str
    raw_text: str = ""

    @property
    def node_label(self) -> str:
        """Generate a label suitable for flowchart node."""
        # Truncate to reasonable length for display
        max_len = 40
        given_short = (
            self.given_clause[:max_len] + "..."
            if len(self.given_clause) > max_len
            else self.given_clause
        )
        return given_short


@dataclass
class ParsedUserStory:
    """Structured representation of a user story extracted from spec.

    Attributes:
        id: Unique ID (e.g., "US1")
        story_number: Story number (1, 2, 3...)
        title: Brief title from header
        priority: Priority level (P1, P2, P3, P4)
        description: Full user story description
        scenarios: List of acceptance scenarios
        raw_text: Original markdown text
    """

    id: str
    story_number: int
    title: str
    priority: str
    description: str = ""
    scenarios: list[AcceptanceScenario] = field(default_factory=list)
    raw_text: str = ""

    @property
    def subgraph_id(self) -> str:
        """Generate unique subgraph ID for Mermaid flowchart."""
        return f"US{self.story_number}"

    @property
    def subgraph_label(self) -> str:
        """Generate subgraph label for Mermaid flowchart."""
        return f"US{self.story_number} - {self.title}"


@dataclass
class EntityAttribute:
    """Attribute within an entity definition.

    Attributes:
        name: Attribute name
        attr_type: Data type (string, int, uuid, etc.)
        is_pk: Primary key flag
        is_fk: Foreign key flag
    """

    name: str
    attr_type: str = "string"
    is_pk: bool = False
    is_fk: bool = False

    @property
    def mermaid_line(self) -> str:
        """Generate Mermaid ER attribute line."""
        pk_marker = " PK" if self.is_pk else ""
        fk_marker = " FK" if self.is_fk else ""
        return f"        {self.attr_type} {self.name}{pk_marker}{fk_marker}"


@dataclass
class EntityRelationship:
    """Relationship between two entities.

    Attributes:
        source_entity: Source entity name
        target_entity: Target entity name
        cardinality: Relationship cardinality
        label: Relationship label (verb phrase)
    """

    source_entity: str
    target_entity: str
    cardinality: Cardinality
    label: str = ""

    @property
    def mermaid_line(self) -> str:
        """Generate Mermaid ER relationship line."""
        label_part = f' : "{self.label}"' if self.label else ""
        return f"    {self.source_entity} {self.cardinality.mermaid_notation} {self.target_entity}{label_part}"


@dataclass
class ParsedEntity:
    """Structured representation of an entity from Key Entities section.

    Attributes:
        name: Entity name (e.g., "User")
        description: What the entity represents
        raw_text: Original markdown text
        attributes: Parsed attributes
        relationships: Relationships to other entities
    """

    name: str
    description: str = ""
    raw_text: str = ""
    attributes: list[EntityAttribute] = field(default_factory=list)
    relationships: list[EntityRelationship] = field(default_factory=list)

    @property
    def mermaid_entity_block(self) -> str:
        """Generate Mermaid ER entity block."""
        if not self.attributes:
            return f"    {self.name}"

        lines = [f"    {self.name} {{"]
        for attr in self.attributes:
            lines.append(attr.mermaid_line)
        lines.append("    }")
        return "\n".join(lines)


@dataclass
class DiagramSection:
    """Represents an AUTO-GENERATED section in a file.

    Attributes:
        section_name: Section identifier (e.g., "user-journey")
        start_line: Start line number (BEGIN marker)
        end_line: End line number (END marker)
        content: Content between markers
    """

    section_name: str
    start_line: int
    end_line: int
    content: str = ""

    @property
    def begin_marker(self) -> str:
        """Generate the BEGIN marker comment."""
        return f'<!-- BEGIN:AUTO-GENERATED section="{self.section_name}" -->'

    @property
    def end_marker(self) -> str:
        """Generate the END marker comment."""
        return "<!-- END:AUTO-GENERATED -->"


@dataclass
class ValidationResult:
    """Result of Mermaid syntax validation.

    Attributes:
        passed: Overall pass/fail
        errors: Syntax errors found
        warnings: Non-blocking warnings
    """

    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        """Number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Number of warnings."""
        return len(self.warnings)

    @property
    def is_valid(self) -> bool:
        """Alias for passed."""
        return self.passed


@dataclass
class GeneratedDiagram:
    """Result of diagram generation.

    Attributes:
        id: Unique diagram ID
        diagram_type: Type of diagram generated
        mermaid_content: Generated Mermaid syntax
        is_valid: Whether syntax validation passed
        validation: Detailed validation result
        node_count: Number of nodes/entities in diagram
    """

    id: str
    diagram_type: DiagramType
    mermaid_content: str
    is_valid: bool = True
    validation: Optional[ValidationResult] = None
    node_count: int = 0

    @property
    def wrapped_content(self) -> str:
        """Return content wrapped in Mermaid code fence."""
        return f"```mermaid\n{self.mermaid_content}\n```"


@dataclass
class DiagramResult:
    """Result of diagram generation operation.

    Attributes:
        file_path: Path to the file that was processed
        diagrams: List of generated diagrams
        sections_found: AUTO-GENERATED sections found in file
        sections_updated: Sections that were updated
        success: Overall success status
        error: Error message if failed
    """

    file_path: Path
    diagrams: list[GeneratedDiagram] = field(default_factory=list)
    sections_found: list[DiagramSection] = field(default_factory=list)
    sections_updated: list[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    @property
    def total_diagrams(self) -> int:
        """Total diagrams generated."""
        return len(self.diagrams)

    @property
    def valid_diagrams(self) -> int:
        """Count of valid diagrams."""
        return sum(1 for d in self.diagrams if d.is_valid)

    @property
    def total_nodes(self) -> int:
        """Total nodes across all diagrams."""
        return sum(d.node_count for d in self.diagrams)
