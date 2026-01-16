"""Parser for Key Entities section from spec.md files."""

import re
from typing import Optional

from ..models.diagram_models import (
    Cardinality,
    EntityAttribute,
    EntityRelationship,
    ParsedEntity,
)


class EntityParser:
    """Parses Key Entities section from spec.md content.

    Extracts entity names, descriptions, attributes, and relationships
    from the Key Entities markdown section.
    """

    # Pattern for Key Entities section header
    SECTION_HEADER_PATTERN = re.compile(
        r"^##\s*Key\s+Entities\s*$|^###\s*Key\s+Entities\s*$", re.IGNORECASE | re.MULTILINE
    )

    # Pattern for entity bullet: - **EntityName**: Description
    ENTITY_PATTERN = re.compile(
        r"^[-*]\s+\*\*([A-Za-z][A-Za-z0-9_]*)\*\*:\s*(.+)$", re.MULTILINE
    )

    # Patterns for inferring relationships
    RELATIONSHIP_PATTERNS = [
        (re.compile(r"has\s+many\s+(\w+)", re.IGNORECASE), Cardinality.ONE_TO_MANY),
        (re.compile(r"contains\s+(\w+)", re.IGNORECASE), Cardinality.ONE_TO_MANY),
        (re.compile(r"owns\s+(\w+)", re.IGNORECASE), Cardinality.ONE_TO_MANY),
        (re.compile(r"has\s+one\s+(\w+)", re.IGNORECASE), Cardinality.ONE_TO_ONE),
        (re.compile(r"belongs\s+to\s+(\w+)", re.IGNORECASE), Cardinality.MANY_TO_ONE),
        (re.compile(r"references?\s+(\w+)", re.IGNORECASE), Cardinality.MANY_TO_ONE),
        (re.compile(r"many-to-many\s+(?:with\s+)?(\w+)", re.IGNORECASE), Cardinality.MANY_TO_MANY),
    ]

    # Pattern for common attribute types
    ATTRIBUTE_TYPE_PATTERNS = [
        (re.compile(r"\b(id|uuid|identifier)\b", re.IGNORECASE), "uuid", True, False),
        (re.compile(r"\b(email)\b", re.IGNORECASE), "string", False, False),
        (re.compile(r"\b(name|title|description|text|label)\b", re.IGNORECASE), "string", False, False),
        (re.compile(r"\b(password|hash|token|secret)\b", re.IGNORECASE), "string", False, False),
        (re.compile(r"\b(count|number|quantity|amount)\b", re.IGNORECASE), "int", False, False),
        (re.compile(r"\b(price|cost|rate)\b", re.IGNORECASE), "decimal", False, False),
        (re.compile(r"\b(date|time|timestamp|created|updated)\b", re.IGNORECASE), "datetime", False, False),
        (re.compile(r"\b(status|state|type)\b", re.IGNORECASE), "string", False, False),
        (re.compile(r"\b(active|enabled|is_|has_)\b", re.IGNORECASE), "boolean", False, False),
        (re.compile(r"\b(\w+)_id\b", re.IGNORECASE), "uuid", False, True),  # FK pattern
    ]

    def parse(self, content: str) -> list[ParsedEntity]:
        """Parse all entities from spec content.

        Args:
            content: Full content of spec.md file

        Returns:
            List of ParsedEntity objects
        """
        # Find Key Entities section
        section_content = self._extract_key_entities_section(content)
        if not section_content:
            return []

        entities = []
        entity_names: set[str] = set()

        # Find all entity definitions
        for match in self.ENTITY_PATTERN.finditer(section_content):
            entity_name = match.group(1).strip()
            description = match.group(2).strip()

            # Avoid duplicates
            if entity_name in entity_names:
                continue
            entity_names.add(entity_name)

            # Parse attributes from description
            attributes = self._extract_attributes(entity_name, description)

            # Parse relationships from description
            relationships = self._extract_relationships(entity_name, description, entity_names)

            entity = ParsedEntity(
                name=entity_name,
                description=description,
                raw_text=match.group(0),
                attributes=attributes,
                relationships=[],  # Will be populated in second pass
            )
            entities.append(entity)

        # Second pass: resolve relationships now that we know all entities
        self._resolve_relationships(entities)

        return entities

    def _extract_key_entities_section(self, content: str) -> Optional[str]:
        """Extract the Key Entities section from content.

        Args:
            content: Full file content

        Returns:
            Key Entities section content, or None if not found
        """
        match = self.SECTION_HEADER_PATTERN.search(content)
        if not match:
            return None

        start_pos = match.end()

        # Find next section header
        next_section = re.search(r"^##\s+[^#]", content[start_pos:], re.MULTILINE)
        if next_section:
            end_pos = start_pos + next_section.start()
        else:
            end_pos = len(content)

        return content[start_pos:end_pos]

    def _extract_attributes(self, entity_name: str, description: str) -> list[EntityAttribute]:
        """Extract attributes from entity description.

        Args:
            entity_name: Name of the entity
            description: Entity description text

        Returns:
            List of EntityAttribute objects
        """
        attributes = []
        found_attrs: set[str] = set()

        # Always add an id attribute as PK
        attributes.append(
            EntityAttribute(name="id", attr_type="uuid", is_pk=True, is_fk=False)
        )
        found_attrs.add("id")

        # Look for attribute mentions in description
        words = re.findall(r"\b([a-z][a-z0-9_]*)\b", description.lower())

        for word in words:
            if word in found_attrs or word in ("the", "and", "or", "with", "for", "has", "is", "a", "an"):
                continue

            for pattern, attr_type, is_pk, is_fk in self.ATTRIBUTE_TYPE_PATTERNS:
                if pattern.search(word):
                    # Use the actual word as attribute name
                    attr_name = word
                    if attr_name not in found_attrs:
                        attributes.append(
                            EntityAttribute(
                                name=attr_name,
                                attr_type=attr_type,
                                is_pk=is_pk and len(attributes) == 0,
                                is_fk=is_fk,
                            )
                        )
                        found_attrs.add(attr_name)
                    break

        return attributes

    def _extract_relationships(
        self, entity_name: str, description: str, known_entities: set[str]
    ) -> list[tuple[str, Cardinality, str]]:
        """Extract relationships from entity description.

        Args:
            entity_name: Source entity name
            description: Entity description text
            known_entities: Set of known entity names

        Returns:
            List of (target_entity, cardinality, label) tuples
        """
        relationships = []

        for pattern, cardinality in self.RELATIONSHIP_PATTERNS:
            matches = pattern.finditer(description)
            for match in matches:
                target_name = match.group(1)

                # Normalize target name
                target_normalized = self._normalize_entity_name(target_name)

                # Generate label from match
                label = self._generate_relationship_label(match.group(0))

                relationships.append((target_normalized, cardinality, label))

        return relationships

    def _resolve_relationships(self, entities: list[ParsedEntity]) -> None:
        """Resolve relationships between entities.

        Updates each entity's relationships list based on descriptions.

        Args:
            entities: List of entities to process
        """
        entity_names = {e.name.lower(): e.name for e in entities}

        for entity in entities:
            relationships = self._extract_relationships(
                entity.name, entity.description, set(entity_names.keys())
            )

            for target_name, cardinality, label in relationships:
                # Try to match target to known entity
                target_lower = target_name.lower()

                # Check exact match
                if target_lower in entity_names:
                    actual_target = entity_names[target_lower]
                else:
                    # Try singular/plural matching
                    singular = target_lower.rstrip("s")
                    plural = target_lower + "s"

                    if singular in entity_names:
                        actual_target = entity_names[singular]
                    elif plural in entity_names:
                        actual_target = entity_names[plural]
                    else:
                        # Target not found in known entities, skip
                        continue

                # Avoid self-references unless explicit
                if actual_target == entity.name:
                    continue

                rel = EntityRelationship(
                    source_entity=entity.name,
                    target_entity=actual_target,
                    cardinality=cardinality,
                    label=label,
                )
                entity.relationships.append(rel)

    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity name to PascalCase.

        Args:
            name: Raw entity name

        Returns:
            PascalCase entity name
        """
        # Remove pluralization
        if name.endswith("s") and not name.endswith("ss"):
            name = name[:-1]

        # Capitalize first letter
        return name[0].upper() + name[1:] if name else name

    def _generate_relationship_label(self, match_text: str) -> str:
        """Generate a relationship label from match text.

        Args:
            match_text: The matched relationship text

        Returns:
            Short label for the relationship
        """
        # Extract verb phrase
        text = match_text.lower()

        if "has many" in text or "contains" in text:
            return "has"
        if "has one" in text:
            return "has"
        if "belongs to" in text:
            return "belongs_to"
        if "owns" in text:
            return "owns"
        if "reference" in text:
            return "references"

        return ""

    def count_entities(self, content: str) -> int:
        """Count entities in content without full parsing.

        Args:
            content: Spec content to check

        Returns:
            Number of entities found
        """
        section = self._extract_key_entities_section(content)
        if not section:
            return 0
        return len(self.ENTITY_PATTERN.findall(section))
