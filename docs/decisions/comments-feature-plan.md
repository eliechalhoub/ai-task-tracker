# Comments on Tasks — Design Plan

**Status:** Planning only — no implementation, no files created or edited in `app/`, `tests/`, or `frontend/`.
**Scope note:** this repo has no existing sub-resource (nested) routes, no comment-like feature precedent, and only one frontend file. Several structural decisions below are genuinely new to this codebase, not extensions of an established pattern — flagged explicitly where that's the case.

## 1. Data Model

New Pydantic models, following the schema conventions already in `app/models.py`:

- **`CommentCreate`** — client-facing input: `author: str` (1–100 chars), `body: str` (1–2000 chars). `task_id` should come from the URL path, not the request body, mirroring how `task_id` is never part of `TaskUpdate`'s body (`app/models.py:103-112`) but always a path parameter in `app/main.py`.
- **`CommentResponse`** — output model: `id`, `task_id`, `author`, `body`, `created_at`. No `CommentUpdate` model proposed, since the given field list has no `updated_at` — see Open Question 2.
- Both should use `model_config = ConfigDict(extra="forbid")`, matching the existing convention on all three current models (`app/models.py:48,104,197`).
- `author` and `body` validation should mirror `TaskCreate.validate_title` (`app/models.py:58-78`): a `field_validator` that strips whitespace and enforces the length bound, raising `ValueError` (which FastAPI turns into 422) — this is the established pattern for required string fields in this codebase, not a generic recommendation.
- `id`/`created_at` must be server-assigned only, per the rule already stated in `app/models.py`'s module docstring (lines 4–5: "TaskCreate/TaskUpdate... never accept id/created_at/updated_at -- those are assigned by storage.py").
- **Storage:** `app/storage.py` currently holds one module-level dict, `_tasks: dict[str, TaskResponse] = {}` (line 15). A comment store would need an analogous structure — e.g., `_comments: dict[str, CommentResponse] = {}`, filtered by `task_id` at read time (mirroring how `get_all_tasks` filters in Python rather than at a query layer, `app/storage.py:72-81`). Whatever shape is chosen, `_reset()` (line 153) **must** be extended to clear it too, or `tests/conftest.py`'s autouse `_reset_storage` fixture (lines 8–12) silently stops giving full isolation once comment tests exist.
- **Not clear from the repo:** whether new models belong in `app/models.py` itself (the only schema file today) or a new file — there's no multi-file precedent to follow either way. See Open Question 1.

## 2. API Routes

The repo currently has exactly 5 routes, all flat (`/health`, `/tasks`, `/tasks/{task_id}` — confirmed by reading `app/main.py` in full). **There is no existing nested-resource route to follow**, so this section is a proposal, not an extension of an observed pattern.

| Method | Path | Request body | Response | Error cases |
|---|---|---|---|---|
| `POST` | `/tasks/{task_id}/comments` | `{"author": str, "body": str}` | `201`, `CommentResponse` | `404` if `task_id` doesn't exist (mirroring `_not_found()`, `app/main.py:26-27`); `422` on validation failure or unknown field (`extra="forbid"`) |
| `GET` | `/tasks/{task_id}/comments` | — | `200`, `list[CommentResponse]` | `404` if `task_id` doesn't exist — proposed for consistency with `GET /tasks/{task_id}` (`app/main.py:110-135`), but not confirmed by any existing nested-list behavior since none exists yet (Open Question 5) |
| `DELETE` | `/tasks/{task_id}/comments/{comment_id}` (optional) | — | `204` | `404` if either id doesn't exist, mirroring `DELETE /tasks/{task_id}` (`app/main.py:188-212`) |

No `PATCH` route proposed — consistent with the immutability assumption from the Data Model section.

## 3. Tests

`tests/test_tasks.py` (the only test file today) uses a clear naming convention: `test_<action>_<condition>_returns_<status>[...]`, with `# ---------- ROUTE ----------` section separators, and fixtures (`client`, `created_task`) from `tests/conftest.py`. A `tests/test_comments.py` following the same style would need:

**Happy path:**
- `test_create_comment_valid_returns_201_with_full_body`
- `test_list_comments_for_task_returns_in_order`
- `test_delete_comment_existing_returns_204_no_body` (if deletion is in scope)

**Validation:**
- `test_create_comment_missing_author_returns_422`
- `test_create_comment_blank_author_returns_422` (mirrors `test_create_task_blank_title_returns_422`, line 19)
- `test_create_comment_author_over_100_chars_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_body_over_2000_chars_returns_422`
- `test_create_comment_unknown_field_returns_422` (mirrors `test_create_task_unknown_field_returns_422`, line 29)

