# Release Notes - v0.1.15

**Release Date**: 2026-01-30

## Highlights

This release introduces the **Research Command** (`/doit.researchit`), a new pre-specification workflow stage designed for Product Owners to capture business requirements through interactive AI-assisted Q&A.

## What's New

### Research Command for Product Owners

The `/doit.researchit` command is a template-based slash command that guides Product Owners through a structured Q&A session to capture business requirements **before** technical specification begins.

**Key Features**:

- **12-question interactive workflow** across 4 phases:
  - Phase 1: Problem Understanding (what problem, who experiences it, current state)
  - Phase 2: Users and Goals (personas, success criteria, user types)
  - Phase 3: Requirements and Constraints (must-haves, nice-to-haves, boundaries)
  - Phase 4: Success Metrics (how to measure success and failure)

- **Business-focused**: No technology questions - keeps focus on user value and business outcomes

- **4 research artifacts generated**:
  - `research.md` - Problem statement, target users, business goals
  - `user-stories.md` - Given/When/Then user stories with personas
  - `interview-notes.md` - Stakeholder interview templates
  - `competitive-analysis.md` - Competitor comparison framework

- **Session resume support**: Save progress mid-session and continue later

- **Seamless specit integration**: Research artifacts automatically loaded by `/doit.specit`

### Workflow Enhancement

The Do-It workflow now includes an optional pre-specification stage:

```
┌─────────────────────────────────────────────────────────────────┐
│  doit Workflow (NEW stage)                                      │
│  ● researchit → ○ specit → ○ planit → ○ taskit → ○ implementit │
└─────────────────────────────────────────────────────────────────┘
```

## Usage

### For Product Owners

```
/doit.researchit customer-feedback
```

The AI assistant will guide you through the Q&A session, then generate all research artifacts in `specs/{feature-name}/`.

### For Developers

After research is complete, run `/doit.specit` as usual - it will automatically load the research artifacts as context for specification generation.

## Breaking Changes

None.

## Upgrade Instructions

1. Update to the latest version:
   ```bash
   pip install --upgrade doit-toolkit-cli
   ```

2. Run init update to get new templates:
   ```bash
   doit init --update
   ```

3. Start using `/doit.researchit` in your AI assistant

## Contributors

- Claude Code implementation assistance

## Full Changelog

See [CHANGELOG.md](./CHANGELOG.md) for complete release history.
