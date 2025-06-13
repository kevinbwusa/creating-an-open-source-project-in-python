import datetime as dt
import json
from dataclasses import dataclass
from difflib import SequenceMatcher as SM
from typing import List, Optional

import click

TASK_FILE = "reminder.json"


@dataclass
class Task:
    name: str = ""
    deadline: Optional[dt.date] = None
    done: bool = False

    def to_dict(self):
        return {
            "name": self.name,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "done": self.done,
        }

    @staticmethod
    def from_dict(data):
        return Task(
            name=data["name"],
            deadline=(
                dt.date.fromisoformat(data["deadline"]) if data["deadline"] else None
            ),
            done=data["done"],
        )


def _get_task_list() -> List[Task]:
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_task_list(task_list: List[Task]) -> None:
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump([task.to_dict() for task in task_list], f, indent=4)


def _overdue(deadline: Optional[dt.date]) -> bool:
    return deadline is not None and deadline < dt.date.today()


def _to_date(deadline: str) -> dt.date:
    try:
        return dt.date.fromisoformat(deadline)
    except ValueError:
        raise ValueError(f"{deadline} is not in YYYY-MM-DD format.") from None


def _find_task(target: str, task_list: List[Task]) -> Optional[Task]:
    for task in task_list:
        if target.lower() == task.name.lower():
            return task
    return None


def _find_match(target: str, task_list: List[Task]):
    potential_match = []
    for task in task_list:
        score = SM(None, target, task.name).ratio()
        if score >= 0.9:
            potential_match.append((score, task.name))
    if potential_match:
        potential_match = sorted(potential_match, key=lambda x: x[0], reverse=True)
        if (
            len(potential_match) == 1
            and potential_match[0][0] >= 0.9
            and potential_match[0][1].lower() == target.lower()
        ):
            click.echo(f"'{target}' found in the list.")
            return

        click.echo(f"Cannot find {target}, here are the close matches.")
        for num, match in enumerate(potential_match):
            click.echo(f"{num + 1}. {match[1]}")


@click.group()
def app():
    pass


@click.command()
@click.option("--deadline", default=None, help="Enter date in YYYY-MM-DD format.")
@click.argument("task")
def add(task: str, deadline: str):
    """Add a task in reminders."""
    task_list = _get_task_list()
    target = _find_task(task, task_list)
    if target is not None:
        click.echo(f"'{task}' already in the list.")
        return
    if deadline is None:
        task_list.append(Task(task))
    else:
        task_list.append(Task(task, _to_date(deadline)))
    _save_task_list(task_list)


@click.command(name="list")
def list_tasks():
    """List all the task in reminders."""
    task_list = _get_task_list()
    for num, task in enumerate(task_list):
        if task.done:
            click.secho(f"{num + 1}. {task.name}", fg="green")
        elif _overdue(task.deadline):
            click.secho(f"{num + 1}. {task.name}", fg="red")
        else:
            click.echo(f"{num + 1}. {task.name}")


@click.command()
@click.argument("task")
def remove(task: str):
    """Remove a task in reminders."""
    task_list = _get_task_list()
    target = _find_task(task, task_list)
    if target is not None:
        task_list.remove(target)
    else:
        _find_match(task, task_list)
    _save_task_list(task_list)


@click.command()
@click.argument("task")
def done(task: str):
    """Mark a task as done in reminders."""
    task_list = _get_task_list()
    target = _find_task(task, task_list)
    if target is not None:
        target.done = True
    else:
        _find_match(task, task_list)
    _save_task_list(task_list)


app.add_command(add)
app.add_command(list_tasks)
app.add_command(remove)
app.add_command(done)

if __name__ == "__main__":
    app()
