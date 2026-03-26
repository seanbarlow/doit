# MCP Tool Contracts

**Feature**: 055-mcp-server
**Date**: 2026-03-26

## Tool: doit_validate

**Description**: Validate specification files against quality rules

**Parameters**:

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| spec_path | string | No | null | Path to specific spec to validate. If omitted, validates all specs. |

**Response Schema**:

```json
{
  "specs": [
    {
      "name": "string",
      "path": "string",
      "passed": "boolean",
      "score": "number",
      "issues": [
        {
          "severity": "string (error|warning|info)",
          "line": "number",
          "message": "string",
          "recommendation": "string"
        }
      ]
    }
  ],
  "summary": {
    "total": "number",
    "passed": "number",
    "warned": "number",
    "failed": "number",
    "average_score": "number"
  }
}
```

---

## Tool: doit_status

**Description**: Get project status including spec states and roadmap

**Parameters**:

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| include_roadmap | boolean | No | false | Include active roadmap items in response |
| status_filter | string | No | null | Filter by status: draft, in_progress, complete, approved |
| blocking_only | boolean | No | false | Show only specs blocking commits |

**Response Schema**:

```json
{
  "specs": [
    {
      "name": "string",
      "status": "string",
      "last_modified": "string (ISO 8601)",
      "is_blocking": "boolean",
      "validation_score": "number | null"
    }
  ],
  "summary": {
    "total": "number",
    "by_status": {
      "draft": "number",
      "in_progress": "number",
      "complete": "number",
      "approved": "number"
    },
    "blocking_count": "number"
  },
  "roadmap": [
    {
      "title": "string",
      "priority": "string (P1|P2|P3|P4)",
      "status": "string"
    }
  ]
}
```

---

## Tool: doit_tasks

**Description**: List tasks from a feature's tasks.md with completion status

**Parameters**:

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| feature_name | string | No | null | Feature name (e.g., "055-mcp-server"). Auto-detected from branch if omitted. |
| include_dependencies | boolean | No | false | Include task dependency relationships |

**Response Schema**:

```json
{
  "tasks": [
    {
      "id": "string",
      "description": "string",
      "completed": "boolean",
      "priority": "string | null",
      "requirement_refs": ["string"],
      "dependencies": ["string"]
    }
  ],
  "summary": {
    "total": "number",
    "completed": "number",
    "pending": "number",
    "completion_percentage": "number"
  }
}
```

---

## Tool: doit_context

**Description**: Load project context (constitution, tech stack, roadmap)

**Parameters**:

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| sources | array of string | No | null | Filter to specific sources: constitution, tech_stack, roadmap, completed_roadmap |

**Response Schema**:

```json
{
  "sources": [
    {
      "name": "string",
      "path": "string",
      "content": "string",
      "tokens": "number",
      "status": "string (complete|summarized|truncated|missing)"
    }
  ],
  "summary": {
    "total_sources": "number",
    "total_tokens": "number"
  }
}
```

---

## Tool: doit_scaffold

**Description**: Create doit project directory structure

**Parameters**:

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| tech_stack | string | No | null | Tech stack override (e.g., "python-fastapi"). Uses constitution if omitted. |

**Response Schema**:

```json
{
  "created_dirs": ["string"],
  "created_files": ["string"],
  "skipped": ["string"],
  "summary": "string"
}
```

---

## Tool: doit_verify

**Description**: Verify doit project structure completeness

**Parameters**: None

**Response Schema**:

```json
{
  "checks": [
    {
      "name": "string",
      "passed": "boolean",
      "message": "string"
    }
  ],
  "all_passed": "boolean",
  "summary": "string"
}
```

---

## Resources

| URI | Name | MIME Type | Description |
| --- | --- | --- | --- |
| doit://memory/constitution | Project Constitution | text/markdown | Project principles and governance |
| doit://memory/roadmap | Project Roadmap | text/markdown | Prioritized feature roadmap |
| doit://memory/tech-stack | Tech Stack | text/markdown | Technology decisions |
