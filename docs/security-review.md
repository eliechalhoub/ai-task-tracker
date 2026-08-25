# Security Review — Task Tracker (Module 5)

**Type:** Read-only security-minded audit, not a penetration test or a live vulnerability scan.
**Scope:** Static review of repo contents as of 2026-08-25. No app run, no requests sent, no files edited during the audit itself.
**Reviewer note:** This project is an explicitly non-production learning app — see `README.md` §9 and `CLAUDE.md` §1/§7 for the standing scope exclusions (no auth, no database, no deployment). Findings below are evaluated against that stated scope, not against production-API expectations.

## Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|---|---|---|---|---|---|---|
| F1 | Medium | `app/models.py:51,107,201` | `description` field has no maximum length | `title` has a `field_validator` rejecting >200 chars; no equivalent validator or `Field(max_length=...)` exists for `description` on `TaskCreate`, `TaskUpdate`, or `TaskResponse` | If bounding input matters for this project's goals, add an explicit max length (mirrors the `title` pattern already in the codebase) — touches `app/`, needs explicit approval before any edit | High |
| F2 | Low | `app/models.py:54,110,204` | `assignee` field has no maximum length or format constraint | Same absence pattern as F1: `assignee: Optional[str]` with no validator anywhere in `models.py` | Same as F1 if desired; low priority since `assignee` is a display label, not used in any lookup/query key | High |
| F3 | Low | `app/storage.py:15,49-81`; `app/main.py:78-107` | No cap on total stored tasks; `GET /tasks` has no pagination (`limit`/`offset`) | `_tasks: dict[str, TaskResponse] = {}` grows on every `POST /tasks` with no bound; `get_all_tasks` always returns the full filtered list | Acceptable for a single-trusted-client learning app; worth a note if this API is ever exposed to untrusted/networked clients | Medium (inference about acceptable use, not a stated repo rule) |
| F4 | Informational | Repo-wide (`app/main.py` — all 5 routes) | No authentication or authorization on any endpoint | No dependency, header check, or auth middleware on any route in `main.py`; explicitly declared out of scope in `README.md` §9 and `CLAUDE.md` §7 ("Do not add authentication, user accounts...") | No action — confirmed intentional course-scope decision, not a gap | High |
| F5 | Low | `app/main.py:116,144,194` | `task_id` path parameter accepted as unconstrained `str`, not validated as UUID | `def get_task(task_id: str)` etc. use plain `str`, no `pattern=` constraint, even though `storage.add_task` always generates a UUID4 (`app/storage.py:31`) | Low priority; could add a UUID-shaped `Path` constraint for stricter input shaping — not a functional issue today since a mismatched id just yields a normal 404 | High |
| F6 | Low-Medium | `Dockerfile:2,10` | Base image `python:3.11-slim` pinned by mutable tag, not by digest | `FROM python:3.11-slim AS builder` / `FROM python:3.11-slim` — no `@sha256:...` digest pin | Pin by digest if reproducible/supply-chain-safe builds matter beyond local verification — already flagged as an open question in `docs/decisions/module4-docker-decision.md` §6 | High |
| F7 | Low | `Dockerfile:7` | Dependency install has no hash verification | `pip install --no-cache-dir --prefix=/install -r requirements.txt`; `requirements.txt` pins exact versions (`==`) but not hashes, and `--require-hashes` is not used | Consider `pip-compile --generate-hashes` + `--require-hashes` if supply-chain integrity is a goal; not urgent for a learning project | Medium |
| F8 | Informational | `.github/workflows/ci.yml` | CI runs tests only — no dependency/vulnerability scan, lint, or Docker build step | Workflow has exactly 4 steps: checkout, setup-python 3.11, `pip install -r requirements.txt`, `pytest -v`; this gap is also self-documented in `docs/decisions/module4-docker-decision.md` §4/§6 | Optional `pip-audit` or `docker build` CI step if desired; not urgent for current project scope | High |

## Course-scope classification

Before treating any of the above as an action item, note which findings are (or plausibly are) intentional scope decisions rather than defects:

**Confirmed course-scope decision — not a vulnerability:**
- **F4** (no auth). Directly documented in `CLAUDE.md` §7 and `README.md` §9. No action needed.

