import datetime as dt
import json
from difflib import SequenceMatcher as SM
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

TASK_FILE = "reminder.json"


# @dataclass
class Task(BaseModel):
    """Defines the shape of a task model"""

    title: str = ""
    id: Optional[UUID] = uuid4()
    deadline: Optional[dt.date] = None
    description: Optional[str] = None
    completed: bool = False

    def __str__(self):
        return f"Task(title={self.title}, id={self.id}, deadline={self.
            deadline}, description={self.description}, completed={self.completed})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # Ignore the id field when comparing two Task objects
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
        return hash(self.id)

    def to_dict(self):
        return {
            "title": self.title,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completed": self.completed,
        }

    @staticmethod
    def from_dict(data):
        task = Task(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            title=data.get("title"),
            description=data.get("description"),
            deadline=(
                dt.date.fromisoformat(data["deadline"]) if data["deadline"] else None
            ),
            completed=data.get("completed", False),
        )
        return task


tasks = list[Task]()


def get_task_list() -> List[Task]:
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_task_list(task_list: List[Task]) -> None:
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump([task.to_dict() for task in task_list], f, indent=4)


def overdue(deadline: Optional[dt.date]) -> bool:
    return deadline is not None and deadline < dt.date.today()


def to_date(deadline: str) -> dt.date:
    try:
        return dt.date.fromisoformat(deadline)
    except ValueError:
        raise ValueError(f"{deadline} is not in YYYY-MM-DD format.") from None


def find_task(target: str, task_list: List[Task]) -> Optional[Task]:
    for task in task_list:
        if target.lower() == task.title.lower():
            return task
    return None


def find_match(target: str, task_list: List[Task]):
    potential_match = []
    for task in task_list:
        score = SM(None, target, task.title).ratio()
        if score >= 0.9:
            potential_match.append((score, task.title))
    if potential_match:
        potential_match = sorted(potential_match, key=lambda x: x[0], reverse=True)
        if (
            len(potential_match) == 1
            and potential_match[0][0] >= 0.9
            and potential_match[0][1].lower() == target.lower()
        ):
            print(f"'{target}' found in the list.")
            return

        print(f"Cannot find {target}, here are the close matches.")
        for num, match in enumerate(potential_match):
            print(f"{num + 1}. {match[1]}")
