import datetime as dt

import pytest

import src.models.task_model as app
from src.models.task_model import Task


@pytest.fixture(autouse=True)
def setup_teardown():
    print("Setup before test")
    yield
    print("Teardown after test")
    app.clear_task_list()


@pytest.fixture(name="task_list")
def task_list_fixture():
    task_list = [Task(title="pay rent"), Task(title="buy bread")]
    yield task_list


# Test clear_task_list functions
# ----------------------------------------------------------------------------

def test_clear_task_list(task_list):
    app.save_task_list(task_list)
    load_list = app.get_task_list()
    assert len(load_list) == len(task_list)
    app.clear_task_list()
    load_list = app.get_task_list()
    assert len(load_list) == 0

# Test get_task_list and save_task_list functions
# ----------------------------------------------------------------------------


def test_get_task_list(task_list):
    app.save_task_list(task_list)
    load_list = app.get_task_list()
    assert load_list == task_list


def test_get_task_list_empty():
    app.save_task_list([])
    assert app.get_task_list() == []


# Test overdue function
# ----------------------------------------------------------------------------


def test_overdue():
    assert not app.overdue(None)


def test_overdue_with_date():
    assert app.overdue(dt.date(2022, 1, 1)) is True
    assert app.overdue(dt.date.today()) is False
    assert app.overdue(dt.date(3000, 1, 1)) is False


# Test todate function
# ----------------------------------------------------------------------------


def test_to_date():
    assert app.to_date("2022-09-01") == dt.date(2022, 9, 1)


# Test to_date exception handling
def test_to_date_invalid_format():
    with pytest.raises(ValueError, match="not in YYYY-MM-DD format."):
        app.to_date("2022/09/01")


def test_to_date_invalid_value():
    with pytest.raises(ValueError, match="2022-13-01 is not in YYYY-MM-DD format."):
        app.to_date("2022-13-01")


# Test find_task_by_title function
# ----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("buy bread", Task(title="buy bread")),
        ("buy banana", None),
        ("PAY RENT", Task(title="pay rent")),
    ],
)
def test_find_task_by_title(test_input, expected, task_list):
    app.save_task_list(task_list)
    assert app.find_task_by_title(test_input) == expected


def test_find_task_by_title_empty_list():
    assert app.find_task_by_title("buy bread") is None
    assert app.find_task_by_title("pay rent") is None
    assert app.find_task_by_title("") is None


def test_find_task_by_title_no_match(task_list):
    app.save_task_list(task_list)
    assert app.find_task_by_title("pay mortgage") is None
    assert app.find_task_by_title("") is None


# Test find_match function
# ----------------------------------------------------------------------------
def test_find_match(task_list, capsys):
    app.save_task_list(task_list)
    app.find_match("buy brea")
    captured = capsys.readouterr()
    assert "Cannot find buy brea, here are the close matches." in captured.out
    assert "1. buy bread" in captured.out

    app.find_match("pay rent")
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out


def test_find_match_no_match(task_list, capsys):
    app.save_task_list(task_list)
    app.find_match("pay rent")
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out
    assert "buy bread" not in captured.out


def test_find_match_no_potential_match(task_list, capsys):
    app.save_task_list(task_list)
    app.find_match("pay rent")
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out
    assert "buy bread" not in captured.out


def test_find_match_empty_list(capsys):
    app.find_match("pay rent")
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out
    assert "buy bread" not in captured.out


def test_find_match_no_close_matches(capsys):
    single_task_list = [Task(title="pay rent")]
    app.save_task_list(single_task_list)
    app.find_match("buy bread")
    captured = capsys.readouterr()
    assert "Cannot find buy bread, here are the close matches." not in captured.out
    assert "pay rent" not in captured.out


def test_find_match_no_close_matches_empty_list(capsys):
    app.find_match("buy bread")
    captured = capsys.readouterr()
    assert "Cannot find buy bread, here are the close matches." not in captured.out
    assert "pay rent" not in captured.out


# Test add_task function
# ----------------------------------------------------------------------------

def test_add_task(task_list):
    app.save_task_list(task_list)
    app.add_task(Task(title="add another task"))
    assert len(app.get_task_list()) == len(task_list) + 1

    
# Test delete_task function
# ----------------------------------------------------------------------------

def test_add_task(task_list):
    app.save_task_list(task_list)
    app.add_task(Task(title="add another task"))
    assert len(app.get_task_list()) == len(task_list) + 1