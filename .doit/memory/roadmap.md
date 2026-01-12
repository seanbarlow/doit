# Project Roadmap

**Project**: DoIt
**Last Updated**: 2026-01-10
**Managed by**: `/doit.roadmapit`

## Vision

A simple, intuitive task management app that helps individuals organize their work, track progress, and stay productive.

---

## Active Requirements

### P1 - Critical (Must Have for MVP)

<!-- Items that are essential for minimum viable product or blocking other work -->

- [ ] Create and manage tasks with titles and descriptions
  - **Rationale**: Core functionality - users must be able to create tasks to use the app

- [ ] Mark tasks as complete/incomplete
  - **Rationale**: Essential for tracking progress and productivity

### P2 - High Priority (Significant Business Value)

<!-- Items with high business value, scheduled for near-term delivery -->

- [ ] Organize tasks into lists or categories
  - **Rationale**: Helps users group related tasks and stay organized

- [ ] Set due dates and reminders
  - **Rationale**: Critical for time-sensitive task management

- [ ] Filter and search tasks
  - **Rationale**: Improves usability as task list grows

- [ ] Task priority levels
  - **Rationale**: Allows users to distinguish between urgent and non-urgent tasks within each list

- [ ] Subtasks / Checklists
  - **Rationale**: Enables breaking down complex tasks into smaller, manageable steps

- [ ] Tags and labels for tasks
  - **Rationale**: Enables better organization - complements lists/categories feature (promoted from P3)

### P3 - Medium Priority (Valuable)

<!-- Items that add value but can wait for later iterations -->

- [ ] Recurring tasks
  - **Rationale**: Automates repetitive task creation

- [ ] Notes and attachments
  - **Rationale**: Provides context for tasks beyond title/description

- [ ] Mobile app sync
  - **Rationale**: Enables access across devices - users can manage tasks from phone and desktop

### P4 - Low Priority (Nice to Have)

<!-- Items in the backlog, considered for future development -->

<!-- No P4 items currently -->

---

## Deferred Items

<!-- Items that were considered but intentionally deferred with reason -->

| Item                      | Original Priority | Deferred Date | Reason                            |
|---------------------------|-------------------|---------------|-----------------------------------|
| Dark mode / Theme support | P4                | 2026-01-10    | Focus on core functionality first |

---

## Notes

- Items marked with `[###-feature-name]` reference link to feature branches for tracking
- When a feature completes via `/doit.checkin`, matching items are moved to `completed_roadmap.md`
- Use `/doit.roadmapit add [item]` to add new items
- Use `/doit.roadmapit defer [item]` to move items to deferred section
- Use `/doit.roadmapit reprioritize` to change item priorities
