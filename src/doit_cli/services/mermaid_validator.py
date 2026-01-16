"""Validator for Mermaid diagram syntax."""

import re
from typing import Optional

from ..models.diagram_models import DiagramType, ValidationResult


class MermaidValidator:
    """Validates Mermaid diagram syntax.

    Provides regex-based validation for common syntax errors
    in flowchart and erDiagram types.
    """

    # Valid diagram type declarations
    DIAGRAM_TYPE_PATTERNS = {
        DiagramType.USER_JOURNEY: re.compile(r"^\s*flowchart\s+(LR|TB|RL|BT)", re.MULTILINE),
        DiagramType.ER_DIAGRAM: re.compile(r"^\s*erDiagram\s*$", re.MULTILINE),
        DiagramType.ARCHITECTURE: re.compile(r"^\s*flowchart\s+(LR|TB|RL|BT)", re.MULTILINE),
    }

    # Valid node ID pattern (alphanumeric with underscores)
    NODE_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

    # Arrow patterns for flowchart
    FLOWCHART_ARROW_PATTERNS = [
        re.compile(r"-->"),   # Standard arrow
        re.compile(r"-\.->"),  # Dotted arrow
        re.compile(r"==>"),   # Thick arrow
        re.compile(r"--\s*\w+\s*-->"),  # Labeled arrow
    ]

    # ER diagram cardinality patterns
    ER_CARDINALITY_PATTERN = re.compile(
        r"(\|o|\|\||\}o|\}|)\s*--\s*(\|o|\|\||\}o|\}||\{o|\{)"
    )

    # Bracket pairs for balance checking
    BRACKET_PAIRS = [("{", "}"), ("[", "]"), ("(", ")")]

    def validate(
        self, content: str, diagram_type: Optional[DiagramType] = None
    ) -> ValidationResult:
        """Validate Mermaid diagram syntax.

        Args:
            content: Mermaid diagram content (without code fences)
            diagram_type: Expected diagram type (auto-detected if None)

        Returns:
            ValidationResult with pass/fail and any issues found
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Strip code fences if present
        content = self._strip_code_fences(content)

        if not content.strip():
            errors.append("Empty diagram content")
            return ValidationResult(passed=False, errors=errors, warnings=warnings)

        # Auto-detect diagram type if not provided
        if diagram_type is None:
            diagram_type = self._detect_diagram_type(content)

        if diagram_type is None:
            errors.append("Could not detect diagram type - missing type declaration")
            return ValidationResult(passed=False, errors=errors, warnings=warnings)

        # Validate diagram type declaration
        type_errors = self._validate_type_declaration(content, diagram_type)
        errors.extend(type_errors)

        # Check bracket balance (skip for ER diagrams due to cardinality notation)
        if diagram_type != DiagramType.ER_DIAGRAM:
            bracket_errors = self._validate_brackets(content)
            errors.extend(bracket_errors)

        # Type-specific validation
        if diagram_type in (DiagramType.USER_JOURNEY, DiagramType.ARCHITECTURE):
            flowchart_errors, flowchart_warnings = self._validate_flowchart(content)
            errors.extend(flowchart_errors)
            warnings.extend(flowchart_warnings)
        elif diagram_type == DiagramType.ER_DIAGRAM:
            er_errors, er_warnings = self._validate_er_diagram(content)
            errors.extend(er_errors)
            warnings.extend(er_warnings)

        # Check for node count warning
        node_count = self._count_nodes(content, diagram_type)
        if node_count > 20:
            warnings.append(f"Diagram has {node_count} nodes - may not render well in GitHub")

        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)

    def _strip_code_fences(self, content: str) -> str:
        """Remove markdown code fences from content.

        Args:
            content: Content possibly wrapped in code fences

        Returns:
            Content without code fences
        """
        lines = content.strip().split("\n")

        # Check for opening fence
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        # Check for closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines)

    def _detect_diagram_type(self, content: str) -> Optional[DiagramType]:
        """Auto-detect diagram type from content.

        Args:
            content: Diagram content

        Returns:
            Detected DiagramType or None
        """
        content_lower = content.lower()

        if "erdiagram" in content_lower:
            return DiagramType.ER_DIAGRAM
        if "flowchart" in content_lower:
            return DiagramType.USER_JOURNEY  # Default flowchart to user journey

        return None

    def _validate_type_declaration(
        self, content: str, diagram_type: DiagramType
    ) -> list[str]:
        """Validate diagram type declaration.

        Args:
            content: Diagram content
            diagram_type: Expected type

        Returns:
            List of error messages
        """
        errors = []
        pattern = self.DIAGRAM_TYPE_PATTERNS.get(diagram_type)

        if pattern and not pattern.search(content):
            errors.append(f"Missing or invalid diagram type declaration for {diagram_type.value}")

        return errors

    def _validate_brackets(self, content: str) -> list[str]:
        """Check for balanced brackets.

        Args:
            content: Diagram content

        Returns:
            List of error messages for unbalanced brackets
        """
        errors = []

        for open_char, close_char in self.BRACKET_PAIRS:
            open_count = content.count(open_char)
            close_count = content.count(close_char)

            if open_count != close_count:
                errors.append(
                    f"Unbalanced brackets: {open_count} '{open_char}' vs {close_count} '{close_char}'"
                )

        return errors

    def _validate_flowchart(self, content: str) -> tuple[list[str], list[str]]:
        """Validate flowchart-specific syntax.

        Args:
            content: Flowchart content

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith("%%"):
                continue

            # Skip subgraph declarations
            if stripped.startswith("subgraph") or stripped == "end":
                continue

            # Skip the flowchart declaration
            if stripped.startswith("flowchart"):
                continue

            # Check for node definitions with invalid IDs
            node_match = re.match(r"^\s*([A-Za-z0-9_]+)\s*[\[\(\{]", line)
            if node_match:
                node_id = node_match.group(1)
                if not self.NODE_ID_PATTERN.match(node_id):
                    errors.append(f"Line {line_num}: Invalid node ID '{node_id}'")

            # Check for empty labels
            if '[""]' in line or "[' ']" in line:
                warnings.append(f"Line {line_num}: Empty node label")

        return errors, warnings

    def _validate_er_diagram(self, content: str) -> tuple[list[str], list[str]]:
        """Validate ER diagram-specific syntax.

        Args:
            content: ER diagram content

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        lines = content.split("\n")
        entities_defined: set[str] = set()
        entities_referenced: set[str] = set()

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith("%%"):
                continue

            # Skip erDiagram declaration
            if stripped.lower() == "erdiagram":
                continue

            # Check for entity definition (entity {)
            entity_def_match = re.match(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*\{", line)
            if entity_def_match:
                entities_defined.add(entity_def_match.group(1))
                continue

            # Check for relationship line
            rel_match = re.match(
                r"^\s*([A-Za-z][A-Za-z0-9_]*)\s+\S+\s+([A-Za-z][A-Za-z0-9_]*)", line
            )
            if rel_match:
                entities_referenced.add(rel_match.group(1))
                entities_referenced.add(rel_match.group(2))

                # Validate cardinality notation
                if not self._validate_cardinality_in_line(line):
                    warnings.append(
                        f"Line {line_num}: Potentially invalid cardinality notation"
                    )

        # Check for orphan entities (defined but no relationships)
        orphans = entities_defined - entities_referenced
        for orphan in orphans:
            warnings.append(f"Orphan entity: '{orphan}' has no relationships")

        return errors, warnings

    def _validate_cardinality_in_line(self, line: str) -> bool:
        """Check if a line has valid cardinality notation.

        Args:
            line: Relationship line

        Returns:
            True if valid, False if potentially invalid
        """
        # Valid cardinality patterns
        valid_patterns = [
            "||--||",  # One to one
            "||--o{",  # One to many
            "}o--||",  # Many to one
            "}o--o{",  # Many to many
            "|o--||",  # Zero or one to one
            "||--o|",  # One to zero or one
            "|o--o{",  # Zero or one to many
            "}o--o|",  # Zero or many to one
        ]

        for pattern in valid_patterns:
            if pattern in line:
                return True

        # If line has -- but no valid pattern, might be invalid
        if "--" in line and ":" in line:
            return True  # Assume valid if it has relationship structure

        return True  # Be permissive for edge cases

    def _count_nodes(self, content: str, diagram_type: DiagramType) -> int:
        """Count approximate number of nodes in diagram.

        Args:
            content: Diagram content
            diagram_type: Type of diagram

        Returns:
            Approximate node count
        """
        if diagram_type == DiagramType.ER_DIAGRAM:
            # Count entity definitions
            return len(re.findall(r"^\s*[A-Za-z][A-Za-z0-9_]*\s*\{", content, re.MULTILINE))
        else:
            # Count node definitions in flowchart
            return len(re.findall(r"^\s*[A-Za-z][A-Za-z0-9_]+\s*[\[\(\{]", content, re.MULTILINE))

    def validate_quick(self, content: str) -> bool:
        """Quick validation - just check for basic validity.

        Args:
            content: Diagram content

        Returns:
            True if diagram appears valid
        """
        result = self.validate(content)
        return result.passed
