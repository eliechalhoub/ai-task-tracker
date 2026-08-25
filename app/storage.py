"""
Module 2 in-memory storage for the Task Tracker.

No database, no ORM -- just a module-level dict keyed by generated string id.
id/created_at/updated_at are assigned here, never accepted from client input.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from app.business_rules import is_task_overdue

from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task record.

    Generates the task's `id` (UUID4 string) and `created_at`/`updated_at`
    timestamps (UTC). `description` falls back to `""` if not supplied or
    falsy.

    Args:
        payload (TaskCreate): Validated task fields from the client.

    Returns:
        TaskResponse: The stored task record.
    """
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    record = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,      # new
        tags=payload.tags,              # new
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = record
    return record


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    tag: Optional[str] = None,
    overdue: Optional[bool] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally filtered.

    Filters are applied sequentially and combine with AND logic: a task
    must match every supplied filter to be included. `overdue` is computed
    via `business_rules.is_task_overdue` at call time, not stored.

    Args:
        status (Optional[TaskStatus]): Exact status to match.
        priority (Optional[TaskPriority]): Exact priority to match.
        tag (Optional[str]): Exact, case-sensitive tag string that must be
            present in a task's `tags` list.
        overdue (Optional[bool]): Overdue state (per `is_task_overdue`) to match.

    Returns:
        list[TaskResponse]: Tasks matching all supplied filters, in the
            iteration order of the underlying storage dict (insertion order).
    """
    results = list(_tasks.values())
    if status is not None:
        results = [t for t in results if t.status == status]
    if priority is not None:
        results = [t for t in results if t.priority == priority]
    if tag is not None:
        results = [t for t in results if tag in t.tags]
    if overdue is not None:
        results = [t for t in results if is_task_overdue(t.due_date, t.status) == overdue]
    return results


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a single task by id.

    Args:
        task_id (str): The task's generated UUID string.

    Returns:
        Optional[TaskResponse]: The task, or None if no task with that id
            exists.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly set on `payload` are applied
    (`model_dump(exclude_unset=True)`), so omitted fields are left
    unchanged. `updated_at` is refreshed to the current UTC time on every
    successful update.

    [VERIFY] The `hasattr(existing, "model_copy")` fallback branch below is
    described in an inline comment as support for "the local shim, which
    doesn't implement model_copy" -- it's unclear from this module what
    that shim is or when this path would actually be exercised, since
    `TaskResponse` is a Pydantic v2 `BaseModel` and always has
    `model_copy`.

    Args:
        task_id (str): The task's generated UUID string.
        payload (TaskUpdate): The fields to change.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task with
            `task_id` exists.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None

    changes = payload.model_dump(exclude_unset=True)
    updated = existing.model_copy(update=changes) if hasattr(existing, "model_copy") else None
    if updated is None:
        # Fallback for the local shim, which doesn't implement model_copy.
        data = existing.model_dump()
        data.update(changes)
        updated = TaskResponse(**data)

    updated.updated_at = datetime.now(timezone.utc)
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task by id if it exists.

    Args:
        task_id (str): The task's generated UUID string.

    Returns:
        bool: True if a task was found and deleted, False if no task with
            `task_id` existed.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()
