# Verification — Mid-Course Project

## Baseline check (before any changes)
```
18/18 passed
```

## Backend test results (after both features)
```
27/27 passed
```
18 pre-existing + 9 new (4 due-date, 5 tags).

## Manual browser checks
- [ ] Task with due date shows the date on its card
- [ ] Past-due, non-Done task shows a red "Overdue" pill
- [ ] "Overdue only" filter narrows/restores the board
- [ ] Tags show as chips on cards
- [ ] Blank tag is rejected with a message near the tags field
- [ ] Tag filter narrows the board
- [ ] Module 3 behaviors still work: drag-and-drop, both modal flows, all 4 UI states

## Behavior contract: before/after the `_not_found()` refactor
| | Result |
|---|---|
| Before refactor | 27/27 passed |
| After refactor | 27/27 passed |

## Break Test evidence

### Break test 1 — `due_date` type
- **Test:** `test_create_task_with_invalid_due_date_format_returns_422`
- **Change:** `TaskCreate.due_date` temporarily changed from `Optional[date]` to `Optional[str]`.
- **Result:** not a clean assertion failure — an unhandled `ValidationError` crash, because the bad string passed `TaskCreate` untouched and only failed later when `storage.add_task()` built a `TaskResponse` (still strictly typed). In real FastAPI this would surface as a 500, not a 422.
- **Restored** immediately; full suite back to 27/27.

### Break test 2 — tags blank-check
- **Test:** `test_create_task_with_blank_tag_returns_422`
- **Change:** removed the blank-tag check inside `_clean_tags()`.
- **Result:** clean assertion failure (201 instead of 422), as expected.
- **Restored** immediately; full suite back to 27/27.

### Why both are included
Two similar-looking changes produced different failure modes — one a crash, one a clean fail. Validation living only on the input model isn't enough if a downstream model still enforces the same constraint.