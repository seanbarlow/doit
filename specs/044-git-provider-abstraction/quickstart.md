# Quickstart: Git Provider Abstraction Implementation

**Feature**: 044-git-provider-abstraction
**Date**: 2026-01-22

This guide provides step-by-step instructions for implementing the git provider abstraction layer.

## Prerequisites

- Python 3.11+
- Existing `github_service.py` implementation
- Understanding of the Strategy pattern

## Implementation Order

Follow this order for a clean implementation:

1. **Provider Models** - Create shared data models
2. **Provider Interface** - Define the abstract base class
3. **Provider Factory** - Create the factory for instantiation
4. **Provider Config** - Handle configuration management
5. **GitHub Provider** - Extract from existing service
6. **Azure DevOps Provider** - New implementation
7. **GitLab Provider** - Stub implementation
8. **CLI Commands** - Add provider management commands
9. **Integration** - Update existing commands

## Step 1: Create Provider Models

Create `src/doit_cli/models/provider_models.py`:

```python
"""Provider-agnostic data models for git operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class IssueType(Enum):
    BUG = "bug"
    TASK = "task"
    USER_STORY = "user_story"
    FEATURE = "feature"
    EPIC = "epic"


class IssueState(Enum):
    OPEN = "open"
    CLOSED = "closed"


class PRState(Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


class MilestoneState(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Label:
    name: str
    color: str | None = None
    description: str | None = None


@dataclass
class Issue:
    id: str
    provider_id: str
    title: str
    state: IssueState
    url: str
    created_at: datetime
    updated_at: datetime
    body: str | None = None
    type: IssueType = IssueType.TASK
    labels: list[Label] = field(default_factory=list)
    milestone_id: str | None = None


@dataclass
class PullRequest:
    id: str
    provider_id: str
    title: str
    source_branch: str
    target_branch: str
    state: PRState
    url: str
    created_at: datetime
    body: str | None = None
    labels: list[Label] = field(default_factory=list)
    closes_issues: list[str] = field(default_factory=list)
    merged_at: datetime | None = None


@dataclass
class Milestone:
    id: str
    provider_id: str
    title: str
    state: MilestoneState
    description: str | None = None
    due_date: datetime | None = None
    issue_count: int = 0
    closed_issue_count: int = 0
```

## Step 2: Create Provider Base Class

Create `src/doit_cli/services/providers/base.py`:

```python
"""Abstract base class for git providers."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from doit_cli.models.provider_models import (
        Issue,
        IssueFilters,
        IssueCreateRequest,
        IssueUpdateRequest,
        Milestone,
        MilestoneCreateRequest,
        MilestoneState,
        PullRequest,
        PRCreateRequest,
        PRFilters,
    )


class ProviderType(Enum):
    GITHUB = "github"
    AZURE_DEVOPS = "azure_devops"
    GITLAB = "gitlab"


class GitProvider(ABC):
    """Abstract interface for git hosting providers."""

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    # Issue operations
    @abstractmethod
    def create_issue(self, request: "IssueCreateRequest") -> "Issue":
        pass

    @abstractmethod
    def get_issue(self, issue_id: str) -> "Issue":
        pass

    @abstractmethod
    def list_issues(self, filters: "IssueFilters | None" = None) -> list["Issue"]:
        pass

    @abstractmethod
    def update_issue(self, issue_id: str, updates: "IssueUpdateRequest") -> "Issue":
        pass

    # PR operations
    @abstractmethod
    def create_pull_request(self, request: "PRCreateRequest") -> "PullRequest":
        pass

    @abstractmethod
    def get_pull_request(self, pr_id: str) -> "PullRequest":
        pass

    @abstractmethod
    def list_pull_requests(self, filters: "PRFilters | None" = None) -> list["PullRequest"]:
        pass

    # Milestone operations
    @abstractmethod
    def create_milestone(self, request: "MilestoneCreateRequest") -> "Milestone":
        pass

    @abstractmethod
    def get_milestone(self, milestone_id: str) -> "Milestone":
        pass

    @abstractmethod
    def list_milestones(self, state: "MilestoneState | None" = None) -> list["Milestone"]:
        pass
```

## Step 3: Create Provider Factory

Create `src/doit_cli/services/provider_factory.py`:

```python
"""Factory for creating git provider instances."""

import subprocess
from pathlib import Path

from doit_cli.services.providers.base import GitProvider, ProviderType
from doit_cli.services.provider_config import ProviderConfig


class ProviderFactory:
    """Factory for creating the appropriate git provider."""

    @classmethod
    def create(cls, config: ProviderConfig | None = None) -> GitProvider:
        """Create a provider instance based on configuration."""
        if config is None:
            config = ProviderConfig.load()

        provider_type = config.provider or cls._detect_provider()

        if provider_type == ProviderType.GITHUB:
            from doit_cli.services.providers.github import GitHubProvider
            return GitHubProvider()
        elif provider_type == ProviderType.AZURE_DEVOPS:
            from doit_cli.services.providers.azure_devops import AzureDevOpsProvider
            return AzureDevOpsProvider(config.azure_devops)
        elif provider_type == ProviderType.GITLAB:
            from doit_cli.services.providers.gitlab import GitLabProvider
            return GitLabProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_type}")

    @classmethod
    def _detect_provider(cls) -> ProviderType:
        """Auto-detect provider from git remote URL."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()

            if "github.com" in remote_url or "ghe." in remote_url:
                return ProviderType.GITHUB
            elif "dev.azure.com" in remote_url or "visualstudio.com" in remote_url:
                return ProviderType.AZURE_DEVOPS
            elif "gitlab" in remote_url:
                return ProviderType.GITLAB

        except subprocess.CalledProcessError:
            pass

        # Default to GitHub
        return ProviderType.GITHUB
```

