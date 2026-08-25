# Governance Worksheet — What I Shared With AI Tools (Module 5)

**Purpose:** a retrospective record of what was exposed to AI coding tools while working on the
Task Tracker repo, classified against a risk rubric, so sharing habits can be reviewed rather than
assumed safe by default.

**Scope of this draft:** the table below covers only **one Claude Code session** (2026-08-25,
Module 5 work). It was built from the actual tool-call record of that session — every row maps to
a real file read or grep, nothing invented. It does **not** cover any other session, any other AI
tool used during the course, or any work before this session. Add rows for those separately;
do not assume the "Low" pattern below generalizes without checking each one.

## Risk rubric

- **Low:** public code, course toy project code, no sensitive data, no proprietary logic.
- **Medium:** private but non-sensitive code, internal implementation details, or non-public repo
  context with no secrets and no PII.
- **High:** credentials, tokens, secrets, production config, real customer/user data, regulated
  data, or code not authorized to share.

## What I shared (this session) and risk classification

| Item shared | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|
| Backend source (`app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`) — full file contents | Low | Explicitly a "learning-project" toy repo per `CLAUDE.md` §Project, no proprietary logic, no secrets present in any of these files | Already appropriate as-is — no safer version needed for this project's actual scope | None |
| Test suite (`tests/conftest.py`, `tests/test_tasks.py`) — full/partial contents | Low | Same course-toy-project reasoning; test code contains no data, only assertions against dummy task fields | Already appropriate | None |
| Frontend source (`frontend/index.html`) — targeted excerpts via grep | Low | Static demo Kanban board, no user data, no API keys, client-side only | Already appropriate | None |
| Dependency manifest (`requirements.txt`) — full contents | Low | Public, pinned package names/versions only — no internal registry URLs or private package names | Already appropriate | None |
| CI workflow (`.github/workflows/ci.yml`) — full contents | Low | Generic GitHub Actions steps (checkout, setup-python, pytest) — no secrets, no deploy credentials, no org-specific runners | Already appropriate | None |
| Docker build config (`Dockerfile`, `.dockerignore`) — full contents | Low | No registry credentials, no private base images, non-root user pattern is a public best practice, not proprietary | Already appropriate | None |
| `.env.example` — full contents | Low | Contains only placeholder keys (`PORT`, `APP_ENV`) with non-secret example values; confirmed no actual `.env` file exists in the repo, so no real secret was ever exposed | Already appropriate — but worth stating explicitly here that the real `.env` (if one is ever created) should never be pasted, only `.env.example` | None |
| Project/governance docs (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/decisions/module4-docker-decision.md`) — full contents | Low | These are written specifically to be read by AI coding agents (`AGENTS.md`'s own first line), contain no business-sensitive or proprietary content, only course-project conventions | Already appropriate | None |
| Your email address (`eliechalhoub02@gmail.com`) — present in every turn's system context this session | **Ambiguous — see note below** | Doesn't cleanly fit the rubric: it's PII (your own), but it wasn't something you deliberately pasted — it's injected automatically by the harness for session identification. The rubric's Medium tier explicitly requires "no PII," which this fails, but High requires "regulated data" or "customer/user data," which this also doesn't clearly meet since it's your own single identifier, not a data subject's record | If the course rubric wants a hard Low/Medium line drawn on any PII presence regardless of source, this moves to Medium; if the rubric only cares about *deliberately shared* data, this row may not belong on the worksheet at all | Whether auto-injected session metadata (vs. content actively typed or pasted) counts as "shared" for this retrospective — worth deciding once, since it recurs in every session, not just this one |

## Personal AI usage rules

Derived from this worksheet's own notes — each rule is meant to be concrete enough that a
teammate could tell whether a future action violates it.

| Rule category | Rule | Evidenced by |
|---|---|---|
| 1. What I will never paste | Never paste the contents of `.env`, or any file/value I know or suspect holds a real credential, token, or secret — only placeholder files like `.env.example` are safe. Before pasting an unfamiliar file, check `.gitignore` and `git status` first to see if it's excluded for a reason — don't paste, then wonder. | The `.env.example` row above: no real `.env` file exists in this repo; only the placeholder was ever shared. |
| 2. What I will always verify before accepting | Before accepting any AI-reported security or code-behavior finding, verify it against the exact file and line it cites. If I can't locate the referenced function, config, or pattern with a grep or direct read, treat the finding as unverified — not true — until I check. | A Module 5 grading exercise (this repo, same course) produced 10 synthetic AI security findings; 6 of them (SQL injection, CORS wildcard, stack-trace leak, sequential IDs, Docker-as-root, mass assignment) were False Positives once checked against the actual file each one cited. |
| 3. How I will record AI contributions | Within the same day as an AI coding session, append a new dated row (or block) to this worksheet using the existing table format — listing what was shared and its risk tier per the rubric. Don't carry forward a prior session's "mostly Low" result without re-checking that session's actual shares. | This worksheet's own scope note: it currently covers only one session and explicitly instructs adding rows per session rather than assuming the pattern generalizes. |

## Open items

- **Decide the email-address question above** and update that row's Risk column once resolved.
- **Add rows for any other session/tool** used earlier in the course — this worksheet currently
  reflects one session only and should not be read as a complete governance record.
