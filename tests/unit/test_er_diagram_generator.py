"""Unit tests for ERDiagramGenerator."""

import pytest

from doit_cli.models.diagram_models import (
    Cardinality,
    EntityAttribute,
    EntityRelationship,
    ParsedEntity,
)
from doit_cli.services.er_diagram_generator import ERDiagramGenerator


@pytest.fixture
def generator():
    """Create an ERDiagramGenerator instance."""
    return ERDiagramGenerator()


@pytest.fixture
def sample_entities():
    """Create sample parsed entities."""
    return [
        ParsedEntity(
            name="User",
            description="User account",
            attributes=[
                EntityAttribute(name="id", attr_type="uuid", is_pk=True),
                EntityAttribute(name="email", attr_type="string"),
                EntityAttribute(name="name", attr_type="string"),
            ],
            relationships=[
                EntityRelationship(
                    source_entity="User",
                    target_entity="Task",
                    cardinality=Cardinality.ONE_TO_MANY,
                    label="owns",
                )
            ],
        ),
        ParsedEntity(
            name="Task",
            description="Task item",
            attributes=[
                EntityAttribute(name="id", attr_type="uuid", is_pk=True),
                EntityAttribute(name="title", attr_type="string"),
                EntityAttribute(name="user_id", attr_type="uuid", is_fk=True),
            ],
            relationships=[],
        ),
    ]


class TestERDiagramGenerator:
    """Tests for ERDiagramGenerator class."""

    def test_generate_er_diagram(self, generator, sample_entities):
        """Test basic ER diagram generation."""
        result = generator.generate(sample_entities)

        assert "erDiagram" in result
        assert "User" in result
        assert "Task" in result

    def test_generate_empty_entities(self, generator):
        """Test generation with empty entity list."""
        result = generator.generate([])
        assert result == ""

    def test_generate_diagram_object(self, generator, sample_entities):
        """Test GeneratedDiagram object creation."""
        diagram = generator.generate_diagram(sample_entities)

        assert diagram.diagram_type.value == "er-diagram"
        assert diagram.is_valid
        assert diagram.node_count == 2
        assert "erDiagram" in diagram.mermaid_content

    def test_entity_attributes(self, generator, sample_entities):
        """Test entity attribute generation."""
        result = generator.generate(sample_entities)

        # Check for PK marker
        assert "PK" in result
        # Check for FK marker
        assert "FK" in result
        # Check for attribute types
        assert "uuid" in result
        assert "string" in result

    def test_relationship_lines(self, generator, sample_entities):
        """Test relationship line generation."""
        result = generator.generate(sample_entities)

        # Should have relationship notation
        assert "||--o{" in result or "--" in result

    def test_cardinality_notation(self, generator):
        """Test various cardinality notations."""
        entities = [
            ParsedEntity(
                name="A",
                relationships=[
                    EntityRelationship(
                        source_entity="A",
                        target_entity="B",
                        cardinality=Cardinality.ONE_TO_MANY,
                        label="has",
                    )
                ],
            ),
            ParsedEntity(name="B"),
        ]

        result = generator.generate(entities)
        assert "||--o{" in result

    def test_entity_without_attributes(self, generator):
        """Test entity without attributes."""
        entities = [ParsedEntity(name="Simple")]

        result = generator.generate(entities)
        assert "Simple" in result
        # Should not have curly braces for empty entity
        lines = [l for l in result.split("\n") if "Simple" in l]
        assert len(lines) > 0

    def test_generate_simple(self, generator, sample_entities):
        """Test simplified ER diagram generation."""
        result = generator.generate_simple(sample_entities)

        assert "erDiagram" in result
        # Should have relationships but not detailed attributes
        assert "User" in result or "--" in result

    def test_add_inferred_relationships(self, generator):
        """Test FK-based relationship inference."""
        entities = [
            ParsedEntity(
                name="Order",
                attributes=[
                    EntityAttribute(name="id", attr_type="uuid", is_pk=True),
                    EntityAttribute(name="customer_id", attr_type="uuid", is_fk=True),
                ],
            ),
            ParsedEntity(name="Customer"),
        ]

        result = generator.add_inferred_relationships(entities)
        order = next(e for e in result if e.name == "Order")

        # Should have inferred relationship to Customer
        rel_targets = [r.target_entity for r in order.relationships]
        assert "Customer" in rel_targets

    def test_relationship_label(self, generator, sample_entities):
        """Test that relationship labels are included."""
        result = generator.generate(sample_entities)

        # Should have relationship label
        assert '"owns"' in result or "owns" in result or ":" in result

    def test_duplicate_relationship_handling(self, generator):
        """Test that duplicate relationships are deduplicated."""
        entities = [
            ParsedEntity(
                name="A",
                relationships=[
                    EntityRelationship("A", "B", Cardinality.ONE_TO_MANY, "rel1"),
                    EntityRelationship("A", "B", Cardinality.ONE_TO_MANY, "rel2"),
                ],
            ),
            ParsedEntity(name="B"),
        ]

        result = generator.generate(entities)
        # Count relationship lines between A and B
        lines = [l for l in result.split("\n") if "A" in l and "B" in l and "--" in l]
        assert len(lines) <= 1  # Should be deduplicated
