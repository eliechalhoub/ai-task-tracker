# AGENTS.md

Guidance for AI coding agents (Codex, Claude Code, etc.) working in this repository.

**Current phase note (as of 2026-08-26):** the user has explicitly declared a new phase —
the end-of-course Final Project, worked on branch `final-project`. Section 4 below has been
updated accordingly. Per the standing rule, agents must not revise Section 4 themselves based on
inferred context; update it only when the user explicitly states the phase has changed again and
specifies the new constraints.

## 1. Project summary

A learning-project REST API + Kanban frontend for tracking tasks. Backend is
Python/FastAPI with in-memory storage (no database); frontend is a single static
HTML/CSS/JS file with no build step and no framework. Explicitly out of scope for
the whole project: authentication, user accounts, multi-tenancy, real-time sync,
mobile app, notifications, a production database, and deployment.

Layering is strict and one-directional:
`app/main.py` (HTTP routes) → `app/storage.py` (persistence) →
`app/business_rules.py` (domain rules) → `app/models.py` (Pydantic schemas).
(Source: `README.md` §1, confirmed against `app/main.py`, `app/storage.py`.)

## 2. Tech stack and commands

**Stack** (source: `requirements.txt`):
- fastapi==0.115.0
- uvicorn[standard]==0.30.6
- pydantic==2.9.2
- python-dotenv==1.0.1
- pytest==8.3.3
- httpx==0.27.2
- Frontend: vanilla HTML/CSS/JS, no framework, no build step (`frontend/index.html`)
- Python version: **not pinned** in the repo itself (no `.python-version` or
  `pyproject.toml` found). CI (`.github/workflows/ci.yml`) uses Python 3.11 via
  `actions/setup-python@v5` — treat 3.11 as the CI-verified version, not confirmed
  as a hard project requirement elsewhere.

**Setup:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
`[VERIFY]` — `.env.example` defines `PORT` and `APP_ENV`, but no code under `app/`
reads environment variables (no `os.environ`/`os.getenv`/`load_dotenv` calls found
in `app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`). The
`.env` step currently has no effect on app behavior.

**Run the backend** (from the project root — running from inside `app/` causes
`ModuleNotFoundError: No module named 'app'`, per `README.md` Troubleshooting):
```bash
uvicorn app.main:app --reload --port 8000
```

**Run the frontend** (must be served, not opened as `file://`, so CORS treats it
as its own origin):
```bash
cd frontend
python3 -m http.server 5500
```
Then open http://localhost:5500/index.html. Confirmed in `app/main.py`: CORS
(`CORSMiddleware`) allows only `http://localhost:5500` and `http://127.0.0.1:5500`,
methods `GET, POST, PATCH, DELETE`, header `Content-Type`.

**Run tests:**
```bash
pytest -v
```
Single test:
```bash
pytest tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 -v
```
`tests/verify_a.py` is a standalone script, not a pytest file — confirmed
directly: it imports `ValidationError` and runs `expect_fail`/`expect_ok`
assertions with `print(...)` PASS/FAIL output at module scope, with no
`test_*` functions or pytest fixtures. Run as `python -m tests.verify_a`
from the repo root.

**CI** (confirmed in `.github/workflows/ci.yml`): on every `push` and
`pull_request`, on `ubuntu-latest` — checkout, set up Python 3.11, `pip install -r
requirements.txt`, `pytest -v`. No lint step, no Docker build/test step.

## 3. Business rules visible in code

**Task status** (`TaskStatus` enum, `app/models.py`): `ToDo`, `InProgress`, `Done`.

**Task priority** (`TaskPriority` enum, `app/models.py`): `Low`, `Medium`, `High`.

**Status transitions** (`VALID_TRANSITIONS`, `app/business_rules.py`): only
`ToDo → InProgress`, `InProgress → Done`, `Done → InProgress` are allowed via
`PATCH /tasks/{id}`. Any other transition, including same→same, is rejected with
`422` by `validate_status_transition`. Confirmed in `app/main.py`: this check runs
only on `update_task` (PATCH) — `POST /tasks` (`create_task`) never calls it, so a
task can be created directly with any status, e.g. already `Done`.

