# Mid-Course User Stories

## Feature 1: Due dates + overdue filter

**Story 1 — Set a due date when creating a task**
As a team member, I want to give a task a due date so that I know when it needs to be finished.
- Creating a task with a valid ISO date (`YYYY-MM-DD`) succeeds and the date is returned in the response.
- Due date is optional; omitting it leaves the task with no due date.
- An invalid date value (e.g. `"next tuesday"`) returns HTTP 422.

**Story 2 — See which tasks are overdue**
As a team member, I want overdue tasks to be visually flagged so that I don't lose track of them.
- A task with a due date in the past and a status other than Done shows a red "Overdue" pill on its card.
- A Done task with a past due date does **not** show as overdue.
- A task with no due date shows no pill at all.

**Story 3 — Update a task's due date**
As a team member, I want to change a task's due date so that I can reschedule it.
- `PATCH /tasks/{id}` with a new `due_date` updates only that field.
- Sending `due_date: null` clears the due date.

**Story 4 — Filter the board to overdue tasks only**
As a team member, I want to filter the board to overdue tasks so that I can focus on what's late.
- Checking "Overdue only" re-fetches the board showing only overdue tasks.
- Unchecking it restores the full board.
- Empty columns still render (they don't disappear) if a column has no overdue tasks.

**AI assumption I reviewed:** the first design instinct for "overdue" was a Pydantic `@computed_field` inside `TaskResponse`. I went with a plain shared function (`is_task_overdue()`) instead, called directly by the storage filter — simpler to read and test for a learning project.

---

## Feature 2: Tags / labels

**Story 1 — Add tags when creating a task**
As a team member, I want to tag a task (e.g. "backend", "urgent") so that I can categorize work.
- Creating a task with a list of trimmed, non-empty tags succeeds and returns them unchanged.
- Omitting tags leaves the task with an empty tag list, not an error.

**Story 2 — Reject invalid tags**
As a team member, I want blank or excessive tags rejected so that the tag list stays clean and useful.
- A blank or whitespace-only tag returns HTTP 422.
- More than 5 tags on one task returns HTTP 422.

**Story 3 — Update a task's tags**
As a team member, I want to change a task's tags so that its categorization stays current.
- `PATCH /tasks/{id}` with a new `tags` list fully replaces the existing tags.
- Updating an unrelated field (e.g. priority) leaves existing tags untouched.

**Story 4 — Filter the board by tag**
As a team member, I want to filter tasks by tag so that I can see just one category of work.
- Typing a tag into the filter box and confirming re-fetches the board showing only tasks with that tag.
- Clearing the filter restores the full board.

**AI assumption I reviewed:** tags are deduplicated (case-sensitive) but not lowercased. "Backend" and "backend" are currently treated as two different tags — a deliberate choice to not silently override a team's own casing convention.