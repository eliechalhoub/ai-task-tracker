# Technical Decision Note: Dockerfile Design

**Module:** Module 4 — Task Tracker
**Status:** Draft
**Scope:** `Dockerfile`, `.dockerignore` (local container build/run only)

---

## 1. Context

The Task Tracker has been a locally-run FastAPI app (`uvicorn app.main:app --reload --port 8000`) with no containerization through Module 3. For Module 4, a `Dockerfile` and `.dockerignore` were added at the repo root to let the backend be built and run as a container locally, independent of a developer's virtualenv setup.

`CLAUDE.md` §7 ("Do-not rules") states: *"Do not add deployment steps, Dockerfiles, or CI/CD config... ask before implementing."* `[VERIFY]` — this Dockerfile was added without a recorded approval against that rule; the README (§6) already flags this same conflict. This note does not resolve that conflict; it documents the technical design as built, on the assumption Docker support is in scope for Module 4.

The app itself has no authentication, no database, and is not deployed anywhere (see `README.md` §9, `CLAUDE.md` §1). This container is for local build/run verification only — it does not represent or enable production deployment.

Once reviewed, link this note from `README.md` §10 alongside `mini-adr.md`.

## 2. Decision

Use a two-stage `Dockerfile`:

1. A `builder` stage (`python:3.11-slim`) installs pinned dependencies from `requirements.txt` into `/install` via `pip install --prefix=/install`.
2. A final runtime stage (also `python:3.11-slim`) copies only the installed packages (`/install` → `/usr/local`) and the `app/` source tree from the builder stage — no build toolchain, no `requirements.txt`, no test/docs/frontend files.

The final image:
- Creates and runs as a dedicated non-root user (`app`), never `root`.
- Sets `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`.
- Exposes port 8000 and runs `uvicorn app.main:app --host 0.0.0.0 --port 8000` as its `CMD`.

`.dockerignore` excludes `.env`, `.git`, `venv/`/`.venv/`, Python caches (`__pycache__/`, `*.pyc`, `*.pyo`, both root-level and `**/`-recursive), `.pytest_cache/`, and common editor/OS artifacts from the build context, so none of those are baked into the image.

This is a decision to support **local container verification**, not deployment. There is no orchestration file, no published/pushed image, and no production hardening (no healthcheck directive, no resource limits, no image scanning) anywhere in this repo.

## 3. Alternatives Considered

- **Single-stage build.** Simpler `Dockerfile`, but the final image would carry `pip`'s build cache and any compiled wheels' build dependencies unnecessarily, since nothing here needs a compiler toolchain at runtime. Rejected in favor of the smaller two-stage result.
- **Alpine base instead of `python:3.11-slim`.** Smaller base image, but higher risk of wheel-compatibility issues (musl vs. glibc) for the pinned dependency set. `[VERIFY]` — this wasn't empirically tested against Alpine; `slim` was chosen for known compatibility, not a measured image-size trade-off.
- **Running as root.** Simpler (`USER app` and the `useradd` step could be dropped), but rejected outright — non-root was treated as a baseline requirement, not a nice-to-have.
- **Bind-mounting source instead of `COPY`ing it in.** Would let code changes reflect without a rebuild, closer to a dev-container workflow. Rejected for this module's stated goal (verify the app builds and runs as a container), not chosen as an ongoing dev loop replacement for `uvicorn --reload`.

## 4. Trade-offs

Two-stage build adds a bit of `Dockerfile` complexity — two `FROM` lines, an explicit `COPY --from=builder` — but it buys a smaller final image with no compiler toolchain sitting around at runtime. For a learning project of this size the extra stage is cheap; on a much smaller project I might not have bothered.

Baking `app/` into the image instead of bind-mounting it means the container isn't part of the everyday dev loop — every code change needs a `docker build` before it shows up in the container, so `uvicorn --reload` stays the primary way I iterate, and Docker is really just a "does this still work in a clean environment" check.

`requirements.txt` pins exact versions (`==`), so the dependency set inside the image is reproducible. What isn't pinned anywhere is the Docker Engine version needed to build/run this — a real gap, just not one this project has hit yet.

The biggest trade-off is that nothing in CI touches this `Dockerfile` at all. `pytest -v` runs on every push, but a change that quietly breaks the Docker build (a bad `COPY` path, a dependency that stops installing cleanly) would only be caught by someone remembering to run `docker build` by hand.

## 5. Consequences

- The backend can now be built and run as a container locally, independent of a developer's Python/virtualenv setup, using `docker build -t task-tracker:dev .` and `docker run -p 8000:8000 task-tracker:dev`.
- Container attack surface is reduced by running as non-root and excluding `.env`/`.git`/caches from the build context — but this is a local-verification container, not a hardened production image, and should not be represented as one.
- The `CLAUDE.md` vs. actual-repo-state conflict (Do-not rules forbidding Dockerfiles without prior approval) remains open and unresolved by this note.
- Docker verification is entirely manual; nothing in CI protects this `Dockerfile` from silently rotting as `app/` or `requirements.txt` change.

I would do this differently by adding a `docker build` step to `ci.yml` from the start instead of treating it as a manual afterthought — the whole point of a Dockerfile is that "it works on my machine" isn't good enough, and right now CI can't actually catch a broken image. I'd also raise the `CLAUDE.md` conflict before writing the Dockerfile rather than after, since retrofitting approval is more awkward than asking up front.

## 6. Open Questions

Should `CLAUDE.md`'s Do-not rules be updated to explicitly permit this Dockerfile for Module 4, or should the Docker artifacts be pulled pending explicit approval? I lean toward updating `CLAUDE.md` once this is reviewed, since the container is genuinely useful and scoped to local verification, not deployment.

Should `ci.yml` gain a `docker build` step so a broken Dockerfile fails CI instead of going unnoticed? I think yes, even a build-only step (no push, no registry) would close most of the gap.

Is `python:3.11-slim` the correct/expected base given the repo has no authoritative Python version pin outside `ci.yml`? Worth a quick confirmation with course staff rather than assuming.

Is there a minimum supported Docker Engine version this should document? Not something I've tested against, and probably low priority for a learning project, but worth a one-line note if anyone else needs to run this.