**Scope-adjacent, but not explicitly documented — recommend confirming rather than closing:**
- **F3** (unbounded task count / no pagination). Correlates with the documented "in-memory storage, no production database" decision (`CLAUDE.md` §1, `README.md` §9), but neither document explicitly says unbounded growth is acceptable. Plausible scope decision, not a confirmed one.
- **F8** (minimal CI). Nothing declares "no security scanning" as intentional; the repo's own `docs/decisions/module4-docker-decision.md` §4/§6 calls this a real, self-acknowledged gap rather than a choice. Treat as a genuine (low-severity) gap.

**Not course-scope — genuine findings independent of project purpose:**
- **F1, F2** (unbounded `description`/`assignee`). No document excludes input-length bounding; `title` and `tags` *are* bounded, suggesting inconsistency rather than a decision.
- **F5** (`task_id` not UUID-validated). Unrelated to any documented scope exclusion.
- **F6, F7** (Docker digest pin, pip hash verification). Independent supply-chain gaps. Note: F6 also inherits a separate, more significant open question — the Dockerfile's own existence was added without a recorded approval against `CLAUDE.md` §7's "no Dockerfiles without asking first" rule (see `docs/decisions/module4-docker-decision.md` §1 and `README.md` §6). That governance question is unresolved and distinct from the digest-pinning finding itself.

## Categories where no issue was found

- **Data exposure / stack traces / secrets:** clean. No `.env` file is committed (only `.env.example`, holding non-secret `PORT`/`APP_ENV`); no `os.environ`/`load_dotenv` reads exist in `app/`; no bare `except:`/broad exception handlers found in `app/*.py`; the FastAPI app has no `debug=True`; error bodies (`app/main.py:27`, `app/business_rules.py:36-39`) only ever contain task IDs or enum values, never internals.
- **CORS:** clean. `app/main.py`'s `CORSMiddleware` restricts `allow_origins` to exactly two localhost origins, `allow_methods` to `GET/POST/PATCH/DELETE`, `allow_headers` to `Content-Type`, and does not set `allow_credentials=True` with a wildcard origin.
- **Frontend XSS:** clean. Every user-controlled field rendered into the DOM (`title`, `description`, `tags`, `assignee`, `priority`, `id`, `due_date`) is passed through `escapeHtml()` before insertion into `innerHTML` (`frontend/index.html:575-673`).
- **Enum handling:** clean. `TaskStatus`/`TaskPriority` are Pydantic `str, Enum` types; an invalid value is rejected automatically with a 422, no manual validation needed or missing.
- **Broad exception behavior:** clean. No `except Exception`, bare `except:`, or exception-swallowing pattern exists anywhere in `app/`.

## Files inspected

`app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`, `requirements.txt`, `tests/conftest.py`, `tests/test_tasks.py` (targeted grep), `frontend/index.html`, `.github/workflows/ci.yml`, `Dockerfile`, `.dockerignore`, `.env.example`, `AGENTS.md`, `README.md`, `docs/decisions/module4-docker-decision.md`. Confirmed no `.env` file exists in the working tree.

## Assumptions / limits of this audit

- No live CVE/advisory database lookup was performed for the pinned dependency versions (`fastapi==0.115.0`, `pydantic==2.9.2`, `uvicorn==0.30.6`, `httpx==0.27.2`, `python-dotenv==1.0.1`, `pytest==8.3.3`) — this was a static code/config review only, not a dependency-vulnerability scan.
- The app was not run and no requests were sent; findings about runtime error behavior are inferred from code, not observed from an actual response.
- GitHub repository settings (branch protection, required reviews, secret scanning, fork-PR restrictions) aren't visible as filesystem content and weren't assessed.
- `venv/` and `.git/` internals were excluded from review as environment/tooling, consistent with `.gitignore`.
- All findings are course-scope-aware: several items that would be defects in a production API (no auth, no rate limiting, no pagination cap) are already explicitly declared out of scope by `CLAUDE.md`/`README.md` and are reported here as informational, not as defects — see "Course-scope classification" above for the specific breakdown.
