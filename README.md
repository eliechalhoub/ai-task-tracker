# Task Tracker API (Module 1)

A minimal learning-project REST API for tracking tasks, built with Python and FastAPI.

**In scope:** create / view / update / delete tasks; filter by status and priority.
**Explicitly out of scope:** authentication, user accounts, multi-tenancy, real-time
updates, mobile app, notifications, a production database, and deployment.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Run this from the **project root** (the folder containing the `app/` directory),
not from inside `app/` — see the Troubleshooting note below.

## Test the health check

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status": "ok", "timestamp": "2026-07-28T12:00:00.000000+00:00"}
```

## Swagger UI

Open http://127.0.0.1:8000/docs in your browser to try every endpoint interactively.

## Troubleshooting

If you run `uvicorn app.main:app` from *inside* the `app/` folder instead of the
project root, Python won't find the `app` package and you'll see:

```
ModuleNotFoundError: No module named 'app'
```

Fix: `cd` back to the project root first.

## Frontend (Module 3)

`frontend/index.html` is a static Kanban board (vanilla HTML/CSS/JS, no build step)
that talks to this API at `http://localhost:8000`. Serve it from a local dev server
so the browser treats it as its own origin — e.g. VS Code's Live Server extension
on port 5500. The backend's CORS config in `app/main.py` already allows
`http://localhost:5500` and `http://127.0.0.1:5500`; if you serve the frontend from
a different port, add it to `allow_origins` in `app/main.py`.

## Running tests

```bash
pytest tests/ -v
```

## Mid-course project (due dates + tags)

Two features were added on top of Modules 1-3: optional task **due dates** with an
overdue filter, and **tags/labels** with a tag filter. Both are usable from the
Kanban board (modal fields, card display, and the filter bar above the board) and
from the API directly (`GET /tasks?overdue=true`, `GET /tasks?tag=backend`).
See `docs/midcourse/` for the user stories, design decisions, prompt log, and
verification evidence for this work.

## Data storage

Tasks are stored in an in-memory Python dict (`app/storage.py`) — **not** a file or
database. This means all tasks are lost every time the server restarts. This is a
deliberate Module 2 simplification for a learning project; earlier documentation
in this README incorrectly described a JSON-file store, which was never actually
wired up after Module 2 replaced it with the in-memory version — corrected here.
