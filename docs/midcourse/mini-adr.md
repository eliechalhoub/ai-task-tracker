# Mini-ADR: Mid-Course Features (Due Dates + Tags)

## Features selected

1. **Due dates + overdue filter**
2. **Tags / labels**

Both chosen because both are visible/usable in the Kanban UI and both fit cleanly on top of the existing `TaskCreate`/`TaskUpdate`/`TaskResponse` model shape without touching status/priority/transition logic already covered by Modules 2-3 tests.

## Decision: where "overdue" is computed

**Chosen:** a plain function, `is_task_overdue(due_date, status, today=None)` in `app/business_rules.py`, called by `storage.get_all_tasks()` for the `?overdue=true` filter. The frontend has its own small mirrored version (`isOverdue()` in `index.html`) purely for the card pill.

**Alternative considered and rejected:** a Pydantic `@computed_field` on `TaskResponse` so every response always carries `is_overdue`. Rejected as unnecessary complexity for a learning project — it also wouldn't remove the need for frontend-side logic anyway, since optimistic UI updates need it client-side regardless.

**Trade-off accepted:** the frontend and backend each have their own copy of the overdue rule. If the rule changes, both places need updating.

## Decision: tags as `list[str]`, not comma-separated string

**Chosen:** `tags: list[str]` on the Pydantic models, validated (trimmed, non-blank, max 5, max 30 chars each, deduplicated). The frontend converts to/from a comma-separated string only at the UI boundary.

**Alternative considered and rejected:** storing tags as a single comma-separated string field on the backend. Rejected because it pushes parsing/validation ambiguity into every consumer of the field instead of handling it once, centrally.

## Decision: query-param filters return a plain list, not paginated results

**Chosen:** `GET /tasks?tag=...&overdue=...` still returns a flat JSON array, same shape as before.
**Rejected as out of scope:** pagination/wrapper metadata — not needed at this scale, and would break the existing frontend rendering code.

## Decision: refactor scope

**Chosen:** one small refactor — extracting the repeated `HTTPException(status_code=404, ...)` construction in `app/main.py` into a single `_not_found()` helper, done after both features passed their tests, confirmed behavior-identical before/after (see `verification.md`).
**Rejected as out of scope:** restructuring into an `APIRouter`-per-resource pattern, or moving to a real database — both reasonable future improvements, unrelated to this checkpoint's two features.
