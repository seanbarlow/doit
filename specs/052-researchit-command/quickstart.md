# Quickstart: Research Command for Product Owners

**Feature**: 052-researchit-command
**Date**: 2026-01-29

## Overview

The `/doit.researchit` command helps Product Owners capture business requirements before technical specification. It's a **slash command** that you run in your AI assistant (Claude Code, GitHub Copilot, Cursor), which then guides you through an interactive Q&A session.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  You type: /doit.researchit customer-feedback                  │
│                                                                 │
│  AI Assistant:                                                  │
│  - Reads the command template                                   │
│  - Asks you 12 guided questions about your feature              │
│  - Captures your answers                                        │
│  - Generates research artifacts (research.md, user-stories.md)  │
│  - Recommends next step: /doit.specit                          │
└─────────────────────────────────────────────────────────────────┘
```

## Getting Started

### Prerequisites

- AI coding assistant (Claude Code, GitHub Copilot, Cursor)
- A doit project (run `doit init` if needed)
- A feature idea to research

### Basic Usage

In your AI assistant chat, type:

```
/doit.researchit customer-feedback
```

The AI will then ask you questions like:
- "What problem are you trying to solve?"
- "Who are the primary users?"
- "What does success look like?"

Answer naturally in the chat. The AI captures your responses.

## Workflow Position

```
┌─────────────────────────────────────────────────────────────────┐
│  doit Workflow                                                  │
│  ○ researchit → ● specit → ○ planit → ○ taskit → ○ implementit  │
│       ↑                                                         │
│  NEW: Pre-specification stage for Product Owners                │
└─────────────────────────────────────────────────────────────────┘
```

## Q&A Session Guide

The AI asks questions in four phases:

### Phase 1: Problem Understanding

- What problem are you solving?
- Who experiences this problem?
- What happens today without a solution?

### Phase 2: Users and Goals

- Who are the primary users?
- What does success look like?
- Different user types?

### Phase 3: Requirements

- Must-have features?
- Nice-to-have features?
- What should it NOT do?
- Any constraints?

### Phase 4: Success Metrics

- How will you measure success?
- What would failure look like?

## Output Files

After the Q&A, the AI generates:

```
specs/{feature-name}/
├── research.md              # Problem statement, users, goals
├── user-stories.md          # Given/When/Then scenarios
├── interview-notes.md       # Stakeholder interview templates
└── competitive-analysis.md  # Competitor comparison structure
```

## Tips for Product Owners

1. **Be specific** - "Users can search products by category" is better than "Search functionality"
2. **Think about users** - Who exactly will use this? What are their goals?
3. **Define success** - How will you know the feature worked?
4. **Set boundaries** - What should this feature NOT do?

## What Happens Next

After research is complete, the AI will recommend:

```
Recommended: Run /doit.specit to create a technical specification from this research.
```

When you run `/doit.specit`, it automatically loads your research artifacts as context, making specification faster and more accurate.

## Key Difference from Other Commands

| Command | Who Uses It | Purpose |
|---------|-------------|---------|
| `/doit.researchit` | Product Owners | Capture business requirements (no tech) |
| `/doit.specit` | Developers | Create technical specification |
| `/doit.planit` | Developers | Design implementation approach |

The **researchit** command deliberately avoids technology questions - it's focused purely on business value and user needs.

## Example Session

Here's what a typical research session looks like:

```
You: /doit.researchit customer-feedback

AI: I'll help you research the "customer-feedback" feature. Let me ask some questions
    to understand the requirements.

    **Phase 1: Problem Understanding**

    What problem are you trying to solve with this feature?

You: Customers have no way to tell us what they think about our products.
     We lose valuable feedback that could improve our offerings.

AI: Got it - lack of customer feedback visibility. Who currently experiences this problem?

You: Our product team can't see what customers think, and customers feel unheard.

AI: And what happens today without this solution?

You: Product decisions are made without customer input. Some customers complain
     on social media instead of telling us directly.

AI: Let me summarize Phase 1: You're solving the gap between customer opinions and
    product decisions. Product teams lack insight, customers lack a voice.
    Is this accurate?

You: Yes, that's right.

AI: **Phase 2: Users and Goals**

    Who are the primary users of this feature?

You: Customers who buy our products, and product managers who need insights.

[... session continues through all 4 phases ...]

AI: ## Research Session Complete

    ### Files Created

    | File | Description |
    |------|-------------|
    | specs/053-customer-feedback/research.md | Problem, users, requirements |
    | specs/053-customer-feedback/user-stories.md | 5 user stories created |
    | specs/053-customer-feedback/interview-notes.md | Interview templates |
    | specs/053-customer-feedback/competitive-analysis.md | Competitor framework |

    **Recommended**: Run `/doit.specit` to create a technical specification.
```

## Resuming a Session

If you need to pause and come back later:

```
You: /doit.researchit customer-feedback

AI: I found existing research for "customer-feedback". Would you like to:
    - **Resume**: Continue adding to the existing research
    - **Start Fresh**: Create new research (existing files will be backed up)

You: Resume

AI: Great, loading your previous answers...
    You've completed Phases 1 and 2. Let's continue with Phase 3.
```

## Integration with Specit

After research is complete, `/doit.specit` automatically uses your research:

```text
You: /doit.specit customer-feedback

AI: Loading research artifacts from specs/053-customer-feedback/...
    - Found research.md (problem statement, users, requirements)
    - Found user-stories.md (5 user stories)

    Using this context to generate the technical specification...
```

This ensures continuity from business requirements to technical specification.
