"""Natural language query interpretation for memory search.

This module provides the QueryInterpreter class that transforms natural
language questions into search queries by:
1. Classifying question types (what, why, how, where)
2. Extracting keywords by removing stop words
3. Identifying section hints for targeted searching
"""

import re
from dataclasses import dataclass, field
from enum import Enum


class QuestionType(str, Enum):
    """Classification of natural language question types."""

    WHAT = "what"  # Definitional questions
    WHY = "why"  # Rationale/reasoning questions
    HOW = "how"  # Procedural/process questions
    WHERE = "where"  # Location/reference questions
    WHEN = "when"  # Temporal questions
    WHO = "who"  # Entity/ownership questions
    WHICH = "which"  # Selection/choice questions
    UNKNOWN = "unknown"  # Unclassified questions


@dataclass
class InterpretedQuery:
    """Result of interpreting a natural language query.

    Attributes:
        original_query: The original natural language question.
        question_type: Classified type of question.
        keywords: Extracted keywords for search.
        section_hints: Suggested sections to prioritize.
        search_terms: Final search terms to use.
        confidence: Confidence score for interpretation (0.0-1.0).
    """

    original_query: str
    question_type: QuestionType = QuestionType.UNKNOWN
    keywords: list[str] = field(default_factory=list)
    section_hints: list[str] = field(default_factory=list)
    search_terms: list[str] = field(default_factory=list)
    confidence: float = 0.5

    def get_search_query(self) -> str:
        """Get the search query string from interpreted terms.

        Returns:
            Space-separated search terms.
        """
        return " ".join(self.search_terms) if self.search_terms else " ".join(self.keywords)


