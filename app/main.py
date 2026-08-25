from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
from app import storage
from app.business_rules import validate_status_transition

app = FastAPI(title="Task Tracker API", version="0.2.0")

# Module 3: the frontend is a static file opened via a local dev server (e.g. VS
# Code Live Server on 5500), which is a different origin than the API on 8000.
# Allow only the specific local origins the frontend actually runs on.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

def _not_found(task_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

@app.get("/health")
def health():
    """Report service liveness.

    Returns:
        dict: A JSON-serializable payload with:
            - status (str): Always "ok".
            - timestamp (str): Current UTC time in ISO 8601 format.

    Example:
        GET /health -> 200
        {"status": "ok", "timestamp": "2026-08-25T12:00:00+00:00"}
    """
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    `payload.status` (default `TaskStatus.TODO`) is stored as-is: creation
    does not call `business_rules.validate_status_transition`, so any
    `TaskStatus` value can be set directly here. The transition restriction
    in `business_rules.VALID_TRANSITIONS` only applies to `PATCH` updates
    (see `update_task`), not to creation.

    Args:
        payload (TaskCreate): Client-supplied task fields. `id`,
            `created_at`, and `updated_at` are not accepted here; they are
            assigned in `storage.add_task`.

    Returns:
        TaskResponse: The newly created task, including its generated `id`
            and timestamps.

    Raises:
        fastapi.exceptions.RequestValidationError: If `payload` fails
            Pydantic validation (e.g. blank title, too many tags); FastAPI
            converts this to a 422 response.

    Example:
        POST /tasks
        {"title": "Write docs", "priority": "High"}
        -> 201
        {"id": "...", "title": "Write docs", "status": "ToDo", ...}
    """
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: Optional[TaskStatus] = Query(default=None),
    priority: Optional[TaskPriority] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    overdue: Optional[bool] = Query(default=None),
):
    """List tasks, optionally filtered by status, priority, tag, and overdue state.

    Filters are optional and combine with AND logic when more than one is
    supplied (see `storage.get_all_tasks`).

    Args:
        status (Optional[TaskStatus]): Only return tasks with this exact status.
        priority (Optional[TaskPriority]): Only return tasks with this exact priority.
        tag (Optional[str]): Only return tasks whose `tags` list contains
            this exact string (case-sensitive; tags are not case-normalized
            anywhere in this codebase).
        overdue (Optional[bool]): Only return tasks whose overdue state
            (per `business_rules.is_task_overdue`) matches this value.

    Returns:
        list[TaskResponse]: Matching tasks, in the underlying storage's
            iteration order.

    Example:
        GET /tasks?status=InProgress&tag=backend -> 200
        [{"id": "...", "status": "InProgress", "tags": ["backend"], ...}, ...]
    """
    return storage.get_all_tasks(status=status, priority=priority, tag=tag, overdue=overdue)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by id.

    Args:
        task_id (str): The task's generated UUID string.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with `task_id` exists.

    Example:
        GET /tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6 -> 200
        {"id": "3fa85f64-...", "title": "...", ...}
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise _not_found(task_id)
    return task


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Only fields explicitly present in `payload` are changed (Pydantic
    `exclude_unset=True` semantics, applied in `storage.update_task`).
    Explicit `null` is rejected for `title`, `description`, `status`,
    `priority`, and `tags` at the model level (see `TaskUpdate`);
    `assignee` and `due_date` accept explicit `null` to clear them.

    If `status` is included in the payload, the transition from the task's
    current status is validated against
    `business_rules.VALID_TRANSITIONS` before the update is applied.

    Args:
        task_id (str): The task's generated UUID string.
        payload (TaskUpdate): The fields to change.

    Returns:
        TaskResponse: The task after applying the update.

    Raises:
        HTTPException: 404 if no task with `task_id` exists.
        HTTPException: 422 if `payload.status` is set and the transition
            from the task's current status is not in
            `business_rules.VALID_TRANSITIONS`.
        fastapi.exceptions.RequestValidationError: If `payload` fails
            Pydantic validation.

    Example:
        PATCH /tasks/3fa85f64-... {"status": "InProgress"} -> 200
        {"id": "3fa85f64-...", "status": "InProgress", ...}
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise _not_found(task_id)
        validate_status_transition(existing.status, payload.status)

    updated = storage.update_task(task_id, payload)
    if updated is None:
        raise _not_found(task_id)
    return updated


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)
def delete_task(task_id: str):
    """Delete a task by id.

    Args:
        task_id (str): The task's generated UUID string.

    Returns:
        None: No response body (204 No Content).

    Raises:
        HTTPException: 404 if no task with `task_id` exists.

    Example:
        DELETE /tasks/3fa85f64-... -> 204
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise _not_found(task_id)
    return None
