# Research: GitLab Git Provider Support

**Feature**: 048-gitlab-provider
**Date**: 2026-01-22
**Status**: Complete

## Research Summary

This document captures technical decisions and research findings for implementing the GitLabProvider.

---

## 1. GitLab API Version Selection

**Decision**: Use GitLab REST API v4

**Rationale**:
- REST API v4 is the current stable API (available since GitLab 9.0, 2017)
- Well-documented with comprehensive endpoint coverage
- Consistent with existing Azure DevOps provider pattern (uses REST)
- GraphQL API is out of scope per spec

**Alternatives Considered**:
- GitLab GraphQL API - Rejected: Out of scope, more complex for CRUD operations
- python-gitlab SDK - Rejected: Adds dependency; httpx provides sufficient functionality

---

## 2. Authentication Method

**Decision**: Personal Access Token (PAT) via `GITLAB_TOKEN` environment variable

**Rationale**:
- Simplest authentication method for CLI tools
- Consistent with provider configuration pattern from 047-provider-config-wizard
- Token stored in environment, not in config files (security best practice)
- Supports both gitlab.com and self-hosted instances

**Alternatives Considered**:
- OAuth2 flow - Rejected: Out of scope per spec, adds complexity for CLI usage
- CI Job Token - Rejected: Only works in GitLab CI context

**Token Scope Requirements**:
- `api` - Full API access (required for all operations)

---

## 3. HTTP Client Selection

**Decision**: Use httpx (already in tech stack)

**Rationale**:
- Already a project dependency per tech-stack.md
- Async support available if needed in future
- SOCKS proxy support via truststore
- Consistent with Azure DevOps provider implementation

**Alternatives Considered**:
- requests - Rejected: httpx already in stack, no benefit to adding requests
- aiohttp - Rejected: Async not required for current implementation

---

## 4. Project Identification Strategy

**Decision**: URL-encoded project path (e.g., `owner%2Frepo`)

**Rationale**:
- GitLab API accepts both numeric project IDs and URL-encoded paths
- Path-based identification is more human-readable
- Can be derived from git remote URL without API call
- Pattern: Extract from remote like `gitlab.com/owner/repo.git` → `owner%2Frepo`

**Alternatives Considered**:
- Numeric project ID - Rejected: Requires API call to resolve from path

---

## 5. Label Strategy for Issue Types

**Decision**: Use GitLab labels with predefined names

**Rationale**:
- GitLab doesn't have native issue types (unlike Azure DevOps)
- Labels are the standard way to categorize issues in GitLab
- Auto-create labels if they don't exist (FR-054)

**Label Mapping**:

| Unified IssueType | GitLab Label |
| ----------------- | ------------ |
| EPIC | `Epic` |
| FEATURE | `Feature` |
| BUG | `Bug` |
| TASK | `Task` |
| USER_STORY | `User Story` |

**Priority Labels**:

| Priority | GitLab Label |
| -------- | ------------ |
| P1 | `priority::1` |
| P2 | `priority::2` |
| P3 | `priority::3` |
| P4 | `priority::4` |

**Alternatives Considered**:
- GitLab Premium Epics feature - Rejected: Not available on free tier, using label fallback per spec

---

## 6. Issue Relationships (Epic Linking)

**Decision**: Use GitLab Issue Links API (`/issues/:iid/links`)

**Rationale**:
- FR-016 requires linking issues to parent epics
- GitLab supports related issues via the Links API
- Works on all GitLab tiers (free, premium, ultimate)

**Link Type**: `relates_to` (standard relationship)

**Alternatives Considered**:
- GitLab Premium parent/child epics - Rejected: Tier-restricted
- Description-based linking (mention in body) - Rejected: Not queryable

---

## 7. Error Handling Strategy

**Decision**: Map HTTP status codes to provider exceptions

**Mapping**:

| HTTP Status | Provider Exception | Message Pattern |
| ----------- | ----------------- | --------------- |
| 401 | `AuthenticationError` | "GitLab authentication failed. Check GITLAB_TOKEN." |
| 403 | `AuthenticationError` | "Insufficient permissions for {operation}." |
| 404 | `ResourceNotFoundError` | "{resource_type} {id} not found." |
| 429 | `RateLimitError` | Retry after `Retry-After` header value |
| 5xx | `NetworkError` | "GitLab server error. Try again later." |
| Timeout | `NetworkError` | "Request timed out. Check network connection." |

**Rationale**:
- Consistent with existing exception hierarchy in `exceptions.py`
- Provides actionable error messages per spec FR-040 through FR-044

---

## 8. Self-Hosted GitLab Support

**Decision**: Configurable base URL with gitlab.com default

**Rationale**:
- FR-003 requires self-hosted support
- Base URL stored in provider.yaml as `host` field
- Auto-detect from git remote URL (e.g., `git@gitlab.mycompany.com:org/repo.git`)

**URL Pattern**:
- gitlab.com: `https://gitlab.com/api/v4/`
- Self-hosted: `https://{host}/api/v4/`

---

## 9. Merge Request Terminology

**Decision**: Use "Merge Request" / "MR" in user-facing output

**Rationale**:
- FR-023 requires GitLab-appropriate terminology
- Internally use `PullRequest` model for consistency
- Transform terminology in Rich output formatting

---

## 10. Rate Limiting Handling

**Decision**: Exponential backoff with `@with_retry()` decorator

**Rationale**:
- Existing decorator in `base.py` handles retry logic
- GitLab returns `Retry-After` header on 429 responses
- Maximum 3 retries with exponential backoff (1s, 2s, 4s)

---

## API Endpoint Reference

| Operation | Method | Endpoint |
| --------- | ------ | -------- |
| Validate token | GET | `/api/v4/user` |
| Create issue | POST | `/api/v4/projects/:id/issues` |
| Get issue | GET | `/api/v4/projects/:id/issues/:iid` |
| List issues | GET | `/api/v4/projects/:id/issues` |
| Update issue | PUT | `/api/v4/projects/:id/issues/:iid` |
| Create MR | POST | `/api/v4/projects/:id/merge_requests` |
| Get MR | GET | `/api/v4/projects/:id/merge_requests/:iid` |
| List MRs | GET | `/api/v4/projects/:id/merge_requests` |
| Create milestone | POST | `/api/v4/projects/:id/milestones` |
| Get milestone | GET | `/api/v4/projects/:id/milestones/:id` |
| List milestones | GET | `/api/v4/projects/:id/milestones` |
| Update milestone | PUT | `/api/v4/projects/:id/milestones/:id` |
| Create issue link | POST | `/api/v4/projects/:id/issues/:iid/links` |
| Create label | POST | `/api/v4/projects/:id/labels` |
| List labels | GET | `/api/v4/projects/:id/labels` |

---

## Outstanding Questions

None - all technical decisions resolved.
