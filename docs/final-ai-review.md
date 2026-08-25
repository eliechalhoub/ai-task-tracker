# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: **yes** — `AGENTS.md` §2 lists exact pinned
  dependency versions and the real run/test commands, not generic framework advice.
- Docs-first/read-first guardrail included: **yes** — the Module 5 version of this guardrail
  (read-only by default, `docs/` as the default edit surface) was incompatible with the Final
  Project's actual requirements (running the app, running tests, building Docker, making small
  justified fixes to `app/`/`frontend/`), so it was replaced rather than dropped: `AGENTS.md` §4
  now requires reading `README.md`, `AGENTS.md`, and the relevant `docs/` note for an area
  before editing it, without blocking the edits this phase needs.
- Unexpected app/frontend edits rule included: **yes** — `AGENTS.md` §4 restricts `app/`/
  `frontend/` changes to a small, specific bug/security/documentation-supported fix, explained
  here in this document. (No `app/` or `frontend/` file was actually changed this session —
  only `AGENTS.md`, `README.md`, and files under `docs/`.)

## AI code review mini-log

Reviewed file: the real `README.md` diff produced this session (`git diff README.md`), adding
the Final Project section and two documentation fixes.

| AI comment                                                                                                                                                                      | Grade: Useful / Noise / Wrong | Reason                                                                                                                                    | Verification or decision                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| The Docker commands under the new "Final Project" quick-reference duplicate the fuller version in section 6 but drop `docker logs tt-dev` — risks the two drifting apart later. | Useful                        | Real duplication hazard in a file that has already drifted before (the Python-version and Docker-approval gaps found earlier this course) | Left as-is for this submission (both blocks are currently correct), noting it as a known follow-up rather than fixing now                           |
| `sleep 2` before the Docker health check is a fixed wait, not a poll/retry loop — could still race on a slower machine or CI runner.                                            | Useful                        | This is a documented anti-pattern (the same one this session's own `run` skill explicitly warns against: "don't sleep 5, poll the port")  | Kept `sleep 2` for this submission since it's simple and reproduced the fix once; flagging rather than silently trusting it as a permanent solution |
| The "AI assistance summary" paragraph references `docs/final-ai-review.md` before that file existed in the repo at the time the README diff was written.                        | Noise                         | True but self-resolving — this document was created in the same session, so the reference isn't dangling by submission time               | No change; noted only because it's the kind of sequencing sloppiness worth catching, even though it's harmless here                                 |

No genuinely **Wrong** comment was found in this diff — every factual claim in it (`/health`
shape, test count, Docker commands, CI behavior) was independently verified against a real
command run this session before being written. Listing three real comments rather than
manufacturing a fourth "Wrong" one to fill the category.

## AI security mini-review

Reusing `docs/security-review.md` (produced earlier this course from direct file inspection,
not re-run from scratch this session since no `app/` code changed).

| Finding                                                                  | File evidence                                                                             | Grade: Valid / False Positive / Noise      | Reason                                                                                                                                                                                                          | Next action                                                                                                                                                                                          |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `description` field has no maximum length                                | `app/models.py:51,107,201` — no `field_validator`/`Field(max_length=...)`, unlike `title` | Valid                                      | Real, verifiable inconsistency: `title` and `tags` are both bounded, `description` isn't                                                                                                                        | Proposed fix drafted earlier this course, never applied (see "Rejected AI output" below) — left open for now, not in scope for this submission per the no-new-app-changes-without-justification rule |
| No authentication on any endpoint                                        | `app/main.py` — no auth dependency/middleware on any route                                | Valid (course-scope limitation, not a bug) | Explicitly declared out of scope in `CLAUDE.md` §7 and `README.md` §9, but per the grading rubric a course-scope limitation that would matter outside the learning context still counts as Valid, not dismissed | No action — documented, not fixed, consistent with project scope                                                                                                                                     |
| Docker base image (`python:3.11-slim`) pinned by mutable tag, not digest | `Dockerfile:2,10`                                                                         | Valid                                      | Real supply-chain gap, independent of course scope                                                                                                                                                              | No action this submission — flagged, not required for a local-verification-only container                                                                                                            |

## Manual security check

I did not just accept AI-reported findings this session. The clearest example: Docker
`/health` verification required running real commands in my own terminal (Docker's socket
permissions blocked the AI from running them directly), and my first real run returned
`HTTP_STATUS:000` — a genuine failure the AI had not predicted or written around. I reported
the raw output rather than re-running it silently until it passed, which is what surfaced the
startup-race issue that's now documented and fixed in `README.md` and `docs/release-evidence.md`.
This wasn't AI catching its own mistake — it was a human running the actual command and reporting
what actually happened.

## One AI output I rejected or corrected

Earlier this course, a minimal diff was proposed for `app/models.py` — adding
`MAX_DESCRIPTION_LENGTH = 2000` and bounding the `description` field with `Field(max_length=...)`,
addressing the security-review finding above. I confirmed the proposed value (`2000`) but never
approved the actual file edit, and later explicitly told the AI to forget the diff entirely. It
was never applied. I rejected it not because the reasoning was wrong, but because a proposed
`app/` change needs a deliberate yes on the specific file, not just agreement on a parameter —
and I hadn't given that.

## Three AI usage rules

1. **Never paste:** a real `.env` file, or anything I know or suspect holds a live credential or
   token, into an AI tool. (This never actually happened during the course — no real `.env` ever
   existed in this repo — but it's the concrete thing I'd assume could get pasted or pushed by
   accident, since the setup instructions literally tell you to create one from `.env.example`.)
2. **Always verify:** any AI-reported security or code-behavior finding against the exact file
   and line it cites before accepting it — proven necessary when 6 of 10 synthetic AI security
   findings graded earlier this course turned out to be false positives once checked against the
   actual code.
3. **Record AI contributions by:** appending a dated entry to `docs/governance-worksheet.md`
   after each AI coding session, listing what was shared and its risk tier, rather than assuming
   a prior session's pattern still holds.

## Ownership statement

I'm comfortable submitting this repo as my own work because every claim in it that could be
checked, was checked: the test suite was actually run (30/30), the Docker image was actually
built and its `/health` endpoint actually curled — twice, after the first attempt genuinely
failed — and the CI status was pulled from GitHub's own API rather than assumed. Where AI
findings disagreed with the real code (the synthetic security-finding grading exercise) or where
an AI-authored comment referenced something that didn't exist (the `app/storage.py` "local shim"),
I caught it by checking the file myself, not by trusting the explanation. The one `app/` change
that was proposed during this course was deliberately left unapplied because I hadn't given it
the specific approval it needed, not because I forgot about it. I understand the layering,
validation rules, and known gaps (unbounded `description`, the Dockerfile approval question)
well enough to explain any of them if asked, which is the bar I'm holding this submission to.
