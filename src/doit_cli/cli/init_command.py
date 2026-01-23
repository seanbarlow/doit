"""Init command for initializing doit project structure."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from ..models.agent import Agent
from ..models.project import Project
from ..models.results import InitResult
from ..models.workflow_models import Workflow, WorkflowStep
from ..services.scaffolder import Scaffolder
from ..services.state_manager import StateManager
from ..services.workflow_engine import WorkflowEngine


console = Console()

# Type aliases for CLI options
AgentOption = Annotated[
    Optional[str],
    typer.Option(
        "--agent", "-a",
        help="Target agent(s): claude, copilot, or claude,copilot for both"
    )
]

TemplatesOption = Annotated[
    Optional[Path],
    typer.Option(
        "--templates", "-t",
        help="Custom template directory path"
    )
]

UpdateFlag = Annotated[
    bool,
    typer.Option(
        "--update", "-u",
        help="Update existing project, preserving custom files"
    )
]

ForceFlag = Annotated[
    bool,
    typer.Option(
        "--force", "-f",
        help="Overwrite existing files without backup"
    )
]

YesFlag = Annotated[
    bool,
    typer.Option(
        "--yes", "-y",
        help="Skip confirmation prompts"
    )
]


# =============================================================================
# InitWorkflow Factory (Feature 031)
# =============================================================================


def create_init_workflow(path: Path) -> Workflow:
    """Create the init workflow definition.

    Args:
        path: Target project directory path

    Returns:
        Workflow instance configured for init command

    Example:
        workflow = create_init_workflow(Path("."))
        responses = engine.run(workflow)
    """
    return Workflow(
        id="init-workflow",
        command_name="init",
        description="Initialize a new doit project",
        interactive=True,
        steps=[
            WorkflowStep(
                id="select-agent",
                name="Select AI Agent",
                prompt_text="Which AI agent(s) do you want to initialize for?",
                required=True,
                order=0,
                validation_type="ChoiceValidator",
                default_value="claude",
                options={
                    "claude": "Claude Code",
                    "copilot": "GitHub Copilot",
                    "both": "Both agents",
                },
            ),
            WorkflowStep(
                id="confirm-path",
                name="Confirm Project Path",
                prompt_text=f"Initialize doit in '{path}'?",
                required=True,
                order=1,
                validation_type=None,
                default_value="yes",
                options={"yes": "Confirm", "no": "Cancel"},
            ),
            WorkflowStep(
                id="custom-templates",
                name="Custom Templates",
                prompt_text="Custom template directory (leave empty for default)",
                required=False,
                order=2,
                validation_type="PathExistsValidator",
                default_value="",
            ),
        ],
    )


def map_workflow_responses(responses: dict) -> tuple[list[Agent], Optional[Path]]:
    """Map workflow responses to init parameters.

    Args:
        responses: Dict from WorkflowEngine.run()

    Returns:
        Tuple of (agents list, template_source path or None)

    Raises:
        typer.Exit: If confirm-path is "no"
    """
    # Check confirmation
    if responses.get("confirm-path") == "no":
        console.print("[yellow]Initialization cancelled.[/yellow]")
        raise typer.Exit(0)

    # Parse agent selection
    agent_str = responses.get("select-agent", "claude")
    if agent_str == "both":
        agents = [Agent.CLAUDE, Agent.COPILOT]
    elif agent_str == "copilot":
        agents = [Agent.COPILOT]
    else:
        agents = [Agent.CLAUDE]

    # Parse template path
    template_str = responses.get("custom-templates", "")
    template_source = Path(template_str) if template_str else None

    return agents, template_source


def display_init_result(result: InitResult, agents: list[Agent]) -> None:
    """Display initialization result with rich formatting.

    Args:
        result: The initialization result to display
        agents: List of agents that were initialized
    """
    if not result.success:
        console.print(
            Panel(
                f"[red]Error:[/red] {result.error_message}",
                title="[red]Initialization Failed[/red]",
                border_style="red",
            )
        )
        return

    # Create a tree view of created structure
    tree = Tree("[bold cyan]Doit Project Structure[/bold cyan]")

    if result.created_directories:
        dirs_branch = tree.add("[green]Created Directories[/green]")
        for dir_path in sorted(result.created_directories):
            rel_path = dir_path.relative_to(result.project.path)
            dirs_branch.add(f"[dim]{rel_path}/[/dim]")

    if result.created_files:
        files_branch = tree.add("[green]Created Files[/green]")
        for file_path in sorted(result.created_files):
            rel_path = file_path.relative_to(result.project.path)
            files_branch.add(f"[dim]{rel_path}[/dim]")

    if result.updated_files:
        updated_branch = tree.add("[yellow]Updated Files[/yellow]")
        for file_path in sorted(result.updated_files):
            rel_path = file_path.relative_to(result.project.path)
            updated_branch.add(f"[dim]{rel_path}[/dim]")

    if result.skipped_files:
        skipped_branch = tree.add("[dim]Skipped Files (already exist)[/dim]")
        for file_path in sorted(result.skipped_files):
            rel_path = file_path.relative_to(result.project.path)
            skipped_branch.add(f"[dim]{rel_path}[/dim]")

    console.print()
    console.print(Panel(tree, title="[bold green]Initialization Complete[/bold green]", border_style="green"))

    # Display summary
    console.print()
    console.print(f"[bold]Summary:[/bold] {result.summary}")

    # Display next steps
    display_next_steps(agents)


def display_next_steps(agents: list[Agent]) -> None:
    """Display next steps guidance after initialization.

    Args:
        agents: List of agents that were initialized
    """
    steps = [
        "1. Run [cyan]/doit.constitution[/cyan] to establish project principles",
        "2. Run [cyan]/doit.specit[/cyan] to create your first feature specification",
        "3. Run [cyan]/doit.planit[/cyan] to create an implementation plan",
    ]

    agent_names = ", ".join(a.display_name for a in agents)

    console.print()
    console.print(
        Panel(
            "\n".join(
                [
                    f"[bold]Initialized for:[/bold] {agent_names}",
                    "",
                    "[bold]Next Steps:[/bold]",
                    *steps,
                ]
            ),
            title="[cyan]Getting Started[/cyan]",
            border_style="cyan",
        )
    )


def prompt_agent_selection() -> list[Agent]:
    """Prompt user to select target agent(s).

    Returns:
        List of selected agents
    """
    console.print()
    console.print("[bold]Select target AI agent(s):[/bold]")
    console.print()

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Agent", style="white")
    table.add_column("Command Directory", style="dim")

    table.add_row("1", "Claude Code", ".claude/commands/")
    table.add_row("2", "GitHub Copilot", ".github/prompts/")
    table.add_row("3", "Both", ".claude/commands/ + .github/prompts/")

    console.print(table)
    console.print()

    choice = typer.prompt("Enter your choice (1-3)", default="1")

    if choice == "1":
        return [Agent.CLAUDE]
    elif choice == "2":
        return [Agent.COPILOT]
    elif choice == "3":
        return [Agent.CLAUDE, Agent.COPILOT]
    else:
        console.print("[yellow]Invalid choice, defaulting to Claude[/yellow]")
        return [Agent.CLAUDE]


def parse_agent_string(agent_str: str) -> list[Agent]:
    """Parse agent string into list of Agent enums.

    Args:
        agent_str: Comma-separated agent names (e.g., "claude,copilot")

    Returns:
        List of Agent enums

    Raises:
        typer.BadParameter: If invalid agent name provided
    """
    agents = []
    for name in agent_str.lower().split(","):
        name = name.strip()
        if name == "claude":
            agents.append(Agent.CLAUDE)
        elif name == "copilot":
            agents.append(Agent.COPILOT)
        else:
            raise typer.BadParameter(
                f"Unknown agent: {name}. Use 'claude', 'copilot', or 'claude,copilot'"
            )

    return agents


def validate_custom_templates(template_source: Path, yes: bool = False) -> bool:
    """Validate custom template source and display warnings.

    Args:
        template_source: Path to custom template directory
        yes: Skip confirmation prompts

    Returns:
        True if should continue, False to abort
    """
    from ..services.template_manager import TemplateManager

    template_manager = TemplateManager(template_source)
    validation = template_manager.validate_custom_source()

    if not validation.get("valid", False):
        error_msg = validation.get("error", "Invalid custom template source")
        console.print(f"[red]Error:[/red] {error_msg}")
        return False

    warnings = validation.get("warnings", [])
    if warnings:
        console.print()
        console.print(
            Panel(
                "\n".join(f"• {w}" for w in warnings),
                title="[yellow]Template Warnings[/yellow]",
                border_style="yellow",
            )
        )

        if not yes:
            if not typer.confirm("Continue with missing templates?", default=True):
                return False

    return True


def run_init(
    path: Path,
    agents: Optional[list[Agent]] = None,
    update: bool = False,
    force: bool = False,
    yes: bool = False,
    template_source: Optional[Path] = None,
) -> InitResult:
    """Run the initialization process.

    Args:
        path: Project directory path
        agents: Target agents (None to auto-detect or prompt)
        update: Update existing project
        force: Force overwrite without backup
        yes: Skip confirmation prompts
        template_source: Custom template source path

    Returns:
        InitResult with operation details
    """
    # Defer imports to avoid circular dependencies
    from ..services.template_manager import TemplateManager
    from ..services.agent_detector import AgentDetector

    # Create project model
    project = Project(path=path.resolve())

    # Validate custom template source if provided
    if template_source:
        if not validate_custom_templates(template_source, yes):
            return InitResult(
                success=False,
                project=project,
                error_message="Custom template validation failed",
            )

    # Check if safe directory
    if not project.is_safe_directory() and not force:
        if not yes:
            console.print(
                Panel(
                    f"[yellow]Warning:[/yellow] You are about to initialize doit in [bold]{path}[/bold]\n\n"
                    "This is typically not recommended. Consider initializing in a project directory instead.",
                    title="[yellow]Unsafe Directory[/yellow]",
                    border_style="yellow",
                )
            )
            if not typer.confirm("Continue anyway?", default=False):
                return InitResult(
                    success=False,
                    project=project,
                    error_message="Operation cancelled by user",
                )

    # Determine target agents
    if agents is None:
        detector = AgentDetector(project)
        detected = detector.detect_agents()

        if detected:
            agents = detected
            agent_names = ", ".join(a.display_name for a in agents)
            console.print(f"[cyan]Auto-detected agent(s):[/cyan] {agent_names}")
        elif yes:
            # Default to Claude if --yes and no detection
            agents = [Agent.CLAUDE]
            console.print("[cyan]Defaulting to Claude Code[/cyan]")
        else:
            agents = prompt_agent_selection()

    # Create scaffolder and initialize structure
    scaffolder = Scaffolder(project)
    result = scaffolder.create_doit_structure()

    if not result.success:
        return result

    # Create agent directories and copy templates
    template_manager = TemplateManager(template_source)

    # Copy workflow templates to .doit/templates/
    workflow_result = template_manager.copy_workflow_templates(
        target_dir=project.doit_folder / "templates",
        overwrite=update or force,
    )
    result.created_files.extend(workflow_result.get("created", []))
    result.updated_files.extend(workflow_result.get("updated", []))
    result.skipped_files.extend(workflow_result.get("skipped", []))

    # Copy GitHub issue templates to .github/ISSUE_TEMPLATE/
    github_templates_result = template_manager.copy_github_issue_templates(
        target_dir=project.path / ".github" / "ISSUE_TEMPLATE",
        overwrite=update or force,
    )
    result.created_files.extend(github_templates_result.get("created", []))
    result.updated_files.extend(github_templates_result.get("updated", []))
    result.skipped_files.extend(github_templates_result.get("skipped", []))

    # Copy workflow scripts to .doit/scripts/bash/
    scripts_result = template_manager.copy_scripts(
        target_dir=project.doit_folder / "scripts" / "bash",
        overwrite=update or force,
    )
    result.created_files.extend(scripts_result.get("created", []))
    result.updated_files.extend(scripts_result.get("updated", []))
    result.skipped_files.extend(scripts_result.get("skipped", []))

    # Copy memory templates to .doit/memory/
    # Note: Memory files (constitution, roadmap) should only be overwritten with --force,
    # not --update, since they contain user-customized project content
    memory_result = template_manager.copy_memory_templates(
        target_dir=project.doit_folder / "memory",
        overwrite=force,
    )
    result.created_files.extend(memory_result.get("created", []))
    result.updated_files.extend(memory_result.get("updated", []))
    result.skipped_files.extend(memory_result.get("skipped", []))

    # Copy config templates to .doit/config/
    config_result = template_manager.copy_config_templates(
        target_dir=project.doit_folder / "config",
        overwrite=update or force,
    )
    result.created_files.extend(config_result.get("created", []))
    result.updated_files.extend(config_result.get("updated", []))
    result.skipped_files.extend(config_result.get("skipped", []))

    # Copy hook templates to .doit/hooks/
    hooks_result = template_manager.copy_hook_templates(
        target_dir=project.doit_folder / "hooks",
        overwrite=update or force,
    )
    result.created_files.extend(hooks_result.get("created", []))
    result.updated_files.extend(hooks_result.get("updated", []))
    result.skipped_files.extend(hooks_result.get("skipped", []))

    # Copy workflow document templates (agent-file-template, etc.) to .doit/templates/
    doc_templates_result = template_manager.copy_workflow_document_templates(
        target_dir=project.doit_folder / "templates",
        overwrite=update or force,
    )
    result.created_files.extend(doc_templates_result.get("created", []))
    result.updated_files.extend(doc_templates_result.get("updated", []))
    result.skipped_files.extend(doc_templates_result.get("skipped", []))

    for agent in agents:
        scaffolder.create_agent_directory(agent)

        # Copy templates for this agent
        copy_result = template_manager.copy_templates_for_agent(
            agent=agent,
            target_dir=project.command_directory(agent),
            overwrite=update or force,
        )

        result.created_files.extend(copy_result.get("created", []))
        result.updated_files.extend(copy_result.get("updated", []))
        result.skipped_files.extend(copy_result.get("skipped", []))

        # For Copilot agent, also create/update copilot-instructions.md
        if agent == Agent.COPILOT:
            copilot_instructions_path = project.path / ".github" / "copilot-instructions.md"
            copilot_instructions_path.parent.mkdir(parents=True, exist_ok=True)

            if template_manager.create_copilot_instructions(
                target_path=copilot_instructions_path,
                update_only=False,
            ):
                if copilot_instructions_path in result.created_files:
                    pass  # Already tracked
                elif copilot_instructions_path.exists():
                    result.updated_files.append(copilot_instructions_path)
                else:
                    result.created_files.append(copilot_instructions_path)

    # Update project state
    project.initialized = True
    project.agents = agents

    return result


def init_command(
    path: Annotated[
        Path,
        typer.Argument(
            default=...,
            help="Project directory path (use '.' for current directory)"
        )
    ] = Path("."),
    agent: AgentOption = None,
    templates: TemplatesOption = None,
    update: UpdateFlag = False,
    force: ForceFlag = False,
    yes: YesFlag = False,
) -> None:
    """Initialize a new doit project with bundled templates.

    This command creates the .doit/ folder structure and copies command
    templates for the specified AI agent(s).

    Examples:
        doit init .                    # Initialize in current directory
        doit init . --agent claude     # Claude only
        doit init . --agent copilot    # Copilot only
        doit init . -a claude,copilot  # Both agents
        doit init . --update           # Update existing templates
        doit init . --yes              # Non-interactive mode
    """
    # Parse agent string if provided via CLI
    agents = None
    if agent:
        try:
            agents = parse_agent_string(agent)
        except typer.BadParameter as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Non-interactive mode: bypass workflow entirely (FR-003, FR-008)
    if yes:
        result = run_init(
            path=path,
            agents=agents,
            update=update,
            force=force,
            yes=True,
            template_source=templates,
        )
        display_init_result(result, agents or result.project.agents or [Agent.CLAUDE])
        if not result.success:
            raise typer.Exit(1)
        return

    # Interactive mode: use workflow engine (FR-001, FR-002, FR-005)
    workflow = create_init_workflow(path)

    # Fix MT-005: Use target path for state directory, not cwd
    state_dir = path.resolve() / ".doit" / "state"
    engine = WorkflowEngine(
        console=console,
        state_manager=StateManager(state_dir=state_dir),
    )

    # Fix MT-007: Pre-populate responses for CLI-provided values
    initial_responses: dict[str, str] = {}
    if agents:
        # Map agents to workflow response value
        if len(agents) == 2:
            initial_responses["select-agent"] = "both"
        elif Agent.COPILOT in agents:
            initial_responses["select-agent"] = "copilot"
        else:
            initial_responses["select-agent"] = "claude"
    if templates:
        initial_responses["custom-templates"] = str(templates)

    try:
        responses = engine.run(workflow, initial_responses=initial_responses)
    except KeyboardInterrupt:
        # State is saved by workflow engine (FR-007)
        raise typer.Exit(130)

    # Map workflow responses to init parameters (FR-006)
    workflow_agents, template_source = map_workflow_responses(responses)

    # Use CLI-provided agents if specified, else use workflow selection
    final_agents = agents if agents else workflow_agents

    # Use CLI-provided templates if specified, else use workflow selection
    final_templates = templates if templates else template_source

    # Execute init with collected parameters
    result = run_init(
        path=path,
        agents=final_agents,
        update=update,
        force=force,
        yes=False,
        template_source=final_templates,
    )

    # Display results
    display_init_result(result, final_agents or result.project.agents or [Agent.CLAUDE])

    if not result.success:
        raise typer.Exit(1)
