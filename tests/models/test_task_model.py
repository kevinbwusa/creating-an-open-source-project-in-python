import datetime as dt
import json
import os
import tempfile
from uuid import uuid4
from unittest.mock import patch, mock_open

# While very similar to mocking, patching is more about replacing the actual implementation of a function or object with a mock, rather than creating a fake object.

import pytest

from src.models.task_model import (
    Task,
    to_date,
    overdue,
    get_task_list,
    save_task_list,
    clear_task_list,
    get_task_by_task_id,
    find_task_by_title,
    add_task,
    delete_task,
    update_task,
    mark_task_completed,
    mark_task_incomplete,
)


@pytest.fixture(name="sample_task")
def sample_task_fixture():
    return Task(
        title="Sample Task",
        description="Description",
        deadline=dt.date.today(),
        completed=False,
    )


def test_task_equality():
    t1 = Task(title="A", description="B", deadline=dt.date.today())
    t2 = Task(title="A", description="B", deadline=t1.deadline)
    assert t1 == t2
    assert not (t1 != t2)


def test_to_dict_and_from_dict(sample_task):
    d = sample_task.to_dict()
    t2 = Task.from_dict({
        "task_id": str(sample_task.task_id),
        "title": sample_task.title,
        "description": sample_task.description,
        "deadline": sample_task.deadline.isoformat(),
        "completed": sample_task.completed
    })
    assert sample_task == t2
    assert isinstance(t2, Task)


def test_to_date_valid():
    assert to_date("2023-12-31") == dt.date(2023, 12, 31)


def test_to_date_none_string():
    assert to_date("None") is None


def test_to_date_invalid():
    with pytest.raises(ValueError):
        to_date("31-12-2023")


def test_overdue():
    assert overdue(dt.date.today() - dt.timedelta(days=1)) is True
    assert overdue(dt.date.today() + dt.timedelta(days=1)) is False
    assert overdue(None) is False


def test_save_and_get_task_list(tmp_path):
    test_file = tmp_path / "test_tasks.json"
    tasks = [Task(title="Task 1")]
    with patch("src.models.task_model.TASK_FILE", str(test_file)):
        save_task_list(tasks)
        loaded = get_task_list()
        assert len(loaded) == 1
        assert loaded[0].title == "Task 1"


def test_clear_task_list(tmp_path):
    test_file = tmp_path / "test_tasks.json"
    with patch("src.models.task_model.TASK_FILE", str(test_file)):
        save_task_list([Task(title="X")])
        clear_task_list()
        assert get_task_list() == []


def test_get_task_by_task_id(tmp_path):
    task = Task(title="FindMe")
    with patch("src.models.task_model.TASK_FILE", tmp_path / "test.json"):
        save_task_list([task])
        found = get_task_by_task_id(task.task_id)
        assert found and found.title == "FindMe"


def test_find_task_by_title(tmp_path):
    task = Task(title="DoLaundry")
    with patch("src.models.task_model.TASK_FILE", tmp_path / "x.json"):
        save_task_list([task])
        found = find_task_by_title("DoLaundry")
        assert found is not None
        assert found.title == "DoLaundry"


def test_add_task(tmp_path):
    task = Task(title="UniqueTask")
    with patch("src.models.task_model.TASK_FILE", tmp_path / "add.json"):
        add_task(task)
        loaded = get_task_list()
        assert any(t.title == "UniqueTask" for t in loaded)


def test_add_duplicate_task(tmp_path):
    task = Task(title="Dup")
    with patch("src.models.task_model.TASK_FILE", tmp_path / "dup.json"):
        add_task(task)
        with pytest.raises(ValueError):
            add_task(task)


def test_delete_task(tmp_path):
    task = Task(title="ToDelete")
    with patch("src.models.task_model.TASK_FILE", tmp_path / "del.json"):
        save_task_list([task])
        delete_task(task.task_id)
        assert get_task_list() == []


def test_delete_task_not_found(tmp_path):
    with patch("src.models.task_model.TASK_FILE", tmp_path / "bad.json"):
        with pytest.raises(ValueError):
            delete_task(uuid4())


def test_update_task(tmp_path):
    task = Task(title="Old")
    new_task = Task(title="New", task_id=task.task_id)
    with patch("src.models.task_model.TASK_FILE", tmp_path / "upd.json"):
        save_task_list([task])
        update_task(task.task_id, new_task)
        updated = get_task_by_task_id(task.task_id)
        assert updated and updated.title == "New"


def test_update_task_not_found(tmp_path):
    task = Task(title="Nothing")
    with patch("src.models.task_model.TASK_FILE", tmp_path / "notfound.json"):
        with pytest.raises(ValueError):
            update_task(uuid4(), task)


def test_mark_task_completed(tmp_path):
    task = Task(title="Comp")
    with patch("src.models.task_model.TASK_FILE", tmp_path / "complete.json"):
        save_task_list([task])
        mark_task_completed(task.task_id)
        t = get_task_by_task_id(task.task_id)
        assert t and t.completed is True


def test_mark_task_incomplete(tmp_path):
    task = Task(title="Incomp", completed=True)
    with patch("src.models.task_model.TASK_FILE", tmp_path / "incomp.json"):
        save_task_list([task])
        mark_task_incomplete(task.task_id)
        t = get_task_by_task_id(task.task_id)
        assert t and t.completed is False