## Step 4: Create Provider Config

Create `src/doit_cli/services/provider_config.py`:

```python
"""Provider configuration management."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from doit_cli.services.providers.base import ProviderType


@dataclass
class AzureDevOpsConfig:
    organization: str = ""
    project: str = ""
    auth_method: str = "pat"
    api_version: str = "7.0"


@dataclass
class ProviderConfig:
    provider: ProviderType | None = None
    auto_detected: bool = False
    detection_source: str | None = None
    azure_devops: AzureDevOpsConfig = field(default_factory=AzureDevOpsConfig)

    CONFIG_PATH = Path(".doit/config/provider.yaml")

    @classmethod
    def load(cls) -> "ProviderConfig":
        """Load configuration from file."""
        if not cls.CONFIG_PATH.exists():
            return cls()

        with open(cls.CONFIG_PATH) as f:
            data = yaml.safe_load(f) or {}

        config = cls()
        if "provider" in data:
            config.provider = ProviderType(data["provider"])
        config.auto_detected = data.get("auto_detected", False)
        config.detection_source = data.get("detection_source")

        if "azure_devops" in data:
            ado = data["azure_devops"]
            config.azure_devops = AzureDevOpsConfig(
                organization=ado.get("organization", ""),
                project=ado.get("project", ""),
                auth_method=ado.get("auth_method", "pat"),
            )

        return config

    def save(self) -> None:
        """Save configuration to file."""
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {}
        if self.provider:
            data["provider"] = self.provider.value
        data["auto_detected"] = self.auto_detected
        if self.detection_source:
            data["detection_source"] = self.detection_source

        if self.provider == ProviderType.AZURE_DEVOPS:
            data["azure_devops"] = {
                "organization": self.azure_devops.organization,
                "project": self.azure_devops.project,
                "auth_method": self.azure_devops.auth_method,
            }

        with open(self.CONFIG_PATH, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
```

## Step 5: Implement GitHub Provider

Create `src/doit_cli/services/providers/github.py`:

```python
"""GitHub provider implementation using gh CLI."""

import json
import subprocess
from datetime import datetime

from doit_cli.models.provider_models import (
    Issue,
    IssueCreateRequest,
    IssueFilters,
    IssueState,
    IssueType,
    IssueUpdateRequest,
    Label,
    Milestone,
    MilestoneCreateRequest,
    MilestoneState,
    PullRequest,
    PRCreateRequest,
    PRFilters,
    PRState,
)
from doit_cli.services.providers.base import GitProvider, ProviderType


class GitHubProvider(GitProvider):
    """GitHub implementation using the gh CLI."""

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GITHUB

    @property
    def name(self) -> str:
        return "GitHub"

    @property
    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def create_issue(self, request: IssueCreateRequest) -> Issue:
        cmd = ["gh", "issue", "create", "--title", request.title]
        if request.body:
            cmd.extend(["--body", request.body])
        for label in request.labels:
            cmd.extend(["--label", label])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse created issue URL and fetch details
        url = result.stdout.strip()
        issue_number = url.split("/")[-1]
        return self.get_issue(issue_number)

    def get_issue(self, issue_id: str) -> Issue:
        result = subprocess.run(
            ["gh", "issue", "view", issue_id, "--json",
             "number,title,body,state,url,createdAt,updatedAt,labels"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        return self._parse_issue(data)

    def list_issues(self, filters: IssueFilters | None = None) -> list[Issue]:
        cmd = ["gh", "issue", "list", "--json",
               "number,title,body,state,url,createdAt,updatedAt,labels"]

        if filters:
            if filters.state:
                cmd.extend(["--state", filters.state.value])
            if filters.labels:
                for label in filters.labels:
                    cmd.extend(["--label", label])
            if filters.limit:
                cmd.extend(["--limit", str(filters.limit)])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issues_data = json.loads(result.stdout)
        return [self._parse_issue(d) for d in issues_data]

    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        cmd = ["gh", "issue", "edit", issue_id]
        if updates.title:
            cmd.extend(["--title", updates.title])
        if updates.body:
            cmd.extend(["--body", updates.body])
        if updates.labels is not None:
            for label in updates.labels:
                cmd.extend(["--add-label", label])

        subprocess.run(cmd, capture_output=True, text=True, check=True)

        if updates.state == IssueState.CLOSED:
            subprocess.run(
                ["gh", "issue", "close", issue_id],
                capture_output=True,
                text=True,
                check=True,
            )

        return self.get_issue(issue_id)

    # PR and Milestone methods follow similar patterns...
    # (Implementation continues for all interface methods)

    def _parse_issue(self, data: dict) -> Issue:
        """Parse gh CLI JSON output into Issue model."""
        return Issue(
            id=f"github:{data['number']}",
            provider_id=str(data["number"]),
            title=data["title"],
            body=data.get("body"),
            state=IssueState.OPEN if data["state"] == "OPEN" else IssueState.CLOSED,
            url=data["url"],
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00")),
            labels=[Label(name=l["name"]) for l in data.get("labels", [])],
        )
```

