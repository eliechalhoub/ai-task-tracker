# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A learning-project REST API + Kanban frontend for tracking tasks: Python/FastAPI backend,
vanilla HTML/CSS/JS frontend, no build step. Explicitly out of scope: authentication, user
accounts, multi-tenancy, real-time sync, mobile app, notifications, a production database,
and deployment.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 1. Tech stack

- Python — version not pinned anywhere in this repo (no `.python-version`, `pyproject.toml`,
  or README statement found) — **[VERIFY]** the Python version with the student/course
  materials before assuming one.
- FastAPI `0.115.0` (per `requirements.txt`)
- Pydantic v2 — `pydantic==2.9.2` (per `requirements.txt`)
- Uvicorn `0.30.6` (`uvicorn[standard]`, per `requirements.txt`)
- pytest `8.3.3` (per `requirements.txt`)
- httpx `0.27.2` (per `requirements.txt`)
- python-dotenv `1.0.1` (per `requirements.txt`)
- Frontend: vanilla HTML/CSS/JavaScript, no framework, no build step (`frontend/index.html`)

## 2. Run command

```bash
uvicorn app.main:app --reload --port 8000
```
Must be run from the project root (the folder containing `app/`) — running from inside
`app/` causes `ModuleNotFoundError: No module named 'app'` (per README Troubleshooting).

Run the frontend (must be served, not opened as a `file://` URL, so the browser treats it
as its own origin for CORS):
```bash
cd frontend
python3 -m http.server 5500
```
Then open http://localhost:5500/index.html. If served from a different port, add it to
`allow_origins` in `app/main.py`.

## 3. Test command

```bash
pytest -v
```
Run a single test: `pytest tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 -v`

Swagger UI for manual endpoint testing: http://127.0.0.1:8000/docs (default FastAPI
auto-docs — not disabled in `app/main.py`'s `FastAPI(...)` call, which passes no
`docs_url`/`openapi_url` override)

## 4. Architecture summary

Layering is strict and one-directional: `main.py` (HTTP layer) → `storage.py` (persistence)
→ `business_rules.py` (domain rules) → `models.py` (schemas). Keep new logic in the layer it
belongs to rather than folding it into route handlers.

**Backend:**
- **`app/models.py`** — Pydantic v2 schemas. `TaskCreate`/`TaskUpdate` are client-facing input
  models and never accept `id`/`created_at`/`updated_at`; those are assigned only in
  `storage.py`. All three models use `extra="forbid"`. `TaskUpdate` has a `model_validator`
  that rejects explicit `null` for non-nullable fields (`title`, `description`, `status`,
  `priority`, `tags`) — the client must omit a field to leave it unchanged, since PATCH uses
  `exclude_unset=True` semantics. `assignee` and `due_date` are the two fields where explicit
  `null` is meaningful (unassign / clear due date) and is allowed.
- **`app/business_rules.py`** — **this is where task rules live**: `validate_status_transition`
  and `is_task_overdue` (see Business rules section below).
- **`app/storage.py`** — in-memory storage only (`dict[str, TaskResponse]` at module scope).
  **All tasks are lost on every server restart** — this is a deliberate simplification, not a
  bug. `_reset()` exists purely for test isolation (see `tests/conftest.py`'s autouse fixture).
- **`app/main.py`** — FastAPI routes. Status-transition validation happens here (fetches the
  existing task, then calls `validate_status_transition` before delegating to
  `storage.update_task`) rather than inside `storage.py`, since it needs the existing record
  to compare against.

**Frontend:**
- **`frontend/index.html`** — a single self-contained file (HTML/CSS/JS, no framework, no
  build step) implementing a drag-and-drop Kanban board against the API at
  `http://localhost:8000` (`API_BASE` constant, `index.html:522`). It has its own mirrored
  `isOverdue()` function (`index.html:561`) for the overdue pill on cards, duplicating
  `business_rules.is_task_overdue` — this duplication is a known, deliberate trade-off (see
  `docs/midcourse/mini-adr.md`), not an oversight. If the overdue rule changes, update both
  places.

**Tests:**
- **`tests/test_tasks.py`** — endpoint tests via `TestClient`, covering CRUD, filters, PATCH
  null-rejection rules, status transitions, due dates, and tags.
- **`tests/conftest.py`** — `client` fixture and an autouse `_reset_storage` fixture that
  calls `storage._reset()` before and after every test.
- **`tests/verify_a.py`** — standalone script (not a pytest file) that exercises `TaskCreate`/
  `TaskUpdate` validation directly and prints PASS/FAIL lines.

### PATCH semantics

`TaskUpdate` uses `exclude_unset=True` when applied in `storage.update_task`, so omitted
fields are left untouched. Explicit `null` is rejected at the model level for
`title`/`description`/`status`/`priority`/`tags`, and accepted for `assignee`/`due_date`.
Don't "fix" this by making all fields nullable — it's intentional API contract, and
`tests/test_tasks.py` asserts on it directly.

## 5. Business rules

Verified directly against `app/models.py` and `app/business_rules.py`:

- **Task status values** (`TaskStatus` enum, `app/models.py`): `ToDo`, `InProgress`, `Done`.
- **Status transitions** (`VALID_TRANSITIONS`, `app/business_rules.py`): only
  `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress` are allowed. Any other
  transition — including same-status-to-same-status — is rejected by
  `validate_status_transition()` with `422 Unprocessable Entity`. Extend
  `VALID_TRANSITIONS` rather than special-casing transitions elsewhere.
- **Overdue rule** (`is_task_overdue()`, `app/business_rules.py`): a task is overdue only if
  `due_date` is set, the task's status is not `Done`, and `due_date` is strictly before
  "today" (real `date.today()`, or an injectable `today` param used in tests).

## 6. UI states and CORS notes

- **UI states** (`frontend/index.html:528`): the frontend tracks an explicit `uiState`
  variable with four values — `loading`, `ready`, `empty`, `error` — toggled around the
  `fetch` call that loads the task list, driving the `#board-loading` / `#board-error` /
  board visibility.
- **CORS** (`app/main.py`): `CORSMiddleware` allows only `http://localhost:5500` and
  `http://127.0.0.1:5500` as origins, methods `GET, POST, PATCH, DELETE`, and header
  `Content-Type`. If you serve the frontend from a different host/port, add it to
  `allow_origins` in `app/main.py` — but that is an application-code change (see Do-not rules).

## 7. Do-not rules

- Do not add authentication, user accounts, or session/token handling.
- Do not add a database, ORM, or persistent storage layer — storage is intentionally an
  in-memory dict for this learning project.
- Do not add deployment steps, Dockerfiles, or CI/CD config.
- Do not make major UI changes (new views, redesigns, new state values, framework adoption)
  without asking first.
- For anything in this list: if it seems necessary, ask before implementing rather than
  proceeding.

## Documentation

`docs/midcourse/` contains user stories, a mini-ADR (design decisions and rejected
alternatives for the due-dates and tags features), a prompt log, and verification evidence.
Check `docs/midcourse/mini-adr.md` before changing overdue logic, tag representation, or
filter response shape — those decisions and their trade-offs are recorded there.