**Edge cases:**
- `test_create_comment_on_nonexistent_task_returns_404`
- `test_list_comments_empty_task_returns_200_and_empty_list` (mirrors `test_list_tasks_empty_returns_200_and_empty_list`, line 36)
- `test_list_comments_only_returns_comments_for_that_task` (cross-task isolation)
- `test_create_comment_ignores_client_supplied_id_and_created_at`
- A fixture-reset check confirming `storage._reset()` clears comments too, since `tests/conftest.py`'s autouse fixture depends on it covering all storage state.

Would likely want a `created_comment` fixture in `conftest.py`, mirroring `created_task` (lines 20–24), if many tests need a pre-existing comment.

## 4. Frontend Changes

**Only one frontend file exists:** `frontend/index.html` — confirmed via grep, everything (HTML/CSS/JS) is inline in this single file, no separate JS modules. All changes would land here.

Relevant existing structure (confirmed):
- The create/edit modal (`#modal-overlay`, `<form id="task-form">` at line 459) is currently task-fields-only.
- `openEditModal(task)` (line 778) / `openCreateModal()` (line 761) manage the form.
- `renderCard(task)` (line 649) renders each Kanban card, with every user-controlled field passed through `escapeHtml()` (line 575) before insertion into `innerHTML`.
- `API_BASE` (line 522) and the `fetchTasks()`/`buildTasksUrl()` pattern (lines 567, 596) are what a comments fetch would follow.

**Proposed (not built):** a comments section added inside the edit modal (edit mode only, since a task must exist first) — a list of existing comments plus a small add-comment form. Comment rendering must use the same `escapeHtml()`-before-`innerHTML` pattern already used everywhere else, to avoid introducing an XSS gap the rest of the app doesn't have. No change to `renderCard`/the Kanban card itself is assumed necessary, beyond an optional comment-count badge (flagged as optional, not decided here).

**Flag against `CLAUDE.md` §7:** "Do not make major UI changes (new views, redesigns, new state values, framework adoption) without asking first." Whether a comments panel inside the existing modal counts as "major" is a judgment call for the project owner, not something this plan assumes permission for.

## 5. Migration Notes

- No database exists — `app/storage.py`'s own module docstring (line 2) states "No database, no ORM -- just a module-level dict." There is no schema migration in the traditional sense.
- All data is already lost on every server restart (established, confirmed in `AGENTS.md` §3); adding comments extends this existing behavior, doesn't introduce new data-loss risk.
- No backfill needed for existing in-memory tasks — they'd simply start with zero comments.
- **Required, not optional:** `storage._reset()` (`app/storage.py:153`) must clear the new comment store, or the autouse test-isolation fixture in `tests/conftest.py` silently stops covering it.

## 6. Open Questions

1. **Where do comment models live?** `app/models.py` is currently the single schema file for everything; there's no multi-file precedent to follow if a split is preferred.
2. **Are comments ever editable/deletable, or strictly append-only?** The given field list (no `updated_at`) suggests append-only, but that's an inference, not a stated requirement.
3. **What happens to a task's comments when the task is deleted** (`DELETE /tasks/{task_id}`, `app/main.py:188-212`)? `delete_task` (`app/storage.py:137-150`) currently has no concept of cascading to related records.
4. **Does the comments panel count as a "major UI change"** under `CLAUDE.md` §7, requiring sign-off before implementation begins?
5. **Should `GET /tasks/{task_id}/comments` 404 on a missing task**, matching `GET /tasks/{task_id}`'s behavior, or should list endpoints behave differently under a missing parent? No existing nested-list code in this repo to confirm either way.

---

## Files read

`AGENTS.md`, `app/models.py`, `app/main.py`, `app/storage.py`, `tests/test_tasks.py`, `tests/conftest.py`, `README.md` (partial), `frontend/index.html` (structural grep survey — function/element names and line numbers, not the full file).

## Assumptions to verify

- Comment models belong in `app/models.py` (no multi-file schema precedent exists to confirm this either way).
- Comments are append-only (no edit/delete route) — inferred from the absence of `updated_at` in the given fields, not stated as a requirement.
- Nested route shape (`/tasks/{task_id}/comments`) — proposed by analogy to REST convention; this repo has zero existing nested routes to confirm against.
- `GET .../comments` on a missing task should 404 — proposed for consistency with `GET /tasks/{task_id}`, not confirmed by any comment-specific code.
- Comments render inside the existing edit modal rather than a new view — a guess at the smallest-footprint UI location, not confirmed as acceptable under `CLAUDE.md`'s major-UI-change restriction.
- Comment listing order defaults to insertion order, mirroring `get_all_tasks`'s documented behavior (`app/storage.py:70`) — not established for comments specifically since none exist yet.
