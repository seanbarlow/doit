# Research: Spec Status Dashboard

**Feature**: 032-status-dashboard
**Date**: 2026-01-16

## Overview

This document captures research findings and design decisions for the `doit status` command.

---

## Research Tasks

### R1: Existing Validation Integration

**Question**: How does the existing SpecValidator work and how do we integrate with it?

**Findings**:
- SpecValidator exists in `src/doit_cli/services/spec_validator.py` (Feature 029)
- Provides 10 validation rules for spec quality
- Returns ValidationResult with pass/fail status and error details
- Used by git hooks to block commits on validation failure

**Decision**: Reuse SpecValidator directly - don't duplicate validation logic
**Rationale**: Ensures status command shows same results as git hooks
**Alternatives Rejected**: Creating separate validation - would cause divergence

---

### R2: Spec Status Parsing

**Question**: How do we extract status from spec.md files?

**Findings**:
- Status is in frontmatter: `**Status**: Draft`
- Valid statuses: Draft, In Progress, Complete, Approved
- Status line format is consistent across all specs
- Can use regex or line-by-line parsing

**Decision**: Parse `**Status**:` line using regex pattern
**Rationale**: Simple, reliable, no external dependencies
**Alternatives Rejected**: YAML frontmatter parser - overkill for single field

---

### R3: Output Formatting

**Question**: What's the best way to structure multiple output formats?

**Findings**:
- Rich library supports tables, colors, and panels
- JSON serialization via dataclasses_json or manual dict conversion
- Markdown tables follow standard GFM syntax

**Decision**: Use formatter classes with common interface
**Rationale**: Clean separation, easy to add new formats
**Alternatives Rejected**: Single function with format switch - less extensible

---

### R4: Performance for Large Projects

**Question**: How do we ensure performance for projects with many specs?

**Findings**:
- Most projects have 10-50 specs
- Spec scanning is I/O bound (file reads)
- Validation is CPU bound (regex matching)
- Rich table rendering is fast for reasonable row counts

**Decision**: Sequential processing is sufficient for target scale
**Rationale**: Projects with 50 specs complete in <2 seconds
**Alternatives Rejected**: Async/parallel processing - premature optimization

---

### R5: Blocking Status Logic

**Question**: When should a spec be marked as "blocking"?

**Findings**:
- Git hooks run validation on changed specs
- Specs with status "In Progress" are validated
- Specs with status "Draft" may or may not be validated (configurable)
- Validation failures block commits

**Decision**: Mark as "Blocking" if:
1. Status is "In Progress" AND validation fails, OR
2. Status is "Draft" AND validation fails AND spec is in git staging

**Rationale**: Matches actual git hook behavior
**Alternatives Rejected**: Always validate all specs - too noisy for drafts

---

## Resolved Clarifications

No [NEEDS CLARIFICATION] markers were present in the specification. All requirements were sufficiently detailed.

---

## Key Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Validation | Reuse SpecValidator | Consistency with git hooks |
| Status parsing | Regex on markdown | Simple, no dependencies |
| Output formats | Formatter classes | Extensible, clean separation |
| Processing | Sequential | Sufficient for 50+ specs |
| Blocking logic | Match git hook rules | User expectations |
