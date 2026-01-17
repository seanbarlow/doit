"""Memory search service for searching across project context files.

This module provides the MemorySearchService for searching constitution,
roadmap, and spec files with relevance scoring and highlighting.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..models.search_models import (
    ContentSnippet,
    MemorySource,
    QueryType,
    SearchHistory,
    SearchQuery,
    SearchResult,
    SourceFilter,
    SourceType,
)
from .context_loader import ContextLoader, estimate_tokens, extract_keywords
from .query_interpreter import QueryInterpreter, InterpretedQuery


class MemorySearchService:
    """Service for searching across project memory files.

    Provides keyword search, natural language query interpretation,
    and relevance scoring for search results.
    """

    # Section bonuses for relevance scoring
    PRIORITY_SECTIONS = {
        "summary": 1.0,
        "vision": 1.0,
        "overview": 0.8,
        "requirements": 0.5,
        "functional requirements": 0.5,
    }

    def __init__(self, project_root: Path, console: Optional[Console] = None):
        """Initialize the memory search service.

        Args:
            project_root: Root directory of the project.
            console: Rich console for output (creates one if not provided).
        """
        self.project_root = project_root
        self.console = console or Console()
        self.context_loader = ContextLoader(project_root)
        self.query_interpreter = QueryInterpreter()
        self.history = SearchHistory()

    def _classify_source_type(self, path: Path) -> SourceType:
        """Classify a file path as governance or spec.

        Args:
            path: Path to the file.

        Returns:
            SourceType classification.
        """
        path_str = str(path).lower()
        if ".doit/memory" in path_str:
            return SourceType.GOVERNANCE
        return SourceType.SPEC

    def _get_files_for_filter(self, source_filter: SourceFilter) -> list[Path]:
        """Get files matching the source filter.

        Args:
            source_filter: Filter for source types.

        Returns:
            List of file paths to search.
        """
        if source_filter == SourceFilter.GOVERNANCE:
            return self.context_loader.get_memory_files()
        elif source_filter == SourceFilter.SPECS:
            return self.context_loader.get_spec_files()
        else:  # ALL
            return self.context_loader.get_all_searchable_files()

    def _find_section_for_line(self, content: str, line_number: int) -> str:
        """Find which section a line belongs to.

        Args:
            content: Full file content.
            line_number: Line number to check.

        Returns:
            Section name (lowercase) or empty string.
        """
        lines = content.splitlines()
        current_section = ""

        for i, line in enumerate(lines[:line_number], 1):
            if line.startswith("## "):
                current_section = line[3:].strip().lower()
            elif line.startswith("# ") and not current_section:
                current_section = line[2:].strip().lower()

        return current_section

    def _calculate_relevance_score(
        self,
        content: str,
        query_text: str,
        line_number: int,
        match_count: int,
        total_lines: int,
    ) -> float:
        """Calculate relevance score for a search result.

        Formula: score = (tf_score * 0.5) + (position_score * 0.3) + (section_bonus * 0.2)

        Args:
            content: Full file content.
            query_text: Original search query.
            line_number: Line where match was found.
            match_count: Number of matches in file.
            total_lines: Total lines in file.

        Returns:
            Relevance score between 0.0 and 1.0.
        """
        # Term frequency score (normalized)
        words = len(content.split())
        tf_score = min(1.0, match_count / max(words, 1) * 100)

        # Position score (earlier is better)
        if line_number <= 10:
            position_score = 1.0
        elif line_number <= 100:
            position_score = 0.5
        else:
            position_score = 0.3

        # Check if line is in a header
        lines = content.splitlines()
        if line_number <= len(lines):
            line = lines[line_number - 1]
            if line.startswith("#"):
                position_score = 1.0

        # Section bonus
        section = self._find_section_for_line(content, line_number)
        section_bonus = 0.0
        for key, bonus in self.PRIORITY_SECTIONS.items():
            if key in section:
                section_bonus = bonus
                break

        # Calculate final score
        score = (tf_score * 0.5) + (position_score * 0.3) + (section_bonus * 0.2)
        return min(1.0, max(0.0, score))

    def _extract_context(
        self, content: str, line_number: int, context_lines: int = 2
    ) -> tuple[str, str, str]:
        """Extract context around a matched line.

        Args:
            content: Full file content.
            line_number: Line where match was found (1-indexed).
            context_lines: Number of context lines before/after.

        Returns:
            Tuple of (context_before, matched_line, context_after).
        """
        lines = content.splitlines()
        idx = line_number - 1

        if idx < 0 or idx >= len(lines):
            return "", "", ""

        matched_line = lines[idx]

        start_idx = max(0, idx - context_lines)
        end_idx = min(len(lines), idx + context_lines + 1)

        context_before = "\n".join(lines[start_idx:idx])
        context_after = "\n".join(lines[idx + 1 : end_idx])

        return context_before, matched_line, context_after

    def search_keyword(
        self, query: SearchQuery
    ) -> tuple[list[SearchResult], list[MemorySource]]:
        """Search for keywords across memory files.

        Args:
            query: The search query with parameters.

        Returns:
            Tuple of (list of search results, list of memory sources).
        """
        results: list[SearchResult] = []
        sources: dict[str, MemorySource] = {}

        # Get files to search
        files = self._get_files_for_filter(query.source_filter)

        if not files:
            return results, list(sources.values())

        # Prepare search pattern
        pattern = query.query_text
        if query.query_type == QueryType.PHRASE:
            pattern = re.escape(pattern)
        elif query.query_type != QueryType.REGEX and not query.use_regex:
            # Escape special characters for keyword search
            pattern = re.escape(pattern)

        flags = 0 if query.case_sensitive else re.IGNORECASE

        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        # Search each file
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            lines = content.splitlines()
            source_type = self._classify_source_type(file_path)

            # Create memory source
            source = MemorySource.from_path(file_path, source_type)
            sources[source.id] = source

            # Find matches
            file_matches = []
            for i, line in enumerate(lines, 1):
                matches = list(regex.finditer(line))
                if matches:
                    for match in matches:
                        file_matches.append((i, match.group(), match.start(), match.end()))

            if not file_matches:
                continue

            # Calculate relevance for each match
            match_count = len(file_matches)
            for line_number, matched_text, start, end in file_matches:
                relevance = self._calculate_relevance_score(
                    content, query.query_text, line_number, match_count, len(lines)
                )

                context_before, matched_line, context_after = self._extract_context(
                    content, line_number
                )

                result = SearchResult(
                    query_id=query.id,
                    source_id=source.id,
                    relevance_score=relevance,
                    line_number=line_number,
                    matched_text=matched_text,
                    context_before=context_before,
                    context_after=context_after,
                )
                results.append(result)

        # Sort by relevance and limit results
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        results = results[: query.max_results]

        # Track in history
        self.history.add_query(query)

        return results, list(sources.values())

    def search_natural(
        self, query: SearchQuery
    ) -> tuple[list[SearchResult], list[MemorySource], InterpretedQuery]:
        """Search using natural language query interpretation.

        Args:
            query: The search query with natural language text.

        Returns:
            Tuple of (list of search results, list of memory sources, interpreted query).
        """
        # Interpret the natural language query
        interpreted = self.query_interpreter.interpret(query.query_text)

        # Get search terms from interpretation
        search_terms = interpreted.search_terms if interpreted.search_terms else interpreted.keywords

        if not search_terms:
            # Fall back to original query if no keywords extracted
            search_terms = [query.query_text]

        # Build a regex pattern that matches ANY of the search terms (OR)
        # This gives more flexible matching than an exact phrase search
        escaped_terms = [re.escape(term) for term in search_terms]
        search_pattern = "|".join(escaped_terms)

        # Create a regex query with interpreted terms
        keyword_query = SearchQuery(
            query_text=search_pattern,
            query_type=QueryType.REGEX,  # Use regex for OR matching
            source_filter=query.source_filter,
            max_results=query.max_results * 2,  # Get more results for relevance filtering
            case_sensitive=query.case_sensitive,
            use_regex=True,
        )

        # Execute keyword search
        results, sources = self.search_keyword(keyword_query)

        # Boost results that match section hints
        if interpreted.section_hints:
            for result in results:
                source = next((s for s in sources if s.id == result.source_id), None)
                if source:
                    try:
                        content = source.file_path.read_text(encoding="utf-8")
                        section = self._find_section_for_line(content, result.line_number)
                        for hint in interpreted.section_hints:
                            if hint.lower() in section:
                                # Boost score by 10%
                                result.relevance_score = min(1.0, result.relevance_score * 1.1)
                                break
                    except (OSError, UnicodeDecodeError):
                        pass

            # Re-sort after boosting
            results.sort(key=lambda r: r.relevance_score, reverse=True)

        # Limit to original max_results
        results = results[: query.max_results]

        # Track the original natural language query in history
        self.history.add_query(query)

        return results, sources, interpreted

    def search(
        self,
        query_text: str,
        query_type: QueryType = QueryType.KEYWORD,
        source_filter: SourceFilter = SourceFilter.ALL,
        max_results: int = 20,
        case_sensitive: bool = False,
        use_regex: bool = False,
    ) -> tuple[list[SearchResult], list[MemorySource], SearchQuery]:
        """Convenience method to search with individual parameters.

        Args:
            query_text: The search term or question.
            query_type: Type of query (keyword, phrase, natural, regex).
            source_filter: Filter for source types.
            max_results: Maximum results to return.
            case_sensitive: Enable case-sensitive matching.
            use_regex: Interpret query as regex.

        Returns:
            Tuple of (results, sources, query).
        """
        query = SearchQuery(
            query_text=query_text,
            query_type=query_type,
            source_filter=source_filter,
            max_results=max_results,
            case_sensitive=case_sensitive,
            use_regex=use_regex,
        )

        # Use natural language processing for NATURAL query type
        if query_type == QueryType.NATURAL:
            results, sources, interpreted = self.search_natural(query)
            # Store interpreted query info (could be used for display)
            query._interpreted = interpreted
        else:
            results, sources = self.search_keyword(query)

        return results, sources, query

    def format_result_rich(
        self,
        result: SearchResult,
        sources: dict[str, MemorySource],
        query_text: str,
    ) -> Panel:
        """Format a search result as a Rich panel.

        Args:
            result: The search result to format.
            sources: Dictionary of source ID to MemorySource.
            query_text: Original query text for highlighting.

        Returns:
            Rich Panel containing the formatted result.
        """
        source = sources.get(result.source_id)
        if not source:
            return Panel("Unknown source")

        # Build the content with highlighting
        text = Text()

        # Add context before
        if result.context_before:
            text.append(result.context_before + "\n", style="dim")

        # Add matched line with highlighting
        line_content = result.context_before.split("\n")[-1] if result.context_before else ""
        line_content = ""

        # Get the full matched line
        try:
            content = source.file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            if 0 < result.line_number <= len(lines):
                line_content = lines[result.line_number - 1]
        except (OSError, UnicodeDecodeError):
            line_content = result.matched_text

        # Highlight matches in the line
        highlighted = Text(line_content)
        try:
            pattern = re.compile(re.escape(query_text), re.IGNORECASE)
            for match in pattern.finditer(line_content):
                highlighted.stylize("bold yellow", match.start(), match.end())
        except re.error:
            pass

        text.append(highlighted)
        text.append("\n")

        # Add context after
        if result.context_after:
            text.append(result.context_after, style="dim")

        # Build title
        rel_path = source.file_path.relative_to(self.project_root)
        title = f"📄 {rel_path}:{result.line_number}"
        subtitle = f"Score: {result.relevance_score:.2f}"

        return Panel(
            text,
            title=title,
            subtitle=subtitle,
            border_style="blue",
            padding=(0, 1),
        )

    def format_results_json(
        self,
        results: list[SearchResult],
        sources: list[MemorySource],
        query: SearchQuery,
        execution_time_ms: int,
    ) -> dict:
        """Format search results as JSON.

        Args:
            results: List of search results.
            sources: List of memory sources.
            query: The search query.
            execution_time_ms: Search execution time in milliseconds.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        source_map = {s.id: s for s in sources}

        return {
            "query": {
                "id": query.id,
                "text": query.query_text,
                "type": query.query_type.value,
                "source_filter": query.source_filter.value,
                "case_sensitive": query.case_sensitive,
            },
            "results": [
                {
                    "id": r.id,
                    "source": {
                        "path": str(source_map[r.source_id].file_path.relative_to(self.project_root))
                        if r.source_id in source_map
                        else "unknown",
                        "type": source_map[r.source_id].source_type.value
                        if r.source_id in source_map
                        else "unknown",
                    },
                    "relevance_score": r.relevance_score,
                    "line_number": r.line_number,
                    "matched_text": r.matched_text,
                    "context": {
                        "before": r.context_before,
                        "match": r.matched_text,
                        "after": r.context_after,
                    },
                }
                for r in results
            ],
            "metadata": {
                "total_results": len(results),
                "files_searched": len(sources),
                "execution_time_ms": execution_time_ms,
            },
        }

    def get_history(self) -> SearchHistory:
        """Get the search history.

        Returns:
            The current search history.
        """
        return self.history

    def clear_history(self) -> None:
        """Clear the search history."""
        self.history.clear()
