# Personal AI Coding Playbook

**Note:** this version is an illustrative example built from real events in this session, not a
personal reflection written by the repo owner. Voice is AI-approximated, not genuinely the
author's own — replace each bullet with your own wording and, where different, your own course
incidents before treating this as final.

## 1. When I reach for AI first
- Grading AI-generated findings against real code (e.g., the security-review exercise where 6 of
  10 synthetic AI findings turned out to be false positives once checked against the actual files).
- First-pass documentation drafting from a codebase I already trust, when I plan to verify the
  output myself afterward.

## 2. When I do not reach for AI
- Deciding whether a project rule was actually violated and what to do about it (e.g., the
  `Dockerfile` vs. `CLAUDE.md` "no Dockerfiles without asking" conflict — AI surfaced it, but the
  call is mine).
- Accepting an unfamiliar code explanation without checking it — the "local shim" comment in
  `app/storage.py` referenced something that doesn't exist anywhere in the codebase.

## 3. My non-negotiables
- I will never let an `app/` change get applied without explicitly approving the specific diff
  and file — even a "minimal one-line fix" stayed unapplied until I confirmed both the value and
  the path.
- I will never treat an AI-written comment or docstring as ground truth without grepping for what
  it claims to reference.

## 4. My review rules
- Before accepting any AI security or code-behavior finding, check it against the exact file/line
  cited — proven necessary after my own grading exercise caught 6/10 synthetic findings (SQL
  injection, CORS wildcard, sequential IDs, etc.) as false positives.
- Before accepting an AI's "why" explanation for existing code, verify the explanation references
  something real.

## 5. What I am still figuring out
- Whether "scope-adjacent but undocumented" findings (like the missing pagination cap) should
  default to Valid or Noise — left ambiguous in my own security review.
- How often I actually need to re-verify a standing doc like `AGENTS.md` against the code, versus
  trusting it as current.

## 30-day re-read commitment
I will re-read this playbook in 30 days and check whether these rules still match how I actually
worked, not just how I intended to work.

## Decision Card
- For a new feature I reach for: a repo-grounded plan citing actual file/line evidence (e.g.,
  `docs/decisions/comments-feature-plan.md`) over a generic chat answer — the single most
  important fact in that plan (this repo has zero existing nested routes) was only catchable by
  reading the actual code.
- For a code review I reach for: direct file/line verification (grep + read) against the specific
  claim being reviewed — proven necessary when 6 of 10 synthetic AI security findings turned out
  to be false positives once checked against the exact file each one cited.
- For debugging I reach for: grepping the actual codebase to confirm or kill a claim, not
  reasoning about it abstractly — the "local shim" comment in `app/storage.py` could only be
  resolved by checking whether it existed anywhere at all (it didn't).
- For infrastructure I reach for: separate steps for drafting vs. approving — the `Dockerfile`
  here was drafted but never routed through an approval check against `CLAUDE.md`'s rule, and
  that gap is still open.
- I will never paste a real `.env` file into an AI tool. This didn't actually happen during this
  course — no real `.env` ever existed in this repo — but it's the concrete thing I'd assume
  could get pasted or pushed by accident, since the setup instructions literally tell you to
  create one from `.env.example`.
- My one rule is: an `app/`-level edit needs the file explicitly approved, not just the value —
  confirmed when a partial approval (value only, no file) correctly did not trigger an edit.
