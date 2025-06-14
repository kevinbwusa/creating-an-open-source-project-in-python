"""Implements endpoints for the Task API"""

from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from fastapi_server.models.task import Task, add_task, get_task_by_key, get_task_list

DEFAULT_ENDPOINT_TAGS = ["TASK"]

router = APIRouter()


# FastAPI routes definitions for CRUD operations
@router.get("/tasks/", response_model=List[Task])
def read_tasks():
    """REST/API to return the list of tasks."""
    return get_task_list()


@router.post("/tasks/", response_model=Task)
def create_task(task: Task):
    """REST/API to create a new task and add it to the list of tasks."""
    task.task_id = uuid4()
    add_task(task)
    return task


@router.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: UUID):
    """REST/API to return a specific task from the list of tasks."""
    found = get_task_by_key(task_id)
    if found:
        return found

    raise HTTPException(status_code=404, detail="Task not found")


@router.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, task_update: Task):
    """REST/API to update a specific task found the list of tasks."""
    task_list = get_task_list()
    # Find the task by its ID and update it
    if not task_list:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task_update:
        raise HTTPException(status_code=400, detail="No update data provided")
    if task_id is None:
        raise HTTPException(status_code=400, detail="Task ID is required")
    if task_update.task_id is not None and task_update.task_id != task_id:
        raise HTTPException(
            status_code=400,
            detail="Task ID in the body does not match the URL parameter",
        )
    for idx, task in enumerate(task_list):
        if task.task_id == task_id:
            updated_task = task.model_copy(
                update=task_update.model_dump(exclude_unset=True)
            )
            task_list[idx] = updated_task
            return updated_task

    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: UUID):
    """REST/API to remove a specific task from the list of tasks."""
    try:
        delete_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
