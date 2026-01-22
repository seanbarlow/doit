"""Azure DevOps provider implementation using REST API.

This module implements the GitProvider interface for Azure DevOps
using direct REST API calls via httpx.
"""

import os
from datetime import datetime
from typing import Any, Optional

import httpx

from ...models.provider_models import (
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
from ..provider_config import AzureDevOpsConfig
from .base import GitProvider, ProviderType
from .exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)


class AzureDevOpsLabelMapper:
    """Maps labels between unified format and Azure DevOps work item types/tags."""

    # Issue type to Azure DevOps work item type
    TYPE_TO_WORK_ITEM_TYPE = {
        IssueType.BUG: "Bug",
        IssueType.TASK: "Task",
        IssueType.USER_STORY: "User Story",
        IssueType.FEATURE: "Feature",
        IssueType.EPIC: "Epic",
    }

    # Reverse mapping
    WORK_ITEM_TYPE_TO_TYPE = {
        "Bug": IssueType.BUG,
        "Task": IssueType.TASK,
        "User Story": IssueType.USER_STORY,
        "Feature": IssueType.FEATURE,
        "Epic": IssueType.EPIC,
    }

    @classmethod
    def type_to_work_item_type(cls, issue_type: IssueType) -> str:
        """Convert issue type to Azure DevOps work item type."""
        return cls.TYPE_TO_WORK_ITEM_TYPE.get(issue_type, "Task")

    @classmethod
    def work_item_type_to_type(cls, work_item_type: str) -> IssueType:
        """Convert Azure DevOps work item type to issue type."""
        return cls.WORK_ITEM_TYPE_TO_TYPE.get(work_item_type, IssueType.TASK)


