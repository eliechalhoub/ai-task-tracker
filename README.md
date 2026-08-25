# Task Tracker API

A learning-project REST API + Kanban frontend for tracking tasks, built with
Python/FastAPI and vanilla HTML/CSS/JS.

**Core features:** create / view / update / delete tasks; filter by status,
priority, tag, and overdue state; task **due dates** with an overdue indicator;
**tags/labels**; a drag-and-drop Kanban board with create/edit modal.
**Explicitly out of scope:** authentication, user accounts, multi-tenancy,
real-time sync, mobile app, notifications, a production database, and deployment.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

Run this from the **project root** (the folder containing the `app/` directory),
not from inside `app/` — see Troubleshooting below.

Check it's up:
```bash
curl http://127.0.0.1:8000/health
```
Swagger UI (try every endpoint interactively): http://127.0.0.1:8000/docs

## Run the frontend

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

## Run the tests

```bash
pytest tests/ -v
```

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

## Troubleshooting

If you run `uvicorn app.main:app` from *inside* the `app/` folder instead of the
project root, Python won't find the `app` package:

```
ModuleNotFoundError: No module named 'app'
```

Fix: `cd` back to the project root first.

## Data storage

Tasks are stored in an in-memory Python dict (`app/storage.py`) — **not** a file
or database. All tasks are lost on every server restart. This is a deliberate
simplification for a learning project.

## Documentation

See `docs/midcourse/` for user stories, the design ADR, prompt log, and
verification evidence for the due-dates and tags features.