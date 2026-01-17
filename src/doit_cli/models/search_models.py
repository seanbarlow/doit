"""Search models for memory search and query functionality.

This module provides data models for the memory search feature, including
query types, search results, and memory sources.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
import uuid


class QueryType(str, Enum):
    """Type of search query."""

    KEYWORD = "keyword"  # Simple word/phrase search
    PHRASE = "phrase"  # Exact phrase (quoted)
    NATURAL = "natural"  # Natural language question
    REGEX = "regex"  # Regular expression


class SourceType(str, Enum):
    """Type of memory source file."""

    GOVERNANCE = "governance"  # constitution, roadmap, completed_roadmap
    SPEC = "spec"  # spec.md files


class SourceFilter(str, Enum):
    """Filter for source types to search."""

    ALL = "all"  # Search everything
    GOVERNANCE = "governance"  # Only governance files
    SPECS = "specs"  # Only spec files


@dataclass
class SearchQuery:
    """Represents a user's search request with all parameters.

    Attributes:
        id: Unique identifier (UUID)
        query_text: The search term or natural language question
        query_type: Type of query (KEYWORD, PHRASE, NATURAL, REGEX)
        timestamp: When the query was executed
        source_filter: Filter to specific source types (default: ALL)
        max_results: Maximum results to return (default: 20)
        case_sensitive: Case-sensitive matching (default: False)
        use_regex: Interpret query as regex (default: False)
    """

    query_text: str
    query_type: QueryType = QueryType.KEYWORD
    timestamp: datetime = field(default_factory=datetime.now)
    source_filter: SourceFilter = SourceFilter.ALL
    max_results: int = 20
    case_sensitive: bool = False
    use_regex: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate query after initialization."""
        if not self.query_text or not self.query_text.strip():
            raise ValueError("Query text cannot be empty")
        if len(self.query_text) > 500:
            raise ValueError("Query text exceeds maximum length of 500 characters")
        if not 1 <= self.max_results <= 100:
            raise ValueError("Max results must be between 1 and 100")


@dataclass
class SearchResult:
    """A single search match with context and scoring.

    Attributes:
        id: Unique identifier
        query_id: Reference to parent query
        source_id: Reference to source file
        relevance_score: Score between 0.0 and 1.0
        line_number: Line where match was found
        matched_text: The actual matched text
        context_before: Lines before the match
        context_after: Lines after the match
    """

    query_id: str
    source_id: str
    relevance_score: float
    line_number: int
    matched_text: str
    context_before: str = ""
    context_after: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate result after initialization."""
        if not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")


@dataclass
class MemorySource:
    """A searchable file in the project memory.

    Attributes:
        id: Unique identifier (file path hash)
        file_path: Absolute path to the file
        source_type: Classification (GOVERNANCE, SPEC)
        last_modified: File modification timestamp
        line_count: Total lines in file
        token_count: Estimated token count
    """

    file_path: Path
    source_type: SourceType
    last_modified: datetime = field(default_factory=datetime.now)
    line_count: int = 0
    token_count: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def from_path(cls, path: Path, source_type: SourceType) -> "MemorySource":
        """Create a MemorySource from a file path.

        Args:
            path: Path to the file
            source_type: Type of source (governance or spec)

        Returns:
            MemorySource instance
        """
        import hashlib

        file_id = hashlib.md5(str(path).encode()).hexdigest()[:16]
        last_modified = datetime.fromtimestamp(path.stat().st_mtime)

        content = path.read_text(encoding="utf-8")
        line_count = len(content.splitlines())

        # Estimate tokens (approximately 4 chars per token)
        token_count = max(1, len(content) // 4)

        return cls(
            id=file_id,
            file_path=path,
            source_type=source_type,
            last_modified=last_modified,
            line_count=line_count,
            token_count=token_count,
        )


@dataclass
class ContentSnippet:
    """A portion of text extracted for display.

    Attributes:
        id: Unique identifier
        source_id: Reference to source file
        content: The snippet text
        start_line: First line number
        end_line: Last line number
        highlights: Character positions to highlight [(start, end), ...]
    """

    source_id: str
    content: str
    start_line: int
    end_line: int
    highlights: list[tuple[int, int]] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    MAX_CONTENT_LENGTH = 1000

    def __post_init__(self):
        """Validate and truncate content if needed."""
        if len(self.content) > self.MAX_CONTENT_LENGTH:
            # Truncate at word boundary if possible
            truncated = self.content[: self.MAX_CONTENT_LENGTH]
            last_space = truncated.rfind(" ")
            if last_space > self.MAX_CONTENT_LENGTH - 100:
                truncated = truncated[:last_space]
            self.content = truncated + "..."


@dataclass
class SearchHistory:
    """Session-scoped history of queries.

    Attributes:
        session_id: Unique session identifier
        session_start: When session began
        entries: List of past queries
        max_entries: Maximum entries to keep (default: 10)
    """

    session_start: datetime = field(default_factory=datetime.now)
    entries: list[SearchQuery] = field(default_factory=list)
    max_entries: int = 10
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_query(self, query: SearchQuery) -> None:
        """Add a query to history, enforcing max entries.

        Args:
            query: The query to add
        """
        self.entries.append(query)
        # FIFO when limit reached
        while len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def clear(self) -> None:
        """Clear all history entries."""
        self.entries.clear()

    def get_recent(self, count: int = 10) -> list[SearchQuery]:
        """Get most recent queries.

        Args:
            count: Number of queries to return

        Returns:
            List of most recent queries (newest first)
        """
        return list(reversed(self.entries[-count:]))
