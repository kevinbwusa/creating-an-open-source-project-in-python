"""Implement the Task Model"""

import datetime as dt
import json
from difflib import SequenceMatcher as SM
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

TASK_FILE = "reminder.json"


class Task(BaseModel):
    """Defines the shape of a task model"""

    title: str = ""
    task_id: UUID = uuid4()
    deadline: Optional[dt.date] = None
    description: Optional[str] = None
    completed: bool = False

    def __str__(self):
        return f"Task(title={self.title}, task_id={self.task_id}, deadline={self.
            deadline}, description={self.description}, completed={self.completed})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # Ignore the task_id field when comparing two Task objects
        if not isinstance(other, Task):
            return False
        return (
            self.title == other.title
            and self.description == other.description
            and self.deadline == other.deadline
            and self.completed == other.completed
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.task_id)

    def to_dict(self):
        """Provide customized access to this object as a dictionary"""
        return {
            "task_id": str(self.task_id),
            "title": self.title,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completed": self.completed,
        }

    @staticmethod
    def from_dict(data):
        """Provide convertions from dictionary to task object"""
        task = Task(
            task_id=UUID(data["task_id"]) if "task_id" in data else uuid4(),
            title=data.get("title"),
            description=data.get("description"),
            deadline=(
                dt.date.fromisoformat(data["deadline"]) if data["deadline"] else None
            ),
            completed=data.get("completed", False),
        )
        return task


def clear_task_list() -> None:
    """Clears the list of tasks."""
    save_task_list([])
    print("Task list cleared.")


def get_task_list() -> List[Task]:
    """Returns the list of tasks from the JSON file.
    If the file does not exist, returns an empty list."""
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_task_by_task_id(task_id: UUID) -> Optional[Task]:
    """Returns the task with the given task id, or None if not found."""
    for task in get_task_list():
        if task.task_id == task_id:
            return task
    return None


def save_task_list(new_task_list: List[Task]) -> None:
    """Saves the list of tasks to the JSON file."""
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        new_task_dict = [task.to_dict() for task in new_task_list]
        json.dump(new_task_dict, f, indent=4)


def overdue(deadline: Optional[dt.date]) -> bool:
    """Returns True if the deadline is in the past, False otherwise."""
    if deadline is None:
        return False
    return deadline < dt.date.today()


def to_date(deadline: str) -> dt.date | None:
    """Converts a string in YYYY-MM-DD format to a datetime.date object."""
    if not deadline:
        raise ValueError("Deadline cannot be empty.")
    if deadline.lower() == "none":
        return None
    try:
        return dt.date.fromisoformat(deadline)
    except ValueError:
        raise ValueError(f"{deadline} is not in YYYY-MM-DD format.") from None


def find_task_by_title(title: str) -> Optional[Task]:
    """Returns the task with the given title, or None if not found."""
    for task in get_task_list():
        if title.lower() == task.title.lower():
            return task
    return None


def find_match(title: str) -> None:
    """Finds and prints tasks that match the given title."""
    potential_match = []
    for task in get_task_list():
        score = SM(None, title, task.title).ratio()
        if score >= 0.9:
            potential_match.append((score, task.title))
    if potential_match:
        potential_match = sorted(potential_match, key=lambda x: x[0], reverse=True)
        if (
            len(potential_match) == 1
            and potential_match[0][0] >= 0.9
            and potential_match[0][1].lower() == title.lower()
        ):
            print(f"'{title}' found in the list.")
            return

        print(f"Cannot find {title}, here are the close matches.")
        for num, match in enumerate(potential_match):
            print(f"{num + 1}. {match[1]}")


def add_task(task: Task) -> None:
    """Adds a new task to the list of tasks."""
    if find_task_by_title(task.title):
        raise ValueError(f"Task with title '{task.title}' already exists.")
    task_list = get_task_list()
    task_list.append(task)
    save_task_list(task_list)
    print(f"Task '{task.title}' added.")


def delete_task(task_id: UUID) -> None:
    """Deletes the task with the given title."""
    task_list = get_task_list()
    for idx, task in enumerate(task_list):
        if task_id == task.task_id:
            deleted_task = task_list.pop(idx)
            save_task_list(task_list)
            print(f"Task '{deleted_task.task_id}' deleted.")
            return
    raise ValueError(f"Task with id '{task_id}' not found.")


