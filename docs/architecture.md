# Architecture Doc — Context-Strategy Comparison Log

Comparison of three context strategies used to produce a one-page architecture doc for the
Task Tracker repo: Strategy A (`docs/architecture-A.md`, minimal context), Strategy B
(`docs/architecture-B.md`, structured context via `AGENTS.md` + file summaries), and Strategy C
(`docs/architecture-C.md`, targeted context limited to `app/main.py`, `app/models.py`,
`app/storage.py`).

## 1. Strategy comparison table

| Strategy | What it got right | What it got wrong, missed, or invented | Best suited for |
|---|---|---|---|
| **A — Minimal context** | Full, accurate coverage of all 6 sections: correct `Task` fields, correct creation flow, 9 correctly-cited key files (including `app/business_rules.py`, `tests/`, `requirements.txt`), and all three genuine `[VERIFY]` gaps (Python version, unused `.env`, dead "local shim" branch) surfaced independently. | Nothing invented or wrong — it independently derived every claim from the code itself. | A first-pass or "final" reference doc where you want independent verification against the actual code, not a summary of a summary — worth the higher read cost when correctness can't be assumed. |
| **B — Structured context (AGENTS.md + file summaries)** | Landed on essentially the same facts as A (same 9 key files, same data model, same flow, same 3 `[VERIFY]` items) — because it quoted `AGENTS.md` directly rather than re-deriving, every claim traces to a specific section (§1, §3, §6). | Nothing invented, but it's structurally unable to catch an error: if `AGENTS.md` itself had drifted from the code, B would have propagated that drift silently, since it never touched the underlying files to check. | Fast, low-cost doc regeneration once a trusted summary document already exists and is known to be current — the traceability (every claim → one AGENTS.md line) is a real advantage for review speed. |
| **C — Targeted context (main.py, models.py, storage.py only)** | Data model (§2) and creation flow (§3) came through fully accurate and complete — identical in substance to A and B, since both sections live entirely inside the 3 files read. | Explicitly could not fill in: exact status-transition rules, exact overdue definition, frontend file/behavior, test conventions, Python version, deployment scope — all correctly marked "not visible" rather than guessed. Also honestly under-delivered on "Key files" (4 vs. the requested 5–10) rather than padding the list. | Narrow, single-answer questions fully contained in a small file set (e.g., "what happens on task creation," "what does the Task schema look like") — cheapest option, but a poor fit for anything crossing into business rules, frontend, or project-wide conventions. |

## 2. Verdict

**Strategy B**, with a condition: use it as the default for regenerating this doc, but re-run
Strategy A whenever `AGENTS.md` itself changes, to catch drift before it propagates. A and B
produced functionally identical output here, which means B's extra traceability (every claim
pins to a specific `AGENTS.md` section) came at zero accuracy cost this time — but that's only
true because `AGENTS.md` was itself already verified. B has no mechanism to notice if
`AGENTS.md` goes stale; A does, because it reads the code directly. C is disqualified for a
"final" doc specifically — it left 3 of 6 required sections honestly incomplete, which is the
right behavior under its own constraint but not what a canonical reference doc needs.

## 3. Two-sentence context-engineering rule

For task shape X = a narrow, single-behavior question fully contained in 2–3 files (e.g., "what
happens on task creation," "what fields does this entity have"), I use Strategy C because it's
the cheapest option that still gets those specific sections completely right, as shown by C
matching A and B exactly on data model and request flow. For task shape X = a reference document
meant to be trusted later, or any question touching business rules, frontend behavior, or
project-wide conventions, I use Strategy A or B instead, because C's honest "not visible" gaps
land precisely on those fronts, silently under-delivering wherever the answer needed more than
the anchor files could provide.
