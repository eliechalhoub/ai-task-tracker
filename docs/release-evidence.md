# Release Evidence

## Baseline
- Branch: `final-project`
- Date: 2026-08-26
- Local app run command: `uvicorn app.main:app --port 8000` (from repo root, `venv` activated)
- `/health` result: `200` — `{"status":"ok","timestamp":"2026-08-25T22:35:10.866567+00:00"}`
- Frontend check: served via `python3 -m http.server 5500` from `frontend/`, opened at
  `http://localhost:5500/index.html`. No headless-browser tool (`chromium-cli`, Playwright) was
  available in this environment, so this was verified via `curl | grep` on the served HTML
  rather than a rendered screenshot — confirmed the response contains the three board columns
  (`To Do`/`In Progress`/`Done`), the `New Task` control, the `modal`, and `task-form`, i.e. the
  Kanban board and create/edit UI are genuinely present in what's served, not just assumed from
  the file existing.
- Test command: `pytest -v`
- Test result: **30 passed** in 0.21s, 0 failed, no pre-existing or introduced failures.

## CI evidence
- Workflow file: `.github/workflows/ci.yml`
- Latest run link: https://github.com/eliechalhoub/ai-task-tracker/actions/runs/32904063537
  (verified via a direct read-only query to the GitHub Actions API, not guessed — `conclusion:
  success`, `head_sha: 45795d64afb011960e4713fd4752a677196fec23`, matching the "Finalize module
  5" commit on `main`)
- Test command used by CI: `pytest -v` (same command as the local baseline above)
- Shortcut check: confirmed clean by direct read of `ci.yml` — no `continue-on-error`, no
  `|| true`, pytest is not skipped, Python version is explicitly pinned (`3.11` via
  `actions/setup-python@v5`), dependency installation step is present
  (`pip install -r requirements.txt`).

## Docker evidence
- Build command: `docker build -t task-tracker:dev .` — succeeded, 13/13 steps, image tagged
  `task-tracker:dev`.
- Run command: `docker run -d --name tt-dev -p 8000:8000 task-tracker:dev`
- `/health` check: first attempt returned `HTTP_STATUS:000` (curl fired immediately after
  `docker run -d`, before uvicorn finished starting — a real timing race, not a code bug).
  Re-run with a `sleep 2` before the curl returned `200 {"status":"ok",...}`, and
  `docker logs tt-dev` confirmed clean startup: `Application startup complete` /
  `Uvicorn running on http://0.0.0.0:8000` / `GET /health HTTP/1.1" 200 OK`. README's Docker
  section was updated with this `sleep 2` step so the same race doesn't surprise the next person.
- Non-root check: `docker exec tt-dev whoami` → `app` (not `root`) — confirmed directly against
  the running container, not just read from the `Dockerfile`.
- No-baked-secrets check: `.dockerignore` excludes `.env`, `.git`, `venv/`, `.venv/`, and all
  Python caches from the build context (confirmed by reading the file directly). No real `.env`
  file exists in this repo at all (confirmed earlier this course), so there was nothing to
  accidentally bake in regardless.

## Documentation claim-vs-reality log
| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README §2: "Python 3.11" prerequisite | Ran the full local test suite; `pytest` header reported `Python 3.12.3` | Mismatch — CI genuinely pins 3.11, but local dev was never actually confirmed to need it | Updated README §2 to state 3.11 is CI-verified and 3.12.3 is confirmed working locally, instead of leaving it as an open `[VERIFY]` |
| README §4: `GET /health` returns `{"status":"ok","timestamp":...}` | Live `curl http://127.0.0.1:8000/health` against the locally running app | Confirmed accurate, exact shape matched | None |
| README §6: Docker run/curl sequence works as written | Ran the exact documented commands against the real built image | First run returned no response (`HTTP_STATUS:000`) due to a startup race the README didn't warn about | Added a `sleep 2` step and an explanatory note to README §6 |
| README §6: "final image runs as a non-root user (`app`)" | `docker exec tt-dev whoami` against the running container | Confirmed accurate | None |
| README §7 / `.github/workflows/ci.yml` summary: "runs pytest only, no Docker build/lint step" | Direct read of `ci.yml`; cross-checked against the GitHub Actions API run history | Confirmed accurate | None |
