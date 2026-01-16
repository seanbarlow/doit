"""Generator for Architecture diagrams from plan.md files."""

import re
from dataclasses import dataclass, field
from typing import Optional

from ..models.diagram_models import DiagramType, GeneratedDiagram


@dataclass
class ComponentInfo:
    """Information about an architecture component.

    Attributes:
        name: Component name
        layer: Layer it belongs to (CLI, Service, Model, etc.)
        description: Component description
        dependencies: Other components it depends on
    """

    name: str
    layer: str = ""
    description: str = ""
    dependencies: list[str] = field(default_factory=list)


class ArchitectureGenerator:
    """Generates Mermaid architecture diagrams from plan.md content.

    Parses Technical Context and Project Structure sections to create
    a flowchart showing system layers and component relationships.
    """

    # Pattern for project structure code blocks
    STRUCTURE_PATTERN = re.compile(
        r"```(?:text)?\s*\n((?:src/|tests/).*?)```", re.DOTALL
    )

    # Pattern for extracting file paths from structure
    FILE_PATTERN = re.compile(r"^[\s│├└─]*([a-zA-Z_][a-zA-Z0-9_/]*\.py)", re.MULTILINE)

    # Layer classification patterns
    LAYER_PATTERNS = [
        (re.compile(r"cli/|command", re.IGNORECASE), "CLI Layer"),
        (re.compile(r"services?/", re.IGNORECASE), "Service Layer"),
        (re.compile(r"models?/", re.IGNORECASE), "Data Layer"),
        (re.compile(r"tests?/unit", re.IGNORECASE), "Unit Tests"),
        (re.compile(r"tests?/integration", re.IGNORECASE), "Integration Tests"),
        (re.compile(r"formatters?/", re.IGNORECASE), "Formatters"),
        (re.compile(r"prompts?/", re.IGNORECASE), "Prompts"),
        (re.compile(r"rules?/", re.IGNORECASE), "Rules"),
    ]

    def __init__(self, direction: str = "TB"):
        """Initialize generator.

        Args:
            direction: Flowchart direction (TB, LR, etc.)
        """
        self.direction = direction

    def generate(self, content: str) -> str:
        """Generate Mermaid architecture diagram from plan.md content.

        Args:
            content: Full content of plan.md file

        Returns:
            Mermaid flowchart syntax
        """
        components = self._extract_components(content)
        if not components:
            return ""

        # Group components by layer
        layers: dict[str, list[ComponentInfo]] = {}
        for comp in components:
            layer = comp.layer or "Other"
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(comp)

        # Generate diagram
        lines = [f"flowchart {self.direction}"]

        # Add subgraphs for each layer
        layer_order = [
            "CLI Layer",
            "Service Layer",
            "Data Layer",
            "Formatters",
            "Rules",
            "Prompts",
            "Unit Tests",
            "Integration Tests",
            "Other",
        ]

        for layer_name in layer_order:
            if layer_name not in layers:
                continue

            layer_id = self._to_id(layer_name)
            lines.append(f'    subgraph {layer_id}["{layer_name}"]')

            for comp in layers[layer_name]:
                comp_id = self._to_id(comp.name)
                lines.append(f'        {comp_id}["{comp.name}"]')

            lines.append("    end")
            lines.append("")

        # Add connections based on common patterns
        connections = self._infer_connections(components)
        if connections:
            lines.append("    %% Component connections")
            for source, target in connections:
                source_id = self._to_id(source)
                target_id = self._to_id(target)
                lines.append(f"    {source_id} --> {target_id}")

        return "\n".join(lines)

    def generate_diagram(self, content: str) -> GeneratedDiagram:
        """Generate a GeneratedDiagram object from plan content.

        Args:
            content: Plan.md content

        Returns:
            GeneratedDiagram with content and metadata
        """
        mermaid_content = self.generate(content)

        # Count components
        components = self._extract_components(content)

        return GeneratedDiagram(
            id="architecture",
            diagram_type=DiagramType.ARCHITECTURE,
            mermaid_content=mermaid_content,
            is_valid=bool(mermaid_content),
            node_count=len(components),
        )

    def _extract_components(self, content: str) -> list[ComponentInfo]:
        """Extract component information from plan content.

        Args:
            content: Plan content

        Returns:
            List of ComponentInfo objects
        """
        components = []
        seen_names: set[str] = set()

        # Find project structure blocks
        for match in self.STRUCTURE_PATTERN.finditer(content):
            structure_text = match.group(1)

            # Extract file paths
            for file_match in self.FILE_PATTERN.finditer(structure_text):
                file_path = file_match.group(1)

                # Get component name from filename
                name = self._path_to_component_name(file_path)
                if name in seen_names or name == "__init__":
                    continue
                seen_names.add(name)

                # Determine layer
                layer = self._classify_layer(file_path)

                components.append(
                    ComponentInfo(name=name, layer=layer, description="")
                )

        return components

    def _path_to_component_name(self, path: str) -> str:
        """Convert file path to component name.

        Args:
            path: File path (e.g., "src/doit_cli/services/diagram_service.py")

        Returns:
            Component name (e.g., "DiagramService")
        """
        # Get filename without extension
        filename = path.split("/")[-1].replace(".py", "")

        # Convert snake_case to PascalCase
        parts = filename.split("_")
        return "".join(part.capitalize() for part in parts)

    def _classify_layer(self, path: str) -> str:
        """Classify which layer a file belongs to.

        Args:
            path: File path

        Returns:
            Layer name
        """
        for pattern, layer_name in self.LAYER_PATTERNS:
            if pattern.search(path):
                return layer_name
        return "Other"

    def _to_id(self, name: str) -> str:
        """Convert name to valid Mermaid node ID.

        Args:
            name: Component or layer name

        Returns:
            Valid node ID
        """
        # Remove spaces and special characters
        clean = re.sub(r"[^A-Za-z0-9]", "", name)
        return clean

    def _infer_connections(
        self, components: list[ComponentInfo]
    ) -> list[tuple[str, str]]:
        """Infer connections between components based on naming patterns.

        Args:
            components: List of components

        Returns:
            List of (source, target) connection tuples
        """
        connections = []
        comp_names = {c.name for c in components}

        # Common connection patterns
        patterns = [
            # Command -> Service
            (r"(.+)Command$", r"\1Service"),
            # Service -> Parser
            (r"(.+)Service$", r"\1Parser"),
            # Generator -> Models
            (r"(.+)Generator$", "DiagramModels"),
            # Parser -> Models
            (r"(.+)Parser$", "DiagramModels"),
            # Service -> Generator
            (r"(.+)Service$", r"\1Generator"),
            # Service -> Validator
            (r"(.+)Service$", r"\1Validator"),
        ]

        for comp in components:
            for src_pattern, tgt_pattern in patterns:
                match = re.match(src_pattern, comp.name)
                if match:
                    # Try to find matching target
                    if r"\1" in tgt_pattern:
                        target = re.sub(src_pattern, tgt_pattern, comp.name)
                    else:
                        target = tgt_pattern

                    if target in comp_names and target != comp.name:
                        connections.append((comp.name, target))

        # Deduplicate
        return list(set(connections))

    def generate_from_sections(
        self,
        tech_context: Optional[str] = None,
        project_structure: Optional[str] = None,
    ) -> str:
        """Generate architecture diagram from specific sections.

        Args:
            tech_context: Technical Context section content
            project_structure: Project Structure section content

        Returns:
            Mermaid diagram syntax
        """
        combined = ""
        if tech_context:
            combined += tech_context + "\n"
        if project_structure:
            combined += project_structure

        return self.generate(combined)
