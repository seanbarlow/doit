"""Unit tests for UserJourneyGenerator."""

import pytest

from doit_cli.models.diagram_models import AcceptanceScenario, ParsedUserStory
from doit_cli.services.user_journey_generator import UserJourneyGenerator


@pytest.fixture
def generator():
    """Create a UserJourneyGenerator instance."""
    return UserJourneyGenerator()


@pytest.fixture
def sample_stories():
    """Create sample parsed user stories."""
    return [
        ParsedUserStory(
            id="US1",
            story_number=1,
            title="Login Flow",
            priority="P1",
            description="User login functionality",
            scenarios=[
                AcceptanceScenario(
                    id="US1_S1",
                    scenario_number=1,
                    given_clause="user on login page",
                    when_clause="entering credentials",
                    then_clause="redirected to dashboard",
                ),
                AcceptanceScenario(
                    id="US1_S2",
                    scenario_number=2,
                    given_clause="user logged out",
                    when_clause="clicking login",
                    then_clause="form appears",
                ),
            ],
        ),
        ParsedUserStory(
            id="US2",
            story_number=2,
            title="Registration",
            priority="P2",
            description="New user registration",
            scenarios=[
                AcceptanceScenario(
                    id="US2_S1",
                    scenario_number=1,
                    given_clause="on registration page",
                    when_clause="submitting form",
                    then_clause="account created",
                ),
            ],
        ),
    ]


class TestUserJourneyGenerator:
    """Tests for UserJourneyGenerator class."""

    def test_generate_flowchart(self, generator, sample_stories):
        """Test basic flowchart generation."""
        result = generator.generate(sample_stories)

        assert "flowchart LR" in result
        assert "subgraph" in result
        assert "US1" in result
        assert "US2" in result

    def test_generate_empty_stories(self, generator):
        """Test generation with empty story list."""
        result = generator.generate([])
        assert result == ""

    def test_generate_diagram_object(self, generator, sample_stories):
        """Test GeneratedDiagram object creation."""
        diagram = generator.generate_diagram(sample_stories)

        assert diagram.diagram_type.value == "user-journey"
        assert diagram.is_valid
        assert diagram.node_count > 0
        assert "flowchart" in diagram.mermaid_content

    def test_subgraph_labels(self, generator, sample_stories):
        """Test subgraph labels include story info."""
        result = generator.generate(sample_stories)

        assert "US1 - Login Flow" in result
        assert "US2 - Registration" in result

    def test_node_id_uniqueness(self, generator, sample_stories):
        """Test that node IDs are unique."""
        result = generator.generate(sample_stories)

        # Check for unique node patterns
        assert "US1_A" in result or "US1_" in result
        assert "US2_A" in result or "US2_" in result

    def test_scenario_nodes(self, generator, sample_stories):
        """Test that scenarios create Given/When/Then nodes."""
        result = generator.generate(sample_stories)

        # Should have Given, When, Then nodes
        assert "_G[" in result or "Given" in result.lower() or "login page" in result
        assert "_W{" in result or "When" in result.lower() or "credentials" in result.lower()
        assert "_T[" in result or "Then" in result.lower() or "dashboard" in result.lower()

    def test_generate_simple(self, generator, sample_stories):
        """Test simplified flowchart generation."""
        result = generator.generate_simple(sample_stories)

        assert "flowchart LR" in result
        assert "US1" in result
        assert "US2" in result
        # Should have arrows between stories
        assert "-->" in result

    def test_escape_special_characters(self, generator):
        """Test that special characters are escaped in node labels."""
        stories = [
            ParsedUserStory(
                id="US1",
                story_number=1,
                title="Simple Title",
                priority="P1",
                scenarios=[
                    AcceptanceScenario(
                        id="US1_S1",
                        scenario_number=1,
                        given_clause='input with "quotes"',
                        when_clause="action",
                        then_clause="result [done]",
                    )
                ],
            )
        ]

        result = generator.generate(stories)
        # Quotes in node labels should be converted to single quotes
        assert "'quotes'" in result
        # Brackets in labels converted to parentheses
        assert "(done)" in result

    def test_truncate_long_labels(self, generator):
        """Test that long labels are truncated."""
        long_clause = "a" * 100

        stories = [
            ParsedUserStory(
                id="US1",
                story_number=1,
                title="Test",
                priority="P1",
                scenarios=[
                    AcceptanceScenario(
                        id="US1_S1",
                        scenario_number=1,
                        given_clause=long_clause,
                        when_clause="action",
                        then_clause="result",
                    )
                ],
            )
        ]

        result = generator.generate(stories)
        # Should be truncated with ellipsis
        assert "..." in result
