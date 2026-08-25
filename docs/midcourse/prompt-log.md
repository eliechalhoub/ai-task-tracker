# Prompt Log — Mid-Course Project

## Feature 1: Due dates + overdue filter

### Prompt 1 (weak → strong rewrite)

**Weak version:** "Add due dates to tasks."
**Why it's weak:** no field name, no validation rule, no output format.

**Strong version used:**

> Add an optional `due_date` field to `TaskCreate`, `TaskUpdate`, and `TaskResponse` in `app/models.py`, using Python's `date` type so Pydantic validates the ISO format automatically. Keep `extra="forbid"` on the input models. Don't add any extra business rule — just format validation. Wire it through storage, and add an `overdue` query param to `GET /tasks` using a shared helper.

**AI output:** the field additions, plus a first version of the overdue rule as a `@computed_field`.
**Accepted:** the field additions and format-validation-only approach.
**Rejected:** the `@computed_field` — asked for a plain shared function instead.

### Prompt 2

> Write pytest tests for the due_date feature: valid due date, invalid format, updating a due date, and the overdue filter. Use relative dates so tests don't break based on run date.

**AI output:** four tests, including one confirming a Done task with a past due date is excluded from the overdue filter.
**Accepted as-is.**

### Prompt 3

> Add a due-date input and "Overdue only" filter to the frontend. Show a red "Overdue" pill using the same rule as the backend.

**AI output:** modal field, filter checkbox, `isOverdue()` helper, `buildTasksUrl()`.
**Accepted, with one fix along the way:** found `retryBtn` was declared but never wired to a click handler — a Module 3 gap. Fixed in the same pass.

---

## Feature 2: Tags / labels

### Prompt 1

> Add a `tags: list[str]` field to the models. Validate: trim, reject blank, max 5 tags, max 30 chars each, deduplicate. Same pattern as the existing title validator for skip-when-omitted on update.

**AI output:** shared `_clean_tags()` function plus two validators.
**Accepted as-is.**

### Prompt 2

> Write tests for: create with tags, reject blank tag, update tags (replace), filter by tag, tags survive unrelated update.

**AI output:** all 5 tests.
**Accepted as-is.**

### Prompt 3

> Add a tags input (comma-separated) and tag chips to cards. Add a tag filter. Route tag-specific 422s to the tags field, not the generic banner.

**AI output:** comma parsing, chip rendering, 422 routing by message content.
**Accepted, with a noted trade-off:** the parser silently drops empty entries from double commas rather than surfacing a blank-tag error client-side — the backend's blank-tag rejection is mainly reachable via the API directly.
