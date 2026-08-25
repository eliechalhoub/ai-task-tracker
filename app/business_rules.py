from fastapi import HTTPException, status
from datetime import date 

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate that a status change is an allowed transition.

    Only called from `main.update_task` (PATCH), against the task's
    existing stored status. Task creation (`main.create_task`) does not
    call this function, so `POST /tasks` can set any `TaskStatus` value
    directly (e.g. `Done`) with no transition check.

    Args:
        current (TaskStatus): The task's status before the change.
        new (TaskStatus): The requested new status.

    Returns:
        None: Returns nothing when the transition is allowed.

    Raises:
        HTTPException: 422 Unprocessable Entity if `(current, new)` is not
            in `VALID_TRANSITIONS` (this includes same-status-to-same-status).
            The error detail lists the allowed transitions.
    """
    # Same -> same is invalid. Anything not in VALID_TRANSITIONS is invalid.
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )

def is_task_overdue(due_date: date | None, task_status: TaskStatus, today: date | None = None) -> bool:
    """Determine whether a task counts as overdue.

    A task is overdue only if `due_date` is set, `task_status` is not
    `TaskStatus.DONE`, and `due_date` is strictly before `today`.

    Args:
        due_date (date | None): The task's due date, or None if unset.
        task_status (TaskStatus): The task's current status.
        today (date | None): Date to compare against; defaults to
            `date.today()`. Injectable for tests.

    Returns:
        bool: True if the task is overdue, False otherwise.
    """
    if due_date is None or task_status == TaskStatus.DONE:
        return False
    return due_date < (today or date.today())