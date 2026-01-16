"""Generator for ER diagrams from parsed entities."""

from ..models.diagram_models import (
    DiagramType,
    EntityRelationship,
    GeneratedDiagram,
    ParsedEntity,
)


class ERDiagramGenerator:
    """Generates Mermaid ER diagrams from parsed entities.

    Converts ParsedEntity objects into an erDiagram with entity
    definitions and relationship notations.
    """

    def generate(self, entities: list[ParsedEntity]) -> str:
        """Generate Mermaid erDiagram from entities.

        Args:
            entities: List of parsed entities

        Returns:
            Mermaid erDiagram syntax
        """
        if not entities:
            return ""

        lines = ["erDiagram"]

        # Collect all relationships first
        relationships = self._collect_relationships(entities)

        # Add relationship lines
        for rel in relationships:
            lines.append(rel.mermaid_line)

        # Add blank line between relationships and entities
        if relationships:
            lines.append("")

        # Add entity definitions
        for entity in entities:
            entity_lines = self._generate_entity_block(entity)
            lines.extend(entity_lines)

        return "\n".join(lines)

    def generate_diagram(self, entities: list[ParsedEntity]) -> GeneratedDiagram:
        """Generate a GeneratedDiagram object from entities.

        Args:
            entities: List of parsed entities

        Returns:
            GeneratedDiagram with content and metadata
        """
        content = self.generate(entities)

        return GeneratedDiagram(
            id="er-diagram",
            diagram_type=DiagramType.ER_DIAGRAM,
            mermaid_content=content,
            is_valid=True,
            node_count=len(entities),
        )

    def _collect_relationships(
        self, entities: list[ParsedEntity]
    ) -> list[EntityRelationship]:
        """Collect all unique relationships from entities.

        Args:
            entities: List of parsed entities

        Returns:
            Deduplicated list of relationships
        """
        relationships = []
        seen: set[tuple[str, str]] = set()

        entity_names = {e.name for e in entities}

        for entity in entities:
            for rel in entity.relationships:
                # Only include relationships where target exists
                if rel.target_entity not in entity_names:
                    continue

                # Deduplicate based on source-target pair
                key = (rel.source_entity, rel.target_entity)
                reverse_key = (rel.target_entity, rel.source_entity)

                if key not in seen and reverse_key not in seen:
                    relationships.append(rel)
                    seen.add(key)

        return relationships

    def _generate_entity_block(self, entity: ParsedEntity) -> list[str]:
        """Generate entity block with attributes.

        Args:
            entity: Parsed entity

        Returns:
            List of Mermaid syntax lines
        """
        if not entity.attributes:
            # Entity without attributes - just the name
            return [f"    {entity.name}"]

        lines = [f"    {entity.name} {{"]

        for attr in entity.attributes:
            pk_marker = " PK" if attr.is_pk else ""
            fk_marker = " FK" if attr.is_fk else ""
            lines.append(f"        {attr.attr_type} {attr.name}{pk_marker}{fk_marker}")

        lines.append("    }")
        return lines

    def generate_simple(self, entities: list[ParsedEntity]) -> str:
        """Generate a simplified ER diagram with just entities and relationships.

        No attribute details - useful for high-level overview.

        Args:
            entities: List of parsed entities

        Returns:
            Simplified Mermaid erDiagram syntax
        """
        if not entities:
            return ""

        lines = ["erDiagram"]

        # Add relationships
        relationships = self._collect_relationships(entities)
        for rel in relationships:
            lines.append(rel.mermaid_line)

        # Add orphan entities (no relationships)
        related_entities = set()
        for rel in relationships:
            related_entities.add(rel.source_entity)
            related_entities.add(rel.target_entity)

        for entity in entities:
            if entity.name not in related_entities:
                lines.append(f"    {entity.name}")

        return "\n".join(lines)

    def add_inferred_relationships(
        self, entities: list[ParsedEntity]
    ) -> list[ParsedEntity]:
        """Add inferred relationships based on naming conventions.

        Looks for FK patterns like user_id that reference other entities.

        Args:
            entities: List of parsed entities

        Returns:
            Entities with additional inferred relationships
        """
        from ..models.diagram_models import Cardinality

        entity_names_lower = {e.name.lower(): e.name for e in entities}

        for entity in entities:
            for attr in entity.attributes:
                if attr.is_fk and attr.name.endswith("_id"):
                    # Extract referenced entity name
                    ref_name = attr.name[:-3]  # Remove '_id'

                    if ref_name.lower() in entity_names_lower:
                        target = entity_names_lower[ref_name.lower()]

                        # Check if relationship already exists
                        existing = any(
                            r.target_entity == target for r in entity.relationships
                        )

                        if not existing and target != entity.name:
                            rel = EntityRelationship(
                                source_entity=entity.name,
                                target_entity=target,
                                cardinality=Cardinality.MANY_TO_ONE,
                                label="references",
                            )
                            entity.relationships.append(rel)

        return entities
