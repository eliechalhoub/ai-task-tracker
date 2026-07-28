"""
Module 2 in-memory storage for the Task Tracker.

No database, no ORM -- just a module-level dict keyed by generated string id.
id/created_at/updated_at are assigned here, never accepted from client input.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    record = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = record
    return record


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
) -> list[TaskResponse]:
    results = list(_tasks.values())
    if status is not None:
        results = [t for t in results if t.status == status]
    if priority is not None:
        results = [t for t in results if t.priority == priority]
    return results


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
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
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()
