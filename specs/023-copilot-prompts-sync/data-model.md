# Data Model: GitHub Copilot Prompts Synchronization

**Feature**: 023-copilot-prompts-sync
**Date**: 2026-01-15

## Entity Relationships

<!-- BEGIN:AUTO-GENERATED section="er-diagram" -->
```mermaid
erDiagram
    CommandTemplate ||--|| PromptFile : "generates"
    CommandTemplate ||--o| SyncStatus : "has"
    SyncResult ||--|{ FileOperation : "contains"

    CommandTemplate {
        string name PK
        string path
        datetime modified_at
        string description
        string content
    }

    PromptFile {
        string name PK
        string path
        datetime generated_at
        string content
    }

    SyncStatus {
        string command_name FK
        string status
        datetime checked_at
        string reason
    }

    FileOperation {
        string file_path
        string operation_type
        boolean success
        string message
    }
```
<!-- END:AUTO-GENERATED -->

## Entities

### CommandTemplate

Represents a doit command template file in `.doit/templates/commands/`.

| Field | Type | Description |
| ----- | ---- | ----------- |
| name | string | Command name (e.g., "doit.checkin") |
| path | Path | Absolute file path |
| modified_at | datetime | Last modification timestamp |
| description | string | Extracted from YAML frontmatter |
| content | string | Full file content |

**Source**: Files matching `.doit/templates/commands/doit.*.md`

### PromptFile

Represents a generated GitHub Copilot prompt file in `.github/prompts/`.

| Field | Type | Description |
| ----- | ---- | ----------- |
| name | string | Prompt name (e.g., "doit.checkin.prompt") |
| path | Path | Absolute file path |
| generated_at | datetime | Generation timestamp |
| content | string | Transformed content |

**Target**: Files written to `.github/prompts/doit.*.prompt.md`

### SyncStatus

Represents the synchronization state between a command and its prompt.

| Field | Type | Description |
| ----- | ---- | ----------- |
| command_name | string | Reference to CommandTemplate |
| status | SyncStatusEnum | Current sync state |
| checked_at | datetime | When status was last checked |
| reason | string | Explanation for status |

**Status Values**:

<!-- BEGIN:AUTO-GENERATED section="sync-status-state" -->
```mermaid
stateDiagram-v2
    [*] --> Missing : prompt not found
    [*] --> Synchronized : prompt matches command
    [*] --> OutOfSync : command newer than prompt

    Missing --> Synchronized : sync command
    OutOfSync --> Synchronized : sync command
    Synchronized --> OutOfSync : command modified
```
<!-- END:AUTO-GENERATED -->

| Status | Description |
| ------ | ----------- |
| `SYNCHRONIZED` | Prompt exists and matches command |
| `OUT_OF_SYNC` | Command modified after prompt generation |
| `MISSING` | No corresponding prompt file exists |

### SyncResult

Represents the result of a synchronization operation.

| Field | Type | Description |
| ----- | ---- | ----------- |
| total_commands | int | Number of commands found |
| synced | int | Number successfully synced |
| skipped | int | Number skipped (already in sync) |
| failed | int | Number that failed |
| operations | list[FileOperation] | Details of each operation |

### FileOperation

Represents a single file operation during sync.

| Field | Type | Description |
| ----- | ---- | ----------- |
| file_path | string | Path of the file operated on |
| operation_type | OperationType | Type of operation |
| success | bool | Whether operation succeeded |
| message | string | Success/error message |

**Operation Types**:

| Type | Description |
| ---- | ----------- |
| `CREATED` | New prompt file created |
| `UPDATED` | Existing prompt file updated |
| `SKIPPED` | File already in sync |
| `FAILED` | Operation failed |

## Data Flow

```mermaid
flowchart LR
    subgraph Input
        CMD[Command Templates]
    end

    subgraph Processing
        READ[Read Template]
        PARSE[Parse YAML + Content]
        TRANSFORM[Transform Content]
        VALIDATE[Validate Output]
    end

    subgraph Output
        PROMPT[Prompt Files]
        REPORT[Sync Report]
    end

    CMD --> READ --> PARSE --> TRANSFORM --> VALIDATE --> PROMPT
    VALIDATE --> REPORT
```

## Validation Rules

### CommandTemplate Validation

- File must exist and be readable
- Must have `.md` extension
- Must match pattern `doit.*.md`
- Should have valid YAML frontmatter (graceful degradation if missing)

### PromptFile Validation

- Output path must be writable
- Content must be valid markdown
- YAML frontmatter must be valid if present

### Naming Convention

| Input | Output |
| ----- | ------ |
| `doit.checkin.md` | `doit.checkin.prompt.md` |
| `doit.specit.md` | `doit.specit.prompt.md` |
| `doit.{name}.md` | `doit.{name}.prompt.md` |

Transformation: Replace `.md` suffix with `.prompt.md`