def update_task(task_id: UUID, new_task: Task) -> None:
    """Updates the task with the given title."""
    task_list = get_task_list()
    for idx, task in enumerate(task_list):
        if task_id == task.task_id:
            updated_task = new_task.model_copy(
                update=new_task.model_dump(exclude_unset=True)
            )
            task_list[idx] = updated_task
            save_task_list(task_list)
            print(f"Task '{task_id}' updated.")
            return
    raise ValueError(f"Task with id '{task_id}' not found.")


def list_tasks() -> None:
    """Lists all tasks."""
    task_list = get_task_list()
    if not task_list:
        print("No tasks found.")
        return
    for task in task_list:
        print(
            f"Task ID: {task.task_id}, Title: {task.title}, Deadline: {task.
                deadline}, Completed: {task.completed}"
        )


def list_overdue_tasks() -> None:
    """Lists all overdue tasks."""
    task_list = get_task_list()
    overdue_tasks = [task for task in task_list if overdue(task.deadline)]
    if not overdue_tasks:
        print("No overdue tasks found.")
        return
    for task in overdue_tasks:
        print(
            f"Task ID: {task.task_id}, Title: {task.title}, Deadline: {task.
                deadline}, Completed: {task.completed}"
        )


def list_completed_tasks() -> None:
    """Lists all completed tasks."""
    task_list = get_task_list()
    completed_tasks = [task for task in task_list if task.completed]
    if not completed_tasks:
        print("No completed tasks found.")
        return
    for task in completed_tasks:
        print(
            f"Task ID: {task.task_id}, Title: {task.title}, Deadline: {task.
                deadline}, Completed: {task.completed}"
        )


def list_incomplete_tasks() -> None:
    """Lists all incomplete tasks."""
    task_list = get_task_list()
    incomplete_tasks = [task for task in task_list if not task.completed]
    if not incomplete_tasks:
        print("No incomplete tasks found.")
        return
    for task in incomplete_tasks:
        print(
            f"Task ID: {task.task_id}, Title: {task.title}, Deadline: {task.
                deadline}, Completed: {task.completed}"
        )


def mark_task_completed(task_id: UUID) -> None:
    """Marks the task with the given title as completed."""
    task_list = get_task_list()
    for idx, task in enumerate(task_list):
        if task_id == task.task_id:
            task_list[idx].completed = True
            save_task_list(task_list)
            print(f"Task '{task_id}' marked as completed.")
            return
    raise ValueError(f"Task with id '{task_id}' not found.")


def mark_task_incomplete(task_id: UUID) -> None:
    """Marks the task with the given title as incomplete."""
    task_list = get_task_list()
    for idx, task in enumerate(task_list):
        if task_id == task.task_id:
            task_list[idx].completed = False
            save_task_list(task_list)
            print(f"Task '{task_id}' marked as incomplete.")
            return
    raise ValueError(f"Task with id '{task_id}' not found.")


def print_task(task: Task) -> None:
    """Prints the details of a task."""
    print(f"Task ID: {task.task_id}")
    print(f"Title: {task.title}")
    print(f"Deadline: {task.deadline}")
    print(f"Description: {task.description}")
    print(f"Completed: {task.completed}")


def print_task_list(task_list: List[Task]) -> None:
    """Prints the details of a list of tasks."""
    for task in task_list:
        print_task(task)
        print("-" * 20)


def print_help() -> None:
    """Prints the help message."""
    help_message = """
    Commands:
    add <title> [--deadline <YYYY-MM-DD>] [--description <description>] - Adds 
        a new task
    delete <task_id> - Deletes a task
    update <task_id> [--title <title>] [--deadline <YYYY-MM-DD>] 
        [--description <description>] [--completed <True|False>] - Updates a 
        task
    list - Lists all tasks
    list overdue - Lists all overdue tasks
    list completed - Lists all completed tasks
    list incomplete - Lists all incomplete tasks
    complete <task_id> - Marks a task as completed
    incomplete <task_id> - Marks a task as incomplete
    clear - Clears the task list
    help - Prints this help message
    """
    print(help_message)
