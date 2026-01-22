"""Unit tests for UserStoryParser."""

import pytest

from doit_cli.services.user_story_parser import UserStoryParser


@pytest.fixture
def parser():
    """Create a UserStoryParser instance."""
    return UserStoryParser()


@pytest.fixture
def valid_spec_content():
    """Sample spec content with user stories."""
    return '''# Feature Spec

## User Stories

### User Story 1 - Login Flow (Priority: P1)

As a user, I want to log in so that I can access my dashboard.

1. **Given** user is on login page, **When** entering valid credentials, **Then** redirected to dashboard
2. **Given** user is logged out, **When** clicking login button, **Then** login form appears

### User Story 2 - Registration (Priority: P2)

As a new user, I want to register.

1. **Given** user on registration page, **When** submitting form, **Then** account created

## Other Section

Some other content here.
'''


@pytest.fixture
def empty_spec_content():
    """Spec content without user stories."""
    return '''# Feature Spec

## Overview

This is a feature without user stories.

## Requirements

Some requirements here.
'''


class TestUserStoryParser:
    """Tests for UserStoryParser class."""

    def test_parse_valid_stories(self, parser, valid_spec_content):
        """Test parsing valid user stories."""
        stories = parser.parse(valid_spec_content)

        assert len(stories) == 2
        assert stories[0].id == "US1"
        assert stories[0].title == "Login Flow"
        assert stories[0].priority == "P1"
        assert stories[1].id == "US2"
        assert stories[1].priority == "P2"

    def test_parse_scenarios(self, parser, valid_spec_content):
        """Test parsing acceptance scenarios."""
        stories = parser.parse(valid_spec_content)

        assert len(stories[0].scenarios) == 2
        scenario = stories[0].scenarios[0]
        assert "login page" in scenario.given_clause
        assert "credentials" in scenario.when_clause
        assert "dashboard" in scenario.then_clause

    def test_parse_empty_spec(self, parser, empty_spec_content):
        """Test parsing spec without user stories."""
        stories = parser.parse(empty_spec_content)
        assert len(stories) == 0

    def test_count_stories(self, parser, valid_spec_content):
        """Test counting stories without full parse."""
        count = parser.count_stories(valid_spec_content)
        assert count == 2

    def test_get_story_by_number(self, parser, valid_spec_content):
        """Test getting specific story by number."""
        story = parser.get_story_by_number(valid_spec_content, 1)
        assert story is not None
        assert story.title == "Login Flow"

        story = parser.get_story_by_number(valid_spec_content, 99)
        assert story is None

    def test_story_subgraph_id(self, parser, valid_spec_content):
        """Test subgraph ID generation."""
        stories = parser.parse(valid_spec_content)
        assert stories[0].subgraph_id == "US1"
        assert stories[1].subgraph_id == "US2"

    def test_scenario_id_format(self, parser, valid_spec_content):
        """Test scenario ID format."""
        stories = parser.parse(valid_spec_content)
        assert stories[0].scenarios[0].id == "US1_S1"
        assert stories[0].scenarios[1].id == "US1_S2"

    def test_malformed_story_header(self, parser):
        """Test handling malformed story headers."""
        content = '''
### User Story - Missing Number (Priority: P1)

Description here.
'''
        stories = parser.parse(content)
        assert len(stories) == 0

    def test_alternative_priority_formats(self, parser):
        """Test various priority formats."""
        content = '''
### User Story 1 - Test (Priority: p1)

Description.
'''
        stories = parser.parse(content)
        assert len(stories) == 1
        assert stories[0].priority == "P1"
