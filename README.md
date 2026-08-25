# Task Tracker API

A learning-project REST API + Kanban frontend for tracking tasks, built with
Python/FastAPI and vanilla HTML/CSS/JS.

**Core features:** create / view / update / delete tasks; filter by status,
priority, tag, and overdue state; task **due dates** with an overdue indicator;
**tags/labels**; a drag-and-drop Kanban board with create/edit modal.
**Explicitly out of scope:** authentication, user accounts, multi-tenancy,
real-time sync, mobile app, notifications, a production database, and deployment.

## Final Project
Branch reviewed: `final-project`

### What this submission demonstrates
- Existing Task Tracker app still runs inside the intended course scope (verified: `/health`
  returns 200, all 30 tests pass, frontend serves the real Kanban board markup).
- CI runs the pytest suite on push and pull request (`.github/workflows/ci.yml`; latest run on
  `main` succeeded — see `docs/release-evidence.md`).
- Docker image builds and runs with `/health` returning 200, confirmed against the *actual*
  built image, not assumed from the Dockerfile alone.
- AI review, security, and ownership evidence is in `docs/`.

### How to run locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### How to run tests
```bash
pytest -v
```

### How to run with Docker
```bash
docker build -t task-tracker:dev .
docker run -d --name tt-dev -p 8000:8000 task-tracker:dev
sleep 2
curl http://localhost:8000/health
docker stop tt-dev && docker rm tt-dev
```

### Evidence files
- [docs/release-evidence.md](docs/release-evidence.md)
- [docs/final-ai-review.md](docs/final-ai-review.md)
- [docs/ai-playbook.md](docs/ai-playbook.md)

