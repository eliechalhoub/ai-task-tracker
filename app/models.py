"""
Task Tracker data models.

Pydantic v2 only. TaskCreate/TaskUpdate are client-facing input models and
never accept id/created_at/updated_at -- those are assigned by storage.py.

Mid-course additions: due_date (Feature 1) and tags (Feature 2).
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

MAX_TAGS = 5
MAX_TAG_LENGTH = 30
_NON_NULLABLE_FIELDS = ("title", "description", "status", "priority", "tags")

class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _clean_tags(tags: list[str]) -> list[str]:
    cleaned = []
    for tag in tags:
        stripped = tag.strip()
        if not stripped:
            raise ValueError("Tags cannot be blank")
        if len(stripped) > MAX_TAG_LENGTH:
            raise ValueError(f"Each tag must be {MAX_TAG_LENGTH} characters or fewer")
        if stripped not in cleaned:
            cleaned.append(stripped)
    if len(cleaned) > MAX_TAGS:
        raise ValueError(f"A task can have at most {MAX_TAGS} tags")
    return cleaned


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and normalize the task title.

        Args:
            v (str): The raw title value.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If the stripped title is empty, or longer than 200
                characters.
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title is required and cannot be blank")
        if len(stripped) > 200:
            raise ValueError("Title must be 200 characters or fewer")
        return stripped

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize the task's tags.

        Delegates to `_clean_tags`: strips whitespace, rejects blank tags,
        rejects tags over `MAX_TAG_LENGTH` characters, de-duplicates by
        exact (case-sensitive) string match, and rejects more than
        `MAX_TAGS` tags.

        Args:
            v (list[str]): The raw tag list.

        Returns:
            list[str]: The cleaned, de-duplicated tag list.

        Raises:
            ValueError: If any tag is blank or too long, or if there are
                more than `MAX_TAGS` tags after de-duplication.
        """
        return _clean_tags(v)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_null_for_required_fields(cls, data):
        """Reject explicit `null` for non-nullable update fields.

        Runs before field-level validation. `title`, `description`,
        `status`, `priority`, and `tags` cannot be explicitly set to
        `null` in a PATCH payload -- the client must omit the field
        entirely to leave it unchanged. `assignee` and `due_date` are not
        covered by this check, so explicit `null` is allowed for them (to
        unassign / clear a due date).

        Args:
            data: The raw input data for the model, as received by
                Pydantic before field validation.

        Returns:
            The unmodified `data`, if no offending fields are present.

        Raises:
            ValueError: If any of `title`, `description`, `status`,
                `priority`, or `tags` is present in `data` with a value of
                `None`.
        """
        if isinstance(data, dict):
            offenders = [f for f in _NON_NULLABLE_FIELDS if f in data and data[f] is None]
            if offenders:
                raise ValueError(
                    f"{', '.join(offenders)} cannot be explicitly set to null; "
                    f"omit the field entirely to leave it unchanged"
                )
        return data

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and normalize an updated title.

        Only runs when `title` is explicitly supplied with a non-null
        value: explicit `null` is already rejected by
        `reject_explicit_null_for_required_fields`, and Pydantic does not
        run field validators against the unset default.

        Args:
            v (str): The raw title value.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If the stripped title is empty, or longer than 200
                characters.
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title is required and cannot be blank")
        if len(stripped) > 200:
            raise ValueError("Title must be 200 characters or fewer")
        return stripped

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate and normalize updated tags, if supplied.

        Args:
            v (Optional[list[str]]): The raw tag list, or None.

        Returns:
            Optional[list[str]]: None if `v` is None; otherwise the
                cleaned, de-duplicated tag list (see
                `TaskCreate.validate_tags` / `_clean_tags`).

        Raises:
            ValueError: If any tag is blank or too long, or if there are
                more than `MAX_TAGS` tags after de-duplication.
        """
        if v is None:
            return v
        return _clean_tags(v)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime