import pytest
from click.testing import CliRunner
from uuid import uuid4
import datetime as dt
from unittest import mock

from src.cli_server.main import (
    add,
    list_tasks,
    remove,
    completed,
)

from src.models.task_model import Task


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def fake_task():
    return Task(
        title="Test Task",
        task_id=uuid4(),
        deadline=dt.date.today() + dt.timedelta(days=3),
        completed=False,
    )


@pytest.fixture
def patched_get_task_list():
    with mock.patch("src.models.task_model.get_task_list", return_value=[]):
        yield


@pytest.fixture
def patched_save_task_list():
    with mock.patch("src.models.task_model.save_task_list") as mock_save:
        yield mock_save


def test_add_task_without_deadline(
    runner, patched_get_task_list, patched_save_task_list
):
    result = runner.invoke(add, ["My task"])
    assert result.exit_code == 0
    patched_save_task_list.assert_called_once()
    assert "already in the list" not in result.output


def test_add_task_with_deadline(runner, patched_get_task_list, patched_save_task_list):
    deadline = (dt.date.today() + dt.timedelta(days=2)).isoformat()
    result = runner.invoke(add, ["New Task", "--deadline", deadline])
    assert result.exit_code == 0
    patched_save_task_list.assert_called_once()


def test_add_existing_task(runner):
    with mock.patch(
        "src.models.task_model.get_task_list", return_value=[Task(title="Existing")]
    ), mock.patch(
        "src.models.task_model.find_task_by_title", return_value=Task(title="Existing")
    ):
        result = runner.invoke(add, ["Existing"])
        assert "'Existing' already in the list." in result.output


def test_list_tasks_colors(runner, fake_task):
    tasks = [
        Task(title="Done", completed=True),
        Task(title="Late", deadline=dt.date.today() - dt.timedelta(days=1)),
        Task(title="Future", deadline=dt.date.today() + dt.timedelta(days=1)),
    ]
    with mock.patch("src.models.task_model.get_task_list", return_value=tasks), mock.patch(
        "src.models.task_model.overdue", side_effect=lambda d: d < dt.date.today()
    ):
        result = runner.invoke(list_tasks)
        assert "1. Done" in result.output
        assert "2. Late" in result.output
        assert "3. Future" in result.output


def test_remove_existing_task(runner, fake_task):
    with mock.patch(
        "src.models.task_model.get_task_list", return_value=[fake_task]
    ), mock.patch(
        "src.models.task_model.find_task_by_title", return_value=fake_task
    ), mock.patch(
        "src.models.task_model.save_task_list"
    ) as mock_save:
        result = runner.invoke(remove, [fake_task.title])
        assert result.exit_code == 0
        mock_save.assert_called_once()


def test_remove_nonexistent_task_with_match(runner):
    with mock.patch("src.models.task_model.get_task_list", return_value=[]), mock.patch(
        "src.models.task_model.find_task_by_title", return_value=None
    ), mock.patch("src.models.task_model.find_match") as mock_match, mock.patch(
        "src.models.task_model.save_task_list"
    ) as mock_save:
        result = runner.invoke(remove, ["Unknown Task"])
        mock_match.assert_called_once()
        mock_save.assert_called_once()


def test_completed_existing_task(runner, fake_task):
    with mock.patch(
        "src.models.task_model.get_task_list", return_value=[fake_task]
    ), mock.patch(
        "src.models.task_model.find_task_by_title", return_value=fake_task
    ), mock.patch(
        "src.models.task_model.save_task_list"
    ) as mock_save:
        result = runner.invoke(completed, [fake_task.title])
        assert result.exit_code == 0
        assert fake_task.completed is True
        mock_save.assert_called_once()


def test_completed_nonexistent_task(runner):
    with mock.patch("src.models.task_model.get_task_list", return_value=[]), mock.patch(
        "src.models.task_model.find_task_by_title", return_value=None
    ), mock.patch("src.models.task_model.find_match") as mock_match, mock.patch(
        "src.models.task_model.save_task_list"
    ) as mock_save:
        result = runner.invoke(completed, ["Ghost Task"])
        mock_match.assert_called_once()
        mock_save.assert_called_once()
