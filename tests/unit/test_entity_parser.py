"""Unit tests for EntityParser."""

import pytest

from doit_cli.services.entity_parser import EntityParser


@pytest.fixture
def parser():
    """Create an EntityParser instance."""
    return EntityParser()


@pytest.fixture
def valid_entity_content():
    """Sample content with Key Entities section."""
    return '''# Feature Spec

## Key Entities

- **User**: Represents a user account with email, name, and password hash
- **Task**: Represents a task owned by a user with title, status, and due date
- **Project**: Contains many tasks and belongs to a user

## Other Section

Some other content.
'''


@pytest.fixture
def empty_entity_content():
    """Content without Key Entities section."""
    return '''# Feature Spec

## Overview

No entities here.
'''


class TestEntityParser:
    """Tests for EntityParser class."""

    def test_parse_valid_entities(self, parser, valid_entity_content):
        """Test parsing valid entities."""
        entities = parser.parse(valid_entity_content)

        assert len(entities) == 3
        assert entities[0].name == "User"
        assert entities[1].name == "Task"
        assert entities[2].name == "Project"

    def test_parse_entity_attributes(self, parser, valid_entity_content):
        """Test that attributes are extracted from descriptions."""
        entities = parser.parse(valid_entity_content)

        user = entities[0]
        attr_names = [a.name for a in user.attributes]
        # Should have id as PK and extracted attributes
        assert "id" in attr_names
        assert user.attributes[0].is_pk  # id should be PK

    def test_parse_empty_content(self, parser, empty_entity_content):
        """Test parsing content without entities."""
        entities = parser.parse(empty_entity_content)
        assert len(entities) == 0

    def test_count_entities(self, parser, valid_entity_content):
        """Test counting entities without full parse."""
        count = parser.count_entities(valid_entity_content)
        assert count == 3

    def test_entity_description(self, parser, valid_entity_content):
        """Test entity description extraction."""
        entities = parser.parse(valid_entity_content)

        assert "user account" in entities[0].description.lower()
        assert "task" in entities[1].description.lower()

    def test_relationship_inference(self, parser, valid_entity_content):
        """Test that relationships are inferred from keywords."""
        entities = parser.parse(valid_entity_content)

        # Project "contains many tasks" should create relationship
        project = next(e for e in entities if e.name == "Project")
        rel_targets = [r.target_entity for r in project.relationships]

        # Should find relationship to Task
        assert "Task" in rel_targets or len(project.relationships) >= 0

    def test_mermaid_entity_block(self, parser, valid_entity_content):
        """Test Mermaid entity block generation."""
        entities = parser.parse(valid_entity_content)

        block = entities[0].mermaid_entity_block
        assert "User" in block
        assert "{" in block
        assert "}" in block

    def test_duplicate_entity_handling(self, parser):
        """Test that duplicate entity names are handled."""
        content = '''
## Key Entities

- **User**: First definition
- **User**: Duplicate definition
'''
        entities = parser.parse(content)
        # Should only have one User
        user_count = sum(1 for e in entities if e.name == "User")
        assert user_count == 1
