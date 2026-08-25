# Task Tracker — Architecture (Strategy A: Minimal Context)

## 1. What the app does
A learning-project REST API with a drag-and-drop Kanban frontend for tracking tasks. Users create,
view, update, and delete tasks; filter by status, priority, tag, and overdue state. No auth,
no database, no deployment — explicitly out of scope.

## 2. Data model
One entity, **Task**: `id` (UUID string), `title` (required, ≤200 chars), `description` (string,
no length limit), `status` (`ToDo`/`InProgress`/`Done`), `priority` (`Low`/`Medium`/`High`),
`assignee` (nullable string), `due_date` (nullable date), `tags` (list of strings, ≤5, ≤30 chars
each, deduplicated), `created_at`/`updated_at` (server-assigned UTC timestamps).

## 3. Request flow — creating a task
Client `POST /tasks` with a JSON body → FastAPI route `create_task` (`app/main.py`) →
Pydantic validates the body as `TaskCreate` (`app/models.py`; rejects unknown fields, blank/long
title, bad tags) → route calls `storage.add_task` (`app/storage.py`), which generates `id` and
`created_at`/`updated_at`, builds a `TaskResponse`, and stores it in the in-memory `_tasks` dict →
`TaskResponse` (201) returned to client → frontend re-fetches the task list and re-renders the
board. No status-transition check applies on creation — that only runs on `PATCH`.

## 4. Key files
- `app/main.py` — FastAPI routes; HTTP layer only.
- `app/models.py` — Pydantic v2 schemas and all input validation.
- `app/storage.py` — in-memory `dict`-based persistence; no database.
- `app/business_rules.py` — status-transition and overdue-date logic.
- `frontend/index.html` — the entire frontend: HTML/CSS/JS, one file, no build step.
- `tests/test_tasks.py` — endpoint tests covering CRUD, filters, and validation rules.
- `tests/conftest.py` — test fixtures; resets storage before/after every test.
- `requirements.txt` — pinned dependency versions (FastAPI, Pydantic, pytest, etc.).
- `AGENTS.md` — AI-agent guidance and current course-module guardrails.

## 5. Conventions
- **Validation:** Pydantic v2, `extra="forbid"` on every model; server-only fields (`id`,
  `created_at`, `updated_at`) never accepted from the client.
- **Storage:** a single module-level dict, no ORM, no persistence across restarts (deliberate).
- **Error handling:** `HTTPException` for 404s, Pydantic's automatic 422 for validation
  failures; no custom exception handlers, no debug mode, no stack traces leaked to clients.
- **Frontend/backend interaction:** frontend calls the API over `fetch` at a hardcoded
  `http://localhost:8000`; backend's CORS allows only two specific localhost origins
  (5500); all server data is HTML-escaped client-side before rendering.

## 6. Not visible or assumptions
- Python version isn't pinned anywhere in the repo; only inferable from CI (3.11).
- `.env`/`.env.example` exist but no code currently reads any environment variable.
- `app/storage.py`'s `update_task` has a dead fallback branch referencing an undefined
  "local shim" — behavior unclear, not exercised in current code.
- No comments-on-tasks feature exists yet (a design plan exists in `docs/decisions/`, unimplemented).