class QueryInterpreter:
    """Interprets natural language queries for memory search.

    This class transforms natural language questions into structured search
    queries by classifying question types, extracting keywords, and
    identifying section hints.

    Attributes:
        stop_words: Set of common words to filter out.
        question_patterns: Regex patterns for question classification.
        section_mappings: Mappings from keywords to section names.
    """

    # Common English stop words to filter out
    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "do",
        "does",
        "for",
        "from",
        "has",
        "have",
        "how",
        "i",
        "if",
        "in",
        "is",
        "it",
        "its",
        "me",
        "my",
        "no",
        "not",
        "of",
        "on",
        "or",
        "our",
        "should",
        "so",
        "than",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "to",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
        "would",
        "you",
        "your",
    }

    # Question word patterns for classification
    QUESTION_PATTERNS = {
        QuestionType.WHAT: [
            r"^what\s+",
            r"^what's\s+",
            r"^define\s+",
            r"^describe\s+",
            r"^explain\s+what",
        ],
        QuestionType.WHY: [
            r"^why\s+",
            r"^why's\s+",
            r"\breason\s+for\b",
            r"\brationale\b",
            r"\bpurpose\s+of\b",
        ],
        QuestionType.HOW: [
            r"^how\s+",
            r"^how's\s+",
            r"\bprocess\s+for\b",
            r"\bsteps\s+to\b",
            r"\bprocedure\b",
        ],
        QuestionType.WHERE: [
            r"^where\s+",
            r"^where's\s+",
            r"\blocated\b",
            r"\blocation\s+of\b",
            r"\bfind\s+the\b",
        ],
        QuestionType.WHEN: [
            r"^when\s+",
            r"^when's\s+",
            r"\btimeline\b",
            r"\bdeadline\b",
            r"\bschedule\b",
        ],
        QuestionType.WHO: [
            r"^who\s+",
            r"^who's\s+",
            r"\bresponsible\s+for\b",
            r"\bowner\s+of\b",
            r"\bauthor\b",
        ],
        QuestionType.WHICH: [
            r"^which\s+",
            r"\bchoose\s+between\b",
            r"\bselect\b",
            r"\bcompare\b",
        ],
    }

    # Mappings from topic keywords to section names
    SECTION_MAPPINGS = {
        # Vision-related keywords
        "vision": ["Vision", "Project Vision", "Overview"],
        "goal": ["Vision", "Goals", "Objectives"],
        "objective": ["Vision", "Goals", "Objectives"],
        "purpose": ["Vision", "Purpose", "Overview"],
        # Principles-related keywords
        "principle": ["Principles", "Guiding Principles", "Core Principles"],
        "value": ["Principles", "Values", "Core Values"],
        "standard": ["Standards", "Coding Standards", "Principles"],
        # Requirements-related keywords
        "requirement": ["Requirements", "Functional Requirements", "Non-Functional Requirements"],
        "feature": ["Features", "Requirements", "User Stories"],
        "user story": ["User Stories", "Requirements", "Features"],
        # Technical keywords
        "architecture": ["Architecture", "Technical Architecture", "System Design"],
        "technology": ["Technology Stack", "Tech Stack", "Technologies"],
        "stack": ["Technology Stack", "Tech Stack"],
        "api": ["API", "Endpoints", "Contracts"],
        "database": ["Database", "Data Model", "Schema"],
        # Process keywords
        "workflow": ["Workflow", "Process", "Procedures"],
        "process": ["Process", "Workflow", "Procedures"],
        "procedure": ["Procedures", "Process", "Steps"],
        # Roadmap keywords
        "priority": ["Priority", "Priorities", "Roadmap"],
        "roadmap": ["Roadmap", "Timeline", "Priorities"],
        "milestone": ["Milestones", "Roadmap", "Timeline"],
        "phase": ["Phases", "Timeline", "Roadmap"],
    }

    def __init__(self) -> None:
        """Initialize the query interpreter."""
        self.stop_words = self.STOP_WORDS.copy()

    def interpret(self, query: str) -> InterpretedQuery:
        """Interpret a natural language query.

        Args:
            query: The natural language question or query.

        Returns:
            InterpretedQuery with classification and extracted terms.
        """
        if not query or not query.strip():
            return InterpretedQuery(
                original_query=query or "",
                question_type=QuestionType.UNKNOWN,
                confidence=0.0,
            )

        query = query.strip()
        query_lower = query.lower()

        # Classify question type
        question_type, type_confidence = self._classify_question(query_lower)

        # Extract keywords
        keywords = self._extract_keywords(query_lower)

        # Identify section hints
        section_hints = self._identify_section_hints(keywords)

        # Generate search terms (prioritize important keywords)
        search_terms = self._generate_search_terms(keywords, question_type)

        # Calculate overall confidence
        confidence = self._calculate_confidence(
            keywords, section_hints, type_confidence
        )

        return InterpretedQuery(
            original_query=query,
            question_type=question_type,
            keywords=keywords,
            section_hints=section_hints,
            search_terms=search_terms,
            confidence=confidence,
        )

    def _classify_question(self, query: str) -> tuple[QuestionType, float]:
        """Classify the type of question.

        Args:
            query: Lowercase query string.

        Returns:
            Tuple of (QuestionType, confidence score).
        """
        for q_type, patterns in self.QUESTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    # Higher confidence for start-of-query matches
                    confidence = 0.9 if pattern.startswith("^") else 0.7
                    return q_type, confidence

        return QuestionType.UNKNOWN, 0.3

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract keywords by removing stop words.

        Args:
            query: Lowercase query string.

        Returns:
            List of extracted keywords.
        """
        # Remove punctuation except hyphens in compound words
        cleaned = re.sub(r"[^\w\s-]", " ", query)

        # Split into words
        words = cleaned.split()

        # Filter stop words and short words
        keywords = [
            word
            for word in words
            if word not in self.stop_words and len(word) > 2
        ]

        # Preserve order but remove duplicates
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords

    def _identify_section_hints(self, keywords: list[str]) -> list[str]:
        """Identify relevant sections based on keywords.

        Args:
            keywords: List of extracted keywords.

        Returns:
            List of section names to prioritize.
        """
        hints = set()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in self.SECTION_MAPPINGS:
                hints.update(self.SECTION_MAPPINGS[keyword_lower])

            # Check for partial matches
            for mapped_keyword, sections in self.SECTION_MAPPINGS.items():
                if mapped_keyword in keyword_lower or keyword_lower in mapped_keyword:
                    hints.update(sections)

        return list(hints)

    def _generate_search_terms(
        self, keywords: list[str], question_type: QuestionType
    ) -> list[str]:
        """Generate optimized search terms from keywords.

        Args:
            keywords: Extracted keywords.
            question_type: Classified question type.

        Returns:
            Optimized list of search terms.
        """
        if not keywords:
            return []

        # Start with all keywords
        search_terms = keywords.copy()

        # Add synonyms/related terms based on question type
        type_boosters = {
            QuestionType.WHAT: ["definition", "description", "overview"],
            QuestionType.WHY: ["reason", "rationale", "purpose", "because"],
            QuestionType.HOW: ["steps", "process", "procedure", "workflow"],
            QuestionType.WHERE: ["location", "file", "section", "path"],
            QuestionType.WHEN: ["timeline", "date", "schedule", "deadline"],
            QuestionType.WHO: ["owner", "responsible", "team", "author"],
            QuestionType.WHICH: ["compare", "options", "choose", "select"],
        }

        # Add one booster term if available and not already present
        if question_type in type_boosters:
            for booster in type_boosters[question_type]:
                if booster not in search_terms:
                    search_terms.append(booster)
                    break

        return search_terms

    def _calculate_confidence(
        self,
        keywords: list[str],
        section_hints: list[str],
        type_confidence: float,
    ) -> float:
        """Calculate overall interpretation confidence.

        Args:
            keywords: Extracted keywords.
            section_hints: Identified section hints.
            type_confidence: Confidence from question classification.

        Returns:
            Overall confidence score (0.0-1.0).
        """
        if not keywords:
            return 0.1

        # Base confidence from keyword extraction
        keyword_confidence = min(len(keywords) * 0.15, 0.5)

        # Bonus for finding section hints
        hint_bonus = 0.2 if section_hints else 0.0

        # Combine with type confidence
        total = (type_confidence * 0.4) + (keyword_confidence * 0.4) + hint_bonus

        return min(total, 1.0)

    def add_stop_word(self, word: str) -> None:
        """Add a custom stop word.

        Args:
            word: Word to add to stop words set.
        """
        self.stop_words.add(word.lower())

    def remove_stop_word(self, word: str) -> None:
        """Remove a word from stop words.

        Args:
            word: Word to remove from stop words set.
        """
        self.stop_words.discard(word.lower())

    def add_section_mapping(self, keyword: str, sections: list[str]) -> None:
        """Add a custom section mapping.

        Args:
            keyword: Keyword to map.
            sections: List of section names to associate.
        """
        self.SECTION_MAPPINGS[keyword.lower()] = sections
