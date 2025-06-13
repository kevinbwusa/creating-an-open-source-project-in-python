"""Module providing a demonstration of the FastAPI."""

from typing import List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException

from src.main.reminder import Task, tasks

app = FastAPI()


# FastAPI routes definitions for CRUD operations
@app.get("/tasks/", response_model=List[Task])
def read_tasks():
    """REST/API to return the list of tasks."""
    return tasks


@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    """REST/API to create a new task and add it to the list of tasks."""
    task.id = uuid4()
    tasks.append(task)
    return task


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: UUID):
    """REST/API to return a specific task from the list of tasks."""
    for task in tasks:
        if task.id == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, task_update: Task):
    """REST/API to update a specific task found the list of tasks."""
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.model_copy(
                update=task_update.model_dump(exclude_unset=True)
            )
            tasks[idx] = updated_task
            return updated_task

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: UUID):
    """REST/API to remove a specific task from the list of tasks."""
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(idx)

    raise HTTPException(status_code=404, detail="Task not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
