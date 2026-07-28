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

## Data storage

Tasks are stored in `data/tasks.json`, created automatically on first run.
This is a flat file, not a real database — fine for learning, not for production.