class AzureDevOpsProvider(GitProvider):
    """Azure DevOps implementation using REST API.

    This provider uses the Azure DevOps REST API directly,
    authenticated via Personal Access Token (PAT).
    """

    def __init__(self, config: Optional[AzureDevOpsConfig] = None, timeout: int = 30):
        """Initialize the Azure DevOps provider.

        Args:
            config: Azure DevOps configuration with org/project.
            timeout: Timeout in seconds for API requests.
        """
        self.config = config or AzureDevOpsConfig()
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.AZURE_DEVOPS

    @property
    def name(self) -> str:
        return "Azure DevOps"

    @property
    def is_available(self) -> bool:
        """Check if Azure DevOps is configured and accessible."""
        if not self.config.organization or not self.config.project:
            return False
        if not self._get_pat():
            return False
        try:
            # Try to access the project
            client = self._get_client()
            response = client.get(
                f"https://dev.azure.com/{self.config.organization}/_apis/projects/{self.config.project}",
                params={"api-version": self.config.api_version},
            )
            return response.status_code == 200
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # Issue Operations (Work Items)
    # -------------------------------------------------------------------------

    def create_issue(self, request: IssueCreateRequest) -> Issue:
        """Create a new Azure DevOps work item."""
        self._ensure_authenticated()

        work_item_type = AzureDevOpsLabelMapper.type_to_work_item_type(request.type)

        # Build the JSON patch document
        operations = [
            {"op": "add", "path": "/fields/System.Title", "value": request.title},
        ]

        if request.body:
            operations.append(
                {"op": "add", "path": "/fields/System.Description", "value": request.body}
            )

        # Add tags from labels
        if request.labels:
            tags = "; ".join(request.labels)
            operations.append(
                {"op": "add", "path": "/fields/System.Tags", "value": tags}
            )

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/wit/workitems/${work_item_type}"
            )

            response = client.post(
                url,
                params={"api-version": self.config.api_version},
                json=operations,
                headers={"Content-Type": "application/json-patch+json"},
            )

            if response.status_code == 401:
                raise AuthenticationError(
                    "Azure DevOps authentication failed. Check your PAT.",
                    provider="Azure DevOps",
                )
            elif response.status_code == 400:
                raise ValidationError(f"Invalid work item: {response.text}")
            elif response.status_code != 200:
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return self._parse_work_item(data)

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def get_issue(self, issue_id: str) -> Issue:
        """Get an Azure DevOps work item by ID."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(issue_id)

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/wit/workitems/{provider_id}"
            )

            response = client.get(
                url,
                params={"api-version": self.config.api_version},
            )

            if response.status_code == 404:
                raise ResourceNotFoundError("Work Item", provider_id)
            elif response.status_code != 200:
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return self._parse_work_item(data)

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def list_issues(self, filters: Optional[IssueFilters] = None) -> list[Issue]:
        """List Azure DevOps work items matching filters."""
        self._ensure_authenticated()

        # Build WIQL query
        conditions = []

        if filters:
            if filters.state:
                state_str = "Active" if filters.state == IssueState.OPEN else "Closed"
                conditions.append(f"[System.State] = '{state_str}'")

            if filters.type:
                work_item_type = AzureDevOpsLabelMapper.type_to_work_item_type(filters.type)
                conditions.append(f"[System.WorkItemType] = '{work_item_type}'")

            if filters.labels:
                for label in filters.labels:
                    conditions.append(f"[System.Tags] CONTAINS '{label}'")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        wiql = f"SELECT [System.Id] FROM WorkItems WHERE {where_clause}"

        if filters and filters.limit:
            wiql += f" ORDER BY [System.Id] DESC"

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/wit/wiql"
            )

            response = client.post(
                url,
                params={"api-version": self.config.api_version},
                json={"query": wiql},
            )

            if response.status_code != 200:
                raise ProviderError(f"Azure DevOps query error: {response.text}")

            data = response.json()
            work_items = data.get("workItems", [])

            # Limit results
            if filters and filters.limit:
                work_items = work_items[:filters.limit]

            # Fetch full details for each work item
            issues = []
            for wi in work_items:
                try:
                    issue = self.get_issue(str(wi["id"]))
                    issues.append(issue)
                except ResourceNotFoundError:
                    continue

            return issues

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def update_issue(self, issue_id: str, updates: IssueUpdateRequest) -> Issue:
        """Update an Azure DevOps work item."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(issue_id)

        operations = []

        if updates.title:
            operations.append(
                {"op": "replace", "path": "/fields/System.Title", "value": updates.title}
            )

        if updates.body:
            operations.append(
                {"op": "replace", "path": "/fields/System.Description", "value": updates.body}
            )

        if updates.state:
            state_str = "Active" if updates.state == IssueState.OPEN else "Closed"
            operations.append(
                {"op": "replace", "path": "/fields/System.State", "value": state_str}
            )

        if updates.labels is not None:
            tags = "; ".join(updates.labels)
            operations.append(
                {"op": "replace", "path": "/fields/System.Tags", "value": tags}
            )

        if not operations:
            return self.get_issue(provider_id)

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/wit/workitems/{provider_id}"
            )

            response = client.patch(
                url,
                params={"api-version": self.config.api_version},
                json=operations,
                headers={"Content-Type": "application/json-patch+json"},
            )

            if response.status_code == 404:
                raise ResourceNotFoundError("Work Item", provider_id)
            elif response.status_code != 200:
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return self._parse_work_item(data)

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    # -------------------------------------------------------------------------
    # Pull Request Operations
    # -------------------------------------------------------------------------

    def create_pull_request(self, request: PRCreateRequest) -> PullRequest:
        """Create a new Azure DevOps pull request."""
        self._ensure_authenticated()

        repo_id = self._get_repository_id()

        body: dict[str, Any] = {
            "sourceRefName": f"refs/heads/{request.source_branch}",
            "targetRefName": f"refs/heads/{request.target_branch}",
            "title": request.title,
        }

        if request.body:
            body["description"] = request.body

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/git/repositories/{repo_id}/pullrequests"
            )

            response = client.post(
                url,
                params={"api-version": self.config.api_version},
                json=body,
            )

            if response.status_code == 409:
                raise ValidationError("Pull request already exists for this branch")
            elif response.status_code not in (200, 201):
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return self._parse_pull_request(data)

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get an Azure DevOps pull request by ID."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(pr_id)
        repo_id = self._get_repository_id()

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/git/repositories/{repo_id}/pullrequests/{provider_id}"
            )

            response = client.get(
                url,
                params={"api-version": self.config.api_version},
            )

            if response.status_code == 404:
                raise ResourceNotFoundError("Pull Request", provider_id)
            elif response.status_code != 200:
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return self._parse_pull_request(data)

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def list_pull_requests(
        self, filters: Optional[PRFilters] = None
    ) -> list[PullRequest]:
        """List Azure DevOps pull requests matching filters."""
        self._ensure_authenticated()
        repo_id = self._get_repository_id()

        params: dict[str, Any] = {"api-version": self.config.api_version}

        if filters:
            if filters.state:
                state_map = {
                    PRState.OPEN: "active",
                    PRState.MERGED: "completed",
                    PRState.CLOSED: "abandoned",
                }
                params["searchCriteria.status"] = state_map.get(filters.state, "active")

            if filters.source_branch:
                params["searchCriteria.sourceRefName"] = f"refs/heads/{filters.source_branch}"

            if filters.target_branch:
                params["searchCriteria.targetRefName"] = f"refs/heads/{filters.target_branch}"

            if filters.limit:
                params["$top"] = filters.limit

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/git/repositories/{repo_id}/pullrequests"
            )

            response = client.get(url, params=params)

            if response.status_code != 200:
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return [self._parse_pull_request(pr) for pr in data.get("value", [])]

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    # -------------------------------------------------------------------------
    # Milestone Operations (Iterations)
    # -------------------------------------------------------------------------

    def create_milestone(self, request: MilestoneCreateRequest) -> Milestone:
        """Create a new Azure DevOps iteration."""
        self._ensure_authenticated()

        body: dict[str, Any] = {
            "name": request.title,
        }

        if request.due_date:
            body["attributes"] = {
                "finishDate": request.due_date.isoformat(),
            }

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/wit/classificationnodes/Iterations"
            )

            response = client.post(
                url,
                params={"api-version": self.config.api_version},
                json=body,
            )

            if response.status_code == 409:
                raise ValidationError(f"Iteration '{request.title}' already exists")
            elif response.status_code not in (200, 201):
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return self._parse_iteration(data)

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def get_milestone(self, milestone_id: str) -> Milestone:
        """Get an Azure DevOps iteration by ID."""
        self._ensure_authenticated()
        provider_id = self._extract_provider_id(milestone_id)

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/wit/classificationnodes/Iterations/{provider_id}"
            )

            response = client.get(
                url,
                params={"api-version": self.config.api_version, "$depth": "1"},
            )

            if response.status_code == 404:
                raise ResourceNotFoundError("Iteration", provider_id)
            elif response.status_code != 200:
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            return self._parse_iteration(data)

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def list_milestones(
        self, state: Optional[MilestoneState] = None
    ) -> list[Milestone]:
        """List Azure DevOps iterations."""
        self._ensure_authenticated()

        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/wit/classificationnodes/Iterations"
            )

            response = client.get(
                url,
                params={"api-version": self.config.api_version, "$depth": "2"},
            )

            if response.status_code != 200:
                raise ProviderError(f"Azure DevOps error: {response.text}")

            data = response.json()
            milestones = []

            # Parse root and children
            if data.get("children"):
                for child in data["children"]:
                    milestone = self._parse_iteration(child)
                    milestones.append(milestone)

            return milestones

        except httpx.TimeoutException:
            raise NetworkError("Azure DevOps API timeout", is_timeout=True)
        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _get_pat(self) -> Optional[str]:
        """Get Personal Access Token from environment."""
        return os.environ.get("AZURE_DEVOPS_PAT")

    def _ensure_authenticated(self) -> None:
        """Verify Azure DevOps is configured."""
        if not self.config.organization:
            raise AuthenticationError(
                "Azure DevOps organization not configured",
                provider="Azure DevOps",
            )
        if not self.config.project:
            raise AuthenticationError(
                "Azure DevOps project not configured",
                provider="Azure DevOps",
            )
        if not self._get_pat():
            raise AuthenticationError(
                "AZURE_DEVOPS_PAT environment variable not set",
                provider="Azure DevOps",
            )

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with authentication."""
        if self._client is None:
            pat = self._get_pat()
            self._client = httpx.Client(
                timeout=self.timeout,
                auth=("", pat or ""),
            )
        return self._client

    def _get_repository_id(self) -> str:
        """Get the repository ID for the current project."""
        try:
            client = self._get_client()
            url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_apis/git/repositories"
            )

            response = client.get(
                url,
                params={"api-version": self.config.api_version},
            )

            if response.status_code != 200:
                raise ProviderError("Failed to get repository list")

            data = response.json()
            repos = data.get("value", [])

            if not repos:
                raise ProviderError("No repositories found in project")

            # Return the first repository ID
            return repos[0]["id"]

        except httpx.RequestError as e:
            raise NetworkError(f"Azure DevOps network error: {e}")

    def _parse_work_item(self, data: dict) -> Issue:
        """Parse Azure DevOps work item into Issue model."""
        fields = data.get("fields", {})

        # Parse state
        state_str = fields.get("System.State", "Active")
        state = IssueState.OPEN if state_str in ("Active", "New") else IssueState.CLOSED

        # Parse type
        work_item_type = fields.get("System.WorkItemType", "Task")
        issue_type = AzureDevOpsLabelMapper.work_item_type_to_type(work_item_type)

        # Parse tags as labels
        tags_str = fields.get("System.Tags", "")
        labels = []
        if tags_str:
            for tag in tags_str.split(";"):
                tag = tag.strip()
                if tag:
                    labels.append(Label(name=tag))

        # Build URL
        url = data.get("url", "")
        if "_apis/wit/workitems" in url:
            # Convert API URL to web URL
            web_url = (
                f"https://dev.azure.com/{self.config.organization}/"
                f"{self.config.project}/_workitems/edit/{data['id']}"
            )
        else:
            web_url = url

        return Issue(
            id=self._make_unified_id("issue", str(data["id"])),
            provider_id=str(data["id"]),
            title=fields.get("System.Title", ""),
            body=fields.get("System.Description"),
            state=state,
            type=issue_type,
            url=web_url,
            created_at=self._parse_datetime(fields.get("System.CreatedDate", "")),
            updated_at=self._parse_datetime(fields.get("System.ChangedDate", "")),
            labels=labels,
        )

    def _parse_pull_request(self, data: dict) -> PullRequest:
        """Parse Azure DevOps pull request into PullRequest model."""
        # Parse state
        status = data.get("status", "active")
        if status == "completed":
            state = PRState.MERGED
        elif status == "abandoned":
            state = PRState.CLOSED
        else:
            state = PRState.OPEN

        # Parse branches
        source_ref = data.get("sourceRefName", "")
        target_ref = data.get("targetRefName", "")
        source_branch = source_ref.replace("refs/heads/", "")
        target_branch = target_ref.replace("refs/heads/", "")

        # Build URL
        web_url = (
            f"https://dev.azure.com/{self.config.organization}/"
            f"{self.config.project}/_git/pullrequest/{data['pullRequestId']}"
        )

        merged_at = None
        if data.get("closedDate") and state == PRState.MERGED:
            merged_at = self._parse_datetime(data["closedDate"])

        return PullRequest(
            id=self._make_unified_id("pr", str(data["pullRequestId"])),
            provider_id=str(data["pullRequestId"]),
            title=data.get("title", ""),
            body=data.get("description"),
            source_branch=source_branch,
            target_branch=target_branch,
            state=state,
            url=web_url,
            created_at=self._parse_datetime(data.get("creationDate", "")),
            merged_at=merged_at,
        )

    def _parse_iteration(self, data: dict) -> Milestone:
        """Parse Azure DevOps iteration into Milestone model."""
        attributes = data.get("attributes", {})

        # Determine state based on dates
        state = MilestoneState.OPEN
        if attributes.get("finishDate"):
            finish_date = self._parse_datetime(attributes["finishDate"])
            if finish_date < datetime.now(finish_date.tzinfo):
                state = MilestoneState.CLOSED

        due_date = None
        if attributes.get("finishDate"):
            due_date = self._parse_datetime(attributes["finishDate"])

        return Milestone(
            id=self._make_unified_id("ms", str(data["id"])),
            provider_id=str(data["id"]),
            title=data.get("name", ""),
            description=None,  # ADO iterations don't have descriptions
            state=state,
            due_date=due_date,
        )

    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse Azure DevOps datetime string."""
        if not date_str:
            return datetime.now()
        try:
            # Handle Azure DevOps datetime format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now()