### AI assistance summary
AI helped draft or review: CI verification, Docker verification, documentation accuracy checks,
security review, and this final project's evidence documents.
I verified the work by: running the actual test suite (30/30 passed), curling a live `/health`
endpoint (both local and containerized), building and running the real Docker image, querying
GitHub's Actions API directly for the actual latest CI run status, and re-running a failed
Docker health check rather than accepting the first (failing) result.
One AI suggestion I rejected or corrected: see `docs/final-ai-review.md` — a proposed `app/`
diff (bounding the `description` field's length) was left unapplied after review, since it was
never scoped to a concrete required value or explicitly approved.

## 1. Project overview

Backend: Python/FastAPI, in-memory storage only (see [Project conventions and
current limitations](#9-project-conventions-and-current-limitations)).
Frontend: a single static HTML/CSS/JS file with no build step and no
framework. Layering is strict and one-directional:
`app/main.py` (HTTP layer) → `app/storage.py` (persistence) →
`app/business_rules.py` (domain rules) → `app/models.py` (schemas).

This is a learning project. It is **not** deployed anywhere, has **no
authentication**, and has **no persistent database** — see section 9 for the
full list of what's intentionally out of scope.

## 2. Prerequisites

- Python 3.11 in CI (`.github/workflows/ci.yml`, `actions/setup-python@v5`) — this repo has
  no `.python-version` or `pyproject.toml` pinning a version for local development.
  Verified during the final-project baseline: the full test suite (30/30) also passes locally
  on Python 3.12.3, so 3.11 is confirmed for CI but not a hard local requirement.
- `pip` (bundled with Python)
- Docker — only needed for [section 6](#6-run-with-docker); no version is
  pinned in the `Dockerfile`. `[VERIFY]` minimum supported Docker version.

## 3. Local setup

Run from the project root:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`[VERIFY]`: `python-dotenv` is a dependency and `.env` is created here, but no
code under `app/` currently reads environment variables (no
`os.environ`/`os.getenv`/`load_dotenv` calls found) — the `.env` step doesn't
currently affect app behavior.

## 4. Run the app locally

```bash
uvicorn app.main:app --reload --port 8000
```

Run this from the **project root** (the folder containing the `app/` directory),
not from inside `app/` — see [Troubleshooting](#troubleshooting) below.

Check it's up:
```bash
curl http://127.0.0.1:8000/health
```
Swagger UI (try every endpoint interactively): http://127.0.0.1:8000/docs

### Run the frontend

`frontend/index.html` is a static Kanban board (vanilla HTML/CSS/JS, no build
step) that talks to the API at `http://localhost:8000`. Serve it from a local
dev server so the browser treats it as its own origin:

```bash
cd frontend
python3 -m http.server 5500
```
(or VS Code's Live Server extension, which also defaults to port 5500)

Then open http://localhost:5500/index.html. The backend's CORS config in
`app/main.py` already allows `http://localhost:5500` and `http://127.0.0.1:5500`;
if you serve the frontend from a different port, add it to `allow_origins` there.

## 5. Run tests

From the project root, with the virtualenv activated:

```bash
pytest -v
```

Run a single test:
```bash
pytest tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 -v
```

`tests/verify_a.py` is a standalone script, not a pytest file — run it as a
module from the repo root (running it as a plain script fails with
`ModuleNotFoundError: No module named 'app'`, since `tests/` isn't on
`sys.path`):
```bash
python -m tests.verify_a
```

## 6. Run with Docker

A multi-stage `Dockerfile` builds the **backend only** (the frontend is not
included in the image — it's served separately, see section 4). This is for
local container testing, not deployment: there's no orchestration, no
published image, and no production configuration here.

```bash
docker build -t task-tracker:dev .
docker run -d --name tt-dev -p 8000:8000 task-tracker:dev
sleep 2   # give uvicorn a moment to finish starting before the health check
curl http://localhost:8000/health
docker logs tt-dev
```

Verified during the final-project baseline: curling `/health` immediately after `docker run -d`
can race the container's startup and return no response at all — the `sleep 2` above isn't
theoretical, it's what turned a failed check into `{"status":"ok",...}` on the first real run.

Stop and remove the container when done:
```bash
docker stop tt-dev && docker rm tt-dev
```

Notes:
- The final image runs as a non-root user (`app`), not root.
- Base image is `python:3.11-slim` in both build stages — not `python:latest`.
- `.dockerignore` excludes `.env`, `.git`, virtualenvs, and Python caches from
  the build context, so none of those are baked into the image.
- `[VERIFY]` — `CLAUDE.md`'s "Do-not rules" (section 7) say not to add
  Dockerfiles or deployment steps without asking first; a `Dockerfile` and
  `.dockerignore` already exist in this repo (untracked as of this writing).
  Confirm with course staff / update `CLAUDE.md` if this is an intentional,
  approved addition for Module 4, since as written the two documents disagree.

## 7. CI workflow summary

`.github/workflows/ci.yml` runs on every `push` and `pull_request`, on
`ubuntu-latest`:

1. Check out the repo (`actions/checkout@v4`).
2. Set up Python 3.11 (`actions/setup-python@v5`).
3. `pip install -r requirements.txt`.
4. `pytest -v`.

That's the entire workflow — it only runs tests. It does not build the Docker
image, run linting, or deploy anything. `[VERIFY]` whether Module 4 is
expected to add a Docker build/test step to this workflow, since the CI file
currently doesn't reference the `Dockerfile` at all.

## 8. Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI routes (HTTP layer)
│   ├── storage.py         # in-memory persistence
│   ├── business_rules.py  # status-transition and overdue rules
│   └── models.py          # Pydantic v2 schemas
├── frontend/
│   └── index.html         # static Kanban board, no build step
├── tests/
│   ├── conftest.py        # client fixture, per-test storage reset
│   ├── test_tasks.py      # endpoint tests
│   └── verify_a.py        # standalone validation script (not pytest)
├── docs/
│   └── midcourse/         # user stories, mini-ADR, prompt log, verification
├── .github/
│   └── workflows/
│       └── ci.yml         # pytest on push/PR
├── Dockerfile              # multi-stage backend build (see section 6)
├── .dockerignore
├── requirements.txt
├── .env.example
└── CLAUDE.md               # guidance for AI coding assistants on this repo
```

## 9. Project conventions and current limitations

**Conventions:**
- Strict, one-directional layering: `main.py` → `storage.py` →
  `business_rules.py` → `models.py`. New logic belongs in the layer it
  concerns rather than in route handlers.
- `TaskCreate`/`TaskUpdate` never accept `id`/`created_at`/`updated_at` —
  those are assigned only in `storage.py`.
- PATCH uses `exclude_unset=True` semantics: omit a field to leave it
  unchanged. `title`, `description`, `status`, `priority`, and `tags` reject
  explicit `null`; `assignee` and `due_date` accept explicit `null` (to
  unassign / clear a due date).
- Status transitions on `PATCH /tasks/{id}` are restricted to
  `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress` (see
  `app/business_rules.py`). This check only applies to updates —
  `POST /tasks` can set `status` to any value directly (e.g. create a task
  already `Done`), since task creation never calls
  `validate_status_transition`.
- The frontend has its own `isOverdue()` function that mirrors
  `business_rules.is_task_overdue` — a deliberate duplication (see the
  mini-ADR linked below), not an oversight.

**Current limitations (intentionally out of scope):**
- No authentication, user accounts, or session/token handling.
- No database or ORM — storage is an in-memory Python dict
  (`app/storage.py`). **All tasks are lost on every server restart.**
- No multi-tenancy, real-time sync, mobile app, or notifications.
- Not deployed anywhere; the Docker image in section 6 is for local testing
  only, not a production-ready container.
- No CI step builds or tests the Docker image (see section 7).

## Troubleshooting

If you run `uvicorn app.main:app` from *inside* the `app/` folder instead of the
project root, Python won't find the `app` package:

```
ModuleNotFoundError: No module named 'app'
```

Fix: `cd` back to the project root first.

## API reference

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | liveness check |
| POST | `/tasks` | create a task |
| GET | `/tasks` | list tasks; optional `?status=`, `?priority=`, `?tag=`, `?overdue=true` |
| GET | `/tasks/{id}` | get one task |
| PATCH | `/tasks/{id}` | partial update; omit a field to leave it unchanged |
| DELETE | `/tasks/{id}` | delete a task |

### Task fields
`id`, `title` (required), `description`, `status` (`ToDo`/`InProgress`/`Done`),
`priority` (`Low`/`Medium`/`High`), `assignee` (nullable), `due_date` (nullable,
`YYYY-MM-DD`), `tags` (list of strings, max 5, max 30 chars each), `created_at`,
`updated_at`.

**Note on PATCH and null values:** `title`, `description`, `status`, `priority`,
and `tags` cannot be explicitly set to `null` — omit the field entirely if you
don't want to change it. `assignee` and `due_date` *can* be explicitly set to
`null`, since that's how you unassign a task or clear its due date.

## 10. Documentation and decisions

See [`docs/midcourse/`](docs/midcourse/) for user stories, prompt log, and
verification evidence. In particular,
[`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md) records the design
decisions and rejected alternatives for the due-dates and tags features —
check it before changing overdue logic, tag representation, or filter
response shape.
[`docs/decisions/module4-docker-decision.md`](docs/decisions/module4-docker-decision.md)
records the Module 4 Dockerfile design decision, alternatives, and open
questions.
