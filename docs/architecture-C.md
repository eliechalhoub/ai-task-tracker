# Task Tracker — Architecture (Strategy C: Targeted Context)

## 1. What the app does
A FastAPI application titled "Task Tracker API" (`app/main.py`) exposing REST endpoints to
create, list, retrieve, update, and delete tasks, with fields for status, priority, assignee,
due date, and tags. A comment in `app/main.py` indicates a separate static frontend exists,
served from a local dev server on a different origin — its purpose beyond that is not visible
from the files I read.

## 2. Data model
One entity, **Task**, per `app/models.py`: `id`, `title` (required, stripped, ≤200 chars),
`description`, `status` (`TaskStatus`: `ToDo`/`InProgress`/`Done`), `priority` (`TaskPriority`:
`Low`/`Medium`/`High`), `assignee` (nullable), `due_date` (nullable date), `tags` (list, ≤5
items, ≤30 chars each, deduplicated), `created_at`/`updated_at`. All three models
(`TaskCreate`/`TaskUpdate`/`TaskResponse`) use `extra="forbid"`.

## 3. Request flow — creating a task
`POST /tasks` (`app/main.py`) receives a `TaskCreate` payload, validated by Pydantic per the
rules in `app/models.py`. The route calls `storage.add_task` (`app/storage.py`), which generates
a UUID `id` and UTC `created_at`/`updated_at`, builds a `TaskResponse`, stores it in the
module-level `_tasks` dict, and returns it. The route returns this as a `201`.

## 4. Key files
Only four files are confirmable from what I read — the task asked for 5-10, but reading only
three files doesn't surface enough of the repo to name more without guessing:
- `app/main.py` — FastAPI routes (read directly).
- `app/models.py` — Pydantic schemas and validation (read directly).
- `app/storage.py` — in-memory persistence (read directly).
- `app/business_rules.py` — imported by both `app/main.py` (`validate_status_transition`) and
  `app/storage.py` (`is_task_overdue`); its existence and import path are visible, its contents
  are not, since it wasn't one of the three files read.

## 5. Conventions
- **Validation:** Pydantic v2, `extra="forbid"` on all three models; `title` and `tags` have
  explicit length/format validators in `app/models.py`.
- **Storage:** a single in-memory dict (`_tasks`), no database — `app/storage.py`'s own
  docstring states "No database, no ORM."
- **Error handling:** `app/main.py` raises `HTTPException` (404) for missing tasks; validation
  failures are handled by Pydantic (referenced in docstrings as producing 422s), not by any
  custom exception handler visible in this file.
- **Frontend/backend interaction:** not visible from the files I read, beyond the fact that
  CORS in `app/main.py` allows exactly two origins (`http://localhost:5500`,
  `http://127.0.0.1:5500`) and a comment states the frontend runs as a static file on a
  separate origin. No frontend file was read, so its actual interaction pattern is unknown.

## 6. Not visible or assumptions
- The exact allowed status transitions — `app/main.py` references
  `business_rules.VALID_TRANSITIONS` but that file wasn't read, so the specific rule is
  **not visible from the files I read**.
- The exact overdue-task definition — `app/storage.py` calls `business_rules.is_task_overdue`
  but doesn't define it; **not visible from the files I read**.
- The frontend's actual file name, structure, and behavior — **not visible from the files I read**.
- Test conventions, Python version, deployment scope, and any project-level governance rules —
  **not visible from the files I read**.
