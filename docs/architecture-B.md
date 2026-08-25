# Task Tracker — Architecture (Strategy B: Structured Context)

## 1. What the app does
A learning-project REST API with a drag-and-drop Kanban frontend for tracking tasks. Users create,
view, update, and delete tasks; filter by status, priority, tag, and overdue state. Explicitly
out of scope: authentication, user accounts, multi-tenancy, real-time sync, mobile app,
notifications, a production database, and deployment (per `AGENTS.md` §1).

## 2. Data model
One entity, **Task**, per `AGENTS.md` §3: `id`, `title` (required, ≤200 chars), `description`,
`status` (`ToDo`/`InProgress`/`Done`), `priority` (`Low`/`Medium`/`High`), `assignee` (nullable),
`due_date` (nullable), `tags` (≤5, ≤30 chars each, deduplicated), `created_at`/`updated_at`
(server-assigned). Source: `app/models.py` per the file summary.

## 3. Request flow — creating a task
Per the `app/main.py` and `app/storage.py` summaries: client `POST /tasks` → FastAPI route →
Pydantic validates as `TaskCreate` → `storage.add_task` assigns `id`/timestamps and stores the
record in the in-memory `_tasks` dict → `TaskResponse` (201) returned. `AGENTS.md` §3 explicitly
notes creation never calls `validate_status_transition` — a task can be created directly in any
status, unlike `PATCH`.

## 4. Key files
- `app/main.py` — HTTP routes only.
- `app/models.py` — validation and schemas.
- `app/storage.py` — in-memory persistence.
- `app/business_rules.py` — status-transition and overdue rules.
- `frontend/index.html` — entire frontend, one file.
- `tests/test_tasks.py` — endpoint test coverage.
- `tests/conftest.py` — test fixtures and storage reset.
- `requirements.txt` — pinned dependencies.
- `AGENTS.md` — AI-agent guidance and current guardrails.

## 5. Conventions
- **Validation:** Pydantic v2, `extra="forbid"` on all models (`AGENTS.md` §3).
- **Storage:** single in-memory dict, no database, no persistence across restarts — deliberate
  (`AGENTS.md` §3).
- **Error handling:** per the file summaries, `app/main.py` raises `HTTPException` for 404s;
  Pydantic validation failures produce 422s automatically.
- **Frontend/backend interaction:** CORS restricted to two specific localhost origins
  (`AGENTS.md` §6); frontend calls the API directly, per the `frontend/index.html` summary.

## 6. Not visible or assumptions
- Python version not pinned in-repo; only inferable from CI (`AGENTS.md` §2, `[VERIFY]`).
- `.env.example` exists but no app code reads any environment variable (`AGENTS.md` §2, `[VERIFY]`).
- `app/storage.py`'s `update_task` has a dead fallback branch referencing an undefined
  "local shim" (`AGENTS.md` §3, `[VERIFY]`).