## Step 6: Update Existing Service

Refactor `src/doit_cli/services/github_service.py` to delegate:

```python
"""GitHub service - backward compatibility layer."""

from doit_cli.services.provider_factory import ProviderFactory
from doit_cli.services.providers.base import ProviderType


class GitHubService:
    """
    Backward-compatible facade for GitHub operations.

    Delegates to GitHubProvider while maintaining existing interface.
    """

    def __init__(self):
        self._provider = ProviderFactory.create()
        if self._provider.provider_type != ProviderType.GITHUB:
            raise ValueError("GitHubService requires GitHub provider")

    def create_issue(self, title: str, body: str, labels: list[str] | None = None):
        """Create a GitHub issue (legacy interface)."""
        from doit_cli.models.provider_models import IssueCreateRequest

        request = IssueCreateRequest(
            title=title,
            body=body,
            labels=labels or [],
        )
        issue = self._provider.create_issue(request)
        return {"number": issue.provider_id, "url": issue.url}

    # ... other methods maintain backward compatibility
```

## Step 7: Add CLI Commands

Create `src/doit_cli/cli/provider.py`:

```python
"""CLI commands for provider management."""

import typer
from rich.console import Console
from rich.table import Table

from doit_cli.services.provider_factory import ProviderFactory
from doit_cli.services.provider_config import ProviderConfig
from doit_cli.services.providers.base import ProviderType

app = typer.Typer(help="Git provider management commands")
console = Console()


@app.command()
def configure(
    provider: str = typer.Option(None, help="Provider: github, azure_devops, gitlab"),
):
    """Configure the git provider for this project."""
    config = ProviderConfig()

    if provider:
        config.provider = ProviderType(provider)
        config.auto_detected = False
    else:
        # Auto-detect
        config.provider = ProviderFactory._detect_provider()
        config.auto_detected = True
        config.detection_source = "git_remote"

    config.save()
    console.print(f"[green]Provider configured: {config.provider.value}[/green]")


@app.command()
def status():
    """Show current provider status."""
    config = ProviderConfig.load()
    provider = ProviderFactory.create(config)

    table = Table(title="Provider Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Provider", provider.name)
    table.add_row("Type", provider.provider_type.value)
    table.add_row("Available", "✓" if provider.is_available else "✗")
    table.add_row("Auto-detected", "Yes" if config.auto_detected else "No")

    console.print(table)
```

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_provider_factory.py
import pytest
from unittest.mock import patch

from doit_cli.services.provider_factory import ProviderFactory
from doit_cli.services.providers.base import ProviderType


class TestProviderDetection:
    @patch("subprocess.run")
    def test_detect_github(self, mock_run):
        mock_run.return_value.stdout = "https://github.com/user/repo.git"
        mock_run.return_value.returncode = 0

        detected = ProviderFactory._detect_provider()

        assert detected == ProviderType.GITHUB

    @patch("subprocess.run")
    def test_detect_azure_devops(self, mock_run):
        mock_run.return_value.stdout = "https://dev.azure.com/org/project/_git/repo"
        mock_run.return_value.returncode = 0

        detected = ProviderFactory._detect_provider()

        assert detected == ProviderType.AZURE_DEVOPS
```

### Integration Tests

```python
# tests/integration/test_provider_integration.py
import pytest
from doit_cli.services.provider_factory import ProviderFactory


@pytest.mark.integration
class TestProviderIntegration:
    def test_github_provider_availability(self):
        """Test that GitHub provider can check availability."""
        provider = ProviderFactory.create()
        # Should not raise
        _ = provider.is_available

    def test_create_and_close_issue(self):
        """End-to-end test for issue lifecycle."""
        provider = ProviderFactory.create()
        if not provider.is_available:
            pytest.skip("Provider not available")

        # Create
        from doit_cli.models.provider_models import IssueCreateRequest
        issue = provider.create_issue(
            IssueCreateRequest(title="Test issue", body="Test body")
        )
        assert issue.id is not None

        # Close
        from doit_cli.models.provider_models import IssueState, IssueUpdateRequest
        updated = provider.update_issue(
            issue.provider_id,
            IssueUpdateRequest(state=IssueState.CLOSED)
        )
        assert updated.state == IssueState.CLOSED
```

## Next Steps

After implementation:

1. Run `/doit.taskit` to generate implementation tasks
2. Implement each task following TDD (write tests first)
3. Run `/doit.reviewit` for code review
4. Run `/doit.checkin` to complete the feature
