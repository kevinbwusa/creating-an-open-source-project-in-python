import reminder as app
from reminder import Task

import datetime as dt

import pytest


@pytest.fixture
def task_list():
    return [Task(name="pay rent"), Task(name="buy bread")]


# Test _save_task_list and _get_task_list functions
# ----------------------------------------------------------------------------


def test_get_task_list(task_list):
    app._save_task_list(task_list)
    load_list = app._get_task_list()
    assert load_list == task_list


def test_get_task_list_empty():
    app._save_task_list([])
    assert app._get_task_list() == []


# Test _overdue function
# ----------------------------------------------------------------------------


def test_overdue():
    assert not app._overdue(None)


def test_overdue_with_date():
    assert app._overdue(dt.date(2022, 1, 1)) is True
    assert app._overdue(dt.date.today()) is False
    assert app._overdue(dt.date(3000, 1, 1)) is False


# Test _todate function
# ----------------------------------------------------------------------------


def test_to_date():
    assert app._to_date("2022-09-01") == dt.date(2022, 9, 1)


# Test _to_date exception handling
def test_to_date_invalid_format():
    with pytest.raises(ValueError, match="not in YYYY-MM-DD format."):
        app._to_date("2022/09/01")


def test_to_date_invalid_value():
    with pytest.raises(ValueError, match="2022-13-01 is not in YYYY-MM-DD format."):
        app._to_date("2022-13-01")


# Test _find_task function
# ----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("buy bread", Task(name="buy bread")),
        ("buy banana", None),
        ("PAY RENT", Task(name="pay rent")),
    ],
)
def test_find_task(test_input, expected, task_list):
    assert app._find_task(test_input, task_list) == expected


def test_find_task_empty_list():
    assert app._find_task("buy bread", []) is None
    assert app._find_task("pay rent", []) is None
    assert app._find_task("", []) is None


def test_find_task_no_match(task_list):
    assert app._find_task("pay mortgage", task_list) is None
    assert app._find_task("", task_list) is None


# Test _find_match function
# ----------------------------------------------------------------------------
def test_find_match(task_list, capsys):
    app._find_match("buy brea", task_list)
    captured = capsys.readouterr()
    assert "Cannot find buy brea, here are the close matches." in captured.out
    assert "1. buy bread" in captured.out

    app._find_match("pay rent", task_list)
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out


def test_find_match_no_match(task_list, capsys):
    app._find_match("pay rent", task_list)
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out
    assert "buy bread" not in captured.out


def test_find_match_no_potential_match(task_list, capsys):
    app._find_match("pay rent", task_list)
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out
    assert "buy bread" not in captured.out


def test_find_match_empty_list(capsys):
    app._find_match("pay rent", [])
    captured = capsys.readouterr()
    assert "Cannot find pay rent, here are the close matches." not in captured.out
    assert "buy bread" not in captured.out


def test_find_match_no_close_matches(capsys):
    task_list = [Task(name="pay rent")]
    app._find_match("buy bread", task_list)
    captured = capsys.readouterr()
    assert "Cannot find buy bread, here are the close matches." not in captured.out
    assert "pay rent" not in captured.out


def test_find_match_no_close_matches_empty_list(capsys):
    app._find_match("buy bread", [])
    captured = capsys.readouterr()
    assert "Cannot find buy bread, here are the close matches." not in captured.out
    assert "pay rent" not in captured.out
