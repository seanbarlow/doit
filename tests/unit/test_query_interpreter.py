"""Unit tests for QueryInterpreter."""

import pytest

from doit_cli.services.query_interpreter import (
    InterpretedQuery,
    QueryInterpreter,
    QuestionType,
)


class TestQueryInterpreter:
    """Tests for QueryInterpreter class."""

    @pytest.fixture
    def interpreter(self):
        """Create a QueryInterpreter instance."""
        return QueryInterpreter()

    # Question Type Classification Tests

    def test_classify_what_question(self, interpreter):
        """Test classification of 'what' questions."""
        result = interpreter.interpret("What is the project vision?")
        assert result.question_type == QuestionType.WHAT

    def test_classify_why_question(self, interpreter):
        """Test classification of 'why' questions."""
        result = interpreter.interpret("Why are we using Python?")
        assert result.question_type == QuestionType.WHY

    def test_classify_how_question(self, interpreter):
        """Test classification of 'how' questions."""
        result = interpreter.interpret("How do I add a new feature?")
        assert result.question_type == QuestionType.HOW

    def test_classify_where_question(self, interpreter):
        """Test classification of 'where' questions."""
        result = interpreter.interpret("Where is the authentication module?")
        assert result.question_type == QuestionType.WHERE

    def test_classify_when_question(self, interpreter):
        """Test classification of 'when' questions."""
        result = interpreter.interpret("When is the deadline?")
        assert result.question_type == QuestionType.WHEN

    def test_classify_who_question(self, interpreter):
        """Test classification of 'who' questions."""
        result = interpreter.interpret("Who is responsible for testing?")
        assert result.question_type == QuestionType.WHO

    def test_classify_which_question(self, interpreter):
        """Test classification of 'which' questions."""
        result = interpreter.interpret("Which framework should we use?")
        assert result.question_type == QuestionType.WHICH

    def test_classify_unknown_question(self, interpreter):
        """Test classification of unrecognized questions."""
        result = interpreter.interpret("authentication module specs")
        assert result.question_type == QuestionType.UNKNOWN

    def test_classify_rationale_pattern(self, interpreter):
        """Test classification with 'rationale' pattern."""
        # Note: "What" at the start takes precedence over "rationale" mid-sentence
        result = interpreter.interpret("Tell me the rationale for this decision")
        assert result.question_type == QuestionType.WHY

    def test_classify_purpose_pattern(self, interpreter):
        """Test classification with 'purpose of' pattern."""
        result = interpreter.interpret("Tell me the purpose of this feature")
        assert result.question_type == QuestionType.WHY

    # Keyword Extraction Tests

    def test_extract_keywords_removes_stop_words(self, interpreter):
        """Test that stop words are removed from keywords."""
        result = interpreter.interpret("What is the project vision?")
        assert "is" not in result.keywords
        assert "the" not in result.keywords
        assert "what" not in result.keywords
        assert "project" in result.keywords
        assert "vision" in result.keywords

    def test_extract_keywords_preserves_order(self, interpreter):
        """Test that keyword order is preserved."""
        result = interpreter.interpret("authentication login system")
        assert result.keywords.index("authentication") < result.keywords.index("login")
        assert result.keywords.index("login") < result.keywords.index("system")

    def test_extract_keywords_removes_duplicates(self, interpreter):
        """Test that duplicate keywords are removed."""
        result = interpreter.interpret("user user authentication user")
        assert result.keywords.count("user") == 1

    def test_extract_keywords_removes_short_words(self, interpreter):
        """Test that very short words are removed."""
        result = interpreter.interpret("Go to API for DB")
        # 'Go', 'to', 'DB' are all 2 chars or less
        assert "go" not in result.keywords
        assert "to" not in result.keywords

    def test_extract_keywords_handles_punctuation(self, interpreter):
        """Test that punctuation is handled correctly."""
        result = interpreter.interpret("What's the vision? Let's see!")
        assert "vision" in result.keywords
        assert "lets" in result.keywords or "let" in result.keywords

    # Section Hints Tests

    def test_section_hints_for_vision(self, interpreter):
        """Test section hints for vision-related keywords."""
        result = interpreter.interpret("project vision")
        assert "Vision" in result.section_hints or "Project Vision" in result.section_hints

    def test_section_hints_for_requirements(self, interpreter):
        """Test section hints for requirement-related keywords."""
        result = interpreter.interpret("feature requirements")
        assert "Requirements" in result.section_hints or "Features" in result.section_hints

    def test_section_hints_for_architecture(self, interpreter):
        """Test section hints for architecture-related keywords."""
        result = interpreter.interpret("system architecture")
        assert "Architecture" in result.section_hints

    def test_section_hints_for_roadmap(self, interpreter):
        """Test section hints for roadmap-related keywords."""
        result = interpreter.interpret("project roadmap priorities")
        assert "Roadmap" in result.section_hints or "Priorities" in result.section_hints

    def test_no_section_hints_for_generic_query(self, interpreter):
        """Test that generic queries may not have section hints."""
        result = interpreter.interpret("hello world test")
        # Generic words shouldn't have specific section mappings
        assert len(result.section_hints) == 0

    # Search Terms Generation Tests

    def test_search_terms_include_keywords(self, interpreter):
        """Test that search terms include extracted keywords."""
        result = interpreter.interpret("project authentication")
        assert "project" in result.search_terms
        assert "authentication" in result.search_terms

    def test_search_terms_add_boosters_for_what_questions(self, interpreter):
        """Test that 'what' questions add relevant boosters."""
        result = interpreter.interpret("What is validation?")
        # Should add one of: definition, description, overview
        boosters = {"definition", "description", "overview"}
        assert any(b in result.search_terms for b in boosters)

    def test_search_terms_add_boosters_for_how_questions(self, interpreter):
        """Test that 'how' questions add relevant boosters."""
        result = interpreter.interpret("How do I deploy?")
        # Should add one of: steps, process, procedure, workflow
        boosters = {"steps", "process", "procedure", "workflow"}
        assert any(b in result.search_terms for b in boosters)

    def test_get_search_query_returns_space_separated(self, interpreter):
        """Test that get_search_query returns space-separated terms."""
        result = interpreter.interpret("project authentication")
        query = result.get_search_query()
        assert " " in query
        assert "project" in query
        assert "authentication" in query

    # Confidence Score Tests

    def test_confidence_higher_for_classified_questions(self, interpreter):
        """Test that classified questions have higher confidence."""
        what_result = interpreter.interpret("What is the vision?")
        unknown_result = interpreter.interpret("xyz abc")
        assert what_result.confidence > unknown_result.confidence

    def test_confidence_higher_with_section_hints(self, interpreter):
        """Test that queries with section hints have higher confidence."""
        with_hints = interpreter.interpret("project vision requirements")
        without_hints = interpreter.interpret("xyz abc def")
        assert with_hints.confidence > without_hints.confidence

    def test_confidence_bounded_zero_to_one(self, interpreter):
        """Test that confidence is always between 0 and 1."""
        queries = [
            "What is the project vision and requirements?",
            "xyz",
            "",
            "a b c d e f g h i j k l m n o p q r s t u v w x y z",
        ]
        for q in queries:
            result = interpreter.interpret(q)
            assert 0.0 <= result.confidence <= 1.0

    # Edge Cases Tests

    def test_empty_query(self, interpreter):
        """Test handling of empty query."""
        result = interpreter.interpret("")
        assert result.original_query == ""
        assert result.question_type == QuestionType.UNKNOWN
        assert result.keywords == []
        assert result.confidence == 0.0

    def test_none_query(self, interpreter):
        """Test handling of None query."""
        result = interpreter.interpret(None)
        assert result.original_query == ""
        assert result.confidence == 0.0

    def test_whitespace_only_query(self, interpreter):
        """Test handling of whitespace-only query."""
        result = interpreter.interpret("   ")
        # Whitespace is stripped for processing but original is preserved
        assert result.original_query == "   "
        assert result.keywords == []

    def test_preserves_original_query(self, interpreter):
        """Test that original query is preserved."""
        query = "What is the project VISION?"
        result = interpreter.interpret(query)
        assert result.original_query == query

    def test_case_insensitive_classification(self, interpreter):
        """Test that question classification is case-insensitive."""
        result1 = interpreter.interpret("WHAT is this?")
        result2 = interpreter.interpret("what is this?")
        result3 = interpreter.interpret("What Is This?")
        assert result1.question_type == QuestionType.WHAT
        assert result2.question_type == QuestionType.WHAT
        assert result3.question_type == QuestionType.WHAT

    # Custom Configuration Tests

    def test_add_custom_stop_word(self, interpreter):
        """Test adding a custom stop word."""
        interpreter.add_stop_word("custom")
        result = interpreter.interpret("custom authentication")
        assert "custom" not in result.keywords
        assert "authentication" in result.keywords

    def test_remove_stop_word(self, interpreter):
        """Test removing a stop word."""
        interpreter.remove_stop_word("the")
        result = interpreter.interpret("the authentication")
        assert "the" in result.keywords

    def test_add_custom_section_mapping(self, interpreter):
        """Test adding a custom section mapping."""
        interpreter.add_section_mapping("foobar", ["Custom Section", "Another Section"])
        result = interpreter.interpret("foobar test")
        assert "Custom Section" in result.section_hints


class TestInterpretedQuery:
    """Tests for InterpretedQuery dataclass."""

    def test_default_values(self):
        """Test default values for InterpretedQuery."""
        query = InterpretedQuery(original_query="test")
        assert query.question_type == QuestionType.UNKNOWN
        assert query.keywords == []
        assert query.section_hints == []
        assert query.search_terms == []
        assert query.confidence == 0.5

    def test_get_search_query_with_search_terms(self):
        """Test get_search_query when search_terms is set."""
        query = InterpretedQuery(
            original_query="test",
            search_terms=["term1", "term2"],
            keywords=["kw1", "kw2"],
        )
        assert query.get_search_query() == "term1 term2"

    def test_get_search_query_falls_back_to_keywords(self):
        """Test get_search_query falls back to keywords when search_terms is empty."""
        query = InterpretedQuery(
            original_query="test",
            search_terms=[],
            keywords=["kw1", "kw2"],
        )
        assert query.get_search_query() == "kw1 kw2"

    def test_get_search_query_empty(self):
        """Test get_search_query when both are empty."""
        query = InterpretedQuery(original_query="test")
        assert query.get_search_query() == ""