**Overdue rule** (`is_task_overdue`, `app/business_rules.py`): a task is overdue
only if `due_date` is set, status is not `Done`, and `due_date` is strictly before
`today` (real `date.today()` or an injectable `today` param for tests). Confirmed
duplicated client-side in `frontend/index.html` (`isOverdue()` at line 561) —
README and `CLAUDE.md` both note this duplication is deliberate, not an oversight.

**Validation rules** (`app/models.py`):
- `title`: required, stripped, non-blank, max 200 characters (`TaskCreate` and
  `TaskUpdate` share the same validator).
- `tags`: max 5 tags, each max 30 characters, blank tags rejected, de-duplicated
  by exact case-sensitive match (`_clean_tags`).
- `TaskCreate`/`TaskUpdate`/`TaskResponse` all use `extra="forbid"` — unknown
  fields are rejected.
- `TaskCreate`/`TaskUpdate` never accept `id`/`created_at`/`updated_at`; those are
  assigned only in `app/storage.py`.
- `TaskUpdate` PATCH semantics use `exclude_unset=True`: omitted fields are left
  unchanged. A `model_validator` rejects explicit `null` for `title`,
  `description`, `status`, `priority`, `tags`; `assignee` and `due_date` accept
  explicit `null` (to unassign / clear a due date).

**Filtering** (`app/storage.get_all_tasks`, confirmed): `GET /tasks` supports
`status`, `priority`, `tag` (exact, case-sensitive), and `overdue`, combined with
AND logic when more than one is given.

**Storage**: in-memory Python dict at module scope (`app/storage.py`, `_tasks`).
All tasks are lost on every server restart — deliberate, not a bug. `_reset()`
exists purely for test isolation (see `tests/conftest.py`'s autouse fixture).

`[VERIFY]` — `app/storage.py` `update_task` has a dead fallback branch
(`hasattr(existing, "model_copy")`) referencing an undefined "local shim" in its
docstring; since `TaskResponse` is always a Pydantic v2 `BaseModel`, this branch
appears unreachable. Not fixing it — Module 5 is analysis-only.

## 4. Final Project guardrails (current phase — see note at top of file)

Hard constraints — do not deviate from these without explicit user approval:

- **All final-project work happens on the `final-project` branch.** Do not commit this work
  directly to `main`.
- **No new product features.** Do not implement comments, authentication, a production
  database, notifications, or unrelated UI changes — this project hardens/documents/governs
  the existing app, it does not extend it.
- **`app/` and `frontend/` may only be changed for a small, specific bug fix, security fix, or
  documentation-supported correction** — never a refactor or feature addition. Any such change
  must be explained in `docs/final-ai-review.md`.
- **No real secrets or personal data** may be pasted into an AI tool or committed to the repo —
  no credentials, `.env` values, tokens, production logs, or real personal/customer data.
- **Ownership rule:** if a changed line, command, config choice, or AI suggestion can't be
  explained, it does not go into the final submission.
- **State intent before acting**: what the task is understood to be, which files will be
  inspected, and whether edit permission is needed — before making changes.
- **Docs-first / read-first.** Before editing any file, read `README.md`, this file, and the
  relevant `docs/` note for that area first (e.g. `docs/decisions/module4-docker-decision.md`
  before touching `Dockerfile`; `docs/security-review.md` before touching validation logic).
  The point isn't to block edits — this phase explicitly requires them — it's to make sure a
  change is consistent with what's already been decided and documented, instead of re-deciding
  it from scratch.

Retired for this phase (was a Module 5 constraint, not a permanent rule): the "read-only
by default" / "`docs/` is the default edit surface" restriction — replaced above with a
read-first-not-edit-blocked guardrail. This phase explicitly requires running the app, running
tests, building Docker, and — within the limits above — touching `app/`/`frontend/` when
justified.

## 5. Security and governance reminders

- Never paste, log, or otherwise expose secrets (API keys, tokens, `.env`
  contents) in output, commits, or documentation.
- Do not run destructive commands (`rm -rf`, force-push, `git reset --hard`,
  dropping data) without explicit user confirmation.
- Every factual claim about the repo must cite the actual file(s) inspected.
- Do not invent findings, business rules, or commands that aren't verifiable in
  the current codebase — mark anything uncertain or unverified as `[VERIFY]` /
  "not confirmed" instead of guessing.
- If a referenced file isn't visible or accessible, say so explicitly rather than
  assuming its contents.
