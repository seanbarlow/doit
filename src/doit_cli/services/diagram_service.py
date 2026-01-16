"""Main orchestration service for diagram generation."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.diagram_models import (
    DiagramResult,
    DiagramSection,
    DiagramType,
    GeneratedDiagram,
    ValidationResult,
)
from .entity_parser import EntityParser
from .er_diagram_generator import ERDiagramGenerator
from .mermaid_validator import MermaidValidator
from .section_parser import SectionParser
from .user_journey_generator import UserJourneyGenerator
from .user_story_parser import UserStoryParser


class DiagramService:
    """Service for generating Mermaid diagrams from specifications.

    Orchestrates the full workflow:
    1. Parse spec content (user stories, entities)
    2. Generate diagrams (flowcharts, ER diagrams)
    3. Validate Mermaid syntax
    4. Insert/replace in AUTO-GENERATED sections
    """

    # Section name mappings
    SECTION_NAMES = {
        DiagramType.USER_JOURNEY: "user-journey",
        DiagramType.ER_DIAGRAM: "entity-relationships",
        DiagramType.ARCHITECTURE: "architecture",
    }

    def __init__(self, strict: bool = False, backup: bool = True):
        """Initialize diagram service.

        Args:
            strict: If True, fail on validation errors
            backup: If True, create backup before modifying files
        """
        self.strict = strict
        self.backup = backup

        # Initialize components
        self.section_parser = SectionParser()
        self.user_story_parser = UserStoryParser()
        self.entity_parser = EntityParser()
        self.user_journey_generator = UserJourneyGenerator()
        self.er_diagram_generator = ERDiagramGenerator()
        self.validator = MermaidValidator()

    def generate(
        self,
        file_path: Path,
        diagram_types: Optional[list[DiagramType]] = None,
        insert: bool = True,
    ) -> DiagramResult:
        """Generate diagrams for a specification file.

        Args:
            file_path: Path to spec.md or plan.md file
            diagram_types: Types to generate (default: auto-detect applicable)
            insert: If True, insert diagrams into file

        Returns:
            DiagramResult with generated diagrams and status
        """
        result = DiagramResult(file_path=file_path)

        # Validate file exists
        if not file_path.exists():
            result.success = False
            result.error = f"File not found: {file_path}"
            return result

        # Read file content
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result.success = False
            result.error = f"Error reading file: {e}"
            return result

        # Find existing AUTO-GENERATED sections
        result.sections_found = self.section_parser.find_sections(content)

        # Auto-detect diagram types if not specified
        if diagram_types is None:
            diagram_types = self._detect_applicable_types(content)

        # Generate each diagram type
        for diagram_type in diagram_types:
            diagram = self._generate_diagram(content, diagram_type)
            if diagram:
                # Validate
                validation = self.validator.validate(
                    diagram.mermaid_content, diagram_type
                )
                diagram.validation = validation
                diagram.is_valid = validation.passed

                if self.strict and not validation.passed:
                    result.success = False
                    result.error = f"Validation failed for {diagram_type.value}: {validation.errors}"
                    return result

                result.diagrams.append(diagram)

        # Insert diagrams into file if requested
        if insert and result.diagrams:
            updated_content, sections_updated = self._insert_diagrams(
                content, result.diagrams
            )
            result.sections_updated = sections_updated

            if sections_updated:
                # Create backup and write file
                try:
                    self._write_file(file_path, updated_content)
                except Exception as e:
                    result.success = False
                    result.error = f"Error writing file: {e}"
                    return result

        return result

    def validate(
        self, content: str, diagram_type: Optional[DiagramType] = None
    ) -> ValidationResult:
        """Validate Mermaid diagram syntax.

        Args:
            content: Mermaid diagram content
            diagram_type: Type of diagram (auto-detected if None)

        Returns:
            ValidationResult with pass/fail and errors
        """
        return self.validator.validate(content, diagram_type)

    def insert_diagram(
        self, file_path: Path, section_name: str, diagram_content: str
    ) -> bool:
        """Insert or replace diagram in AUTO-GENERATED section.

        Args:
            file_path: Path to target file
            section_name: Section identifier (e.g., "user-journey")
            diagram_content: Mermaid diagram to insert (wrapped in code fence)

        Returns:
            True if successful, False if markers not found
        """
        if not file_path.exists():
            return False

        content = file_path.read_text(encoding="utf-8")

        # Check if section exists
        if not self.section_parser.has_section(content, section_name):
            return False

        # Replace section content
        updated_content, success = self.section_parser.replace_section_content(
            content, section_name, diagram_content
        )

        if success:
            self._write_file(file_path, updated_content)

        return success

    def _detect_applicable_types(self, content: str) -> list[DiagramType]:
        """Detect which diagram types are applicable for content.

        Args:
            content: File content

        Returns:
            List of applicable DiagramType values
        """
        types = []

        # Check for user stories
        if self.user_story_parser.count_stories(content) > 0:
            types.append(DiagramType.USER_JOURNEY)

        # Check for entities
        if self.entity_parser.count_entities(content) > 0:
            types.append(DiagramType.ER_DIAGRAM)

        return types

    def _generate_diagram(
        self, content: str, diagram_type: DiagramType
    ) -> Optional[GeneratedDiagram]:
        """Generate a single diagram type.

        Args:
            content: File content
            diagram_type: Type of diagram to generate

        Returns:
            GeneratedDiagram or None if content not found
        """
        if diagram_type == DiagramType.USER_JOURNEY:
            stories = self.user_story_parser.parse(content)
            if not stories:
                return None
            return self.user_journey_generator.generate_diagram(stories)

        elif diagram_type == DiagramType.ER_DIAGRAM:
            entities = self.entity_parser.parse(content)
            if not entities:
                return None
            return self.er_diagram_generator.generate_diagram(entities)

        elif diagram_type == DiagramType.ARCHITECTURE:
            # Architecture generation would be handled by ArchitectureGenerator
            # For now, return None (to be implemented in Phase 8)
            return None

        return None

    def _insert_diagrams(
        self, content: str, diagrams: list[GeneratedDiagram]
    ) -> tuple[str, list[str]]:
        """Insert diagrams into AUTO-GENERATED sections.

        Args:
            content: Original file content
            diagrams: List of generated diagrams

        Returns:
            Tuple of (updated content, list of section names updated)
        """
        updated_content = content
        sections_updated = []

        for diagram in diagrams:
            section_name = self.SECTION_NAMES.get(diagram.diagram_type)
            if not section_name:
                continue

            # Check if section exists
            if not self.section_parser.has_section(updated_content, section_name):
                # Try to find alternate section names
                alt_names = self._get_alternate_section_names(diagram.diagram_type)
                for alt_name in alt_names:
                    if self.section_parser.has_section(updated_content, alt_name):
                        section_name = alt_name
                        break
                else:
                    # Section not found, skip
                    continue

            # Replace section content
            wrapped_content = diagram.wrapped_content
            updated_content, success = self.section_parser.replace_section_content(
                updated_content, section_name, wrapped_content
            )

            if success:
                sections_updated.append(section_name)

        return updated_content, sections_updated

    def _get_alternate_section_names(self, diagram_type: DiagramType) -> list[str]:
        """Get alternate section names for a diagram type.

        Args:
            diagram_type: Type of diagram

        Returns:
            List of alternate section name possibilities
        """
        alternates = {
            DiagramType.USER_JOURNEY: ["user-journey", "userjourney", "user_journey", "flowchart"],
            DiagramType.ER_DIAGRAM: ["entity-relationships", "er-diagram", "erdiagram", "entities"],
            DiagramType.ARCHITECTURE: ["architecture", "arch", "system-architecture"],
        }
        return alternates.get(diagram_type, [])

    def _write_file(self, file_path: Path, content: str) -> None:
        """Write content to file with optional backup.

        Args:
            file_path: Path to write to
            content: Content to write
        """
        if self.backup and file_path.exists():
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.with_suffix(f".{timestamp}.bak")
            shutil.copy2(file_path, backup_path)

        # Write atomically by writing to temp file first
        temp_path = file_path.with_suffix(".tmp")
        try:
            temp_path.write_text(content, encoding="utf-8")
            temp_path.replace(file_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def get_diagram_content(
        self, file_path: Path, diagram_type: DiagramType
    ) -> Optional[str]:
        """Get existing diagram content from a file.

        Args:
            file_path: Path to file
            diagram_type: Type of diagram to find

        Returns:
            Diagram content if found, None otherwise
        """
        if not file_path.exists():
            return None

        content = file_path.read_text(encoding="utf-8")
        section_name = self.SECTION_NAMES.get(diagram_type)

        if not section_name:
            return None

        section = self.section_parser.find_section(content, section_name)
        if not section:
            return None

        return self.section_parser.extract_mermaid_from_section(section)
