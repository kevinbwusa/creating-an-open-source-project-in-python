"""Command-line interface"""

import os
import sys

import click

# Import or define the app object
import models.task as app

# Now you can import modules from the current directory
from models.task import Task

home = os.environ["HOME"]
print(f"Home directory is {home}", file=sys.stderr)

# Add the parent directory to sys.path to ensure 'reminder' can be imported
top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Top directory is {top_dir}", file=sys.stderr)
sys.path.append(top_dir)


@click.group()
def cli():
    """FastAPI CLI for running and managing the application."""


@cli.command()
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload")
def runserver():
    """Run the FastAPI server."""
    # Logic to run your FastAPI app with or without reload
    # uvicorn.run(fastapi.app, host="0.0.0.0", port=8000)


@click.command()
@click.option("--deadline", default=None, help="Enter date in YYYY-MM-DD format.")
@click.argument("task")
def add(title: str, deadline: str):
    """Add a task in reminders."""
    task_list = app.get_task_list()
    target = app.find_task_by_title(title)
    if target is not None:

        click.echo(f"'{title}' already in the list.")
        return
    if deadline is None:
        task_list.append(Task(title=title))
    else:
        task_list.append(Task(title=title, deadline=app.to_date(deadline)))
    app.save_task_list(task_list)


@click.command(name="list")
def list_tasks():
    """List all the task in reminders."""
    task_list = app.get_task_list()
    for num, task in enumerate(task_list):
        if task.completed:
            click.secho(f"{num + 1}. {task.title}", fg="green")
        elif app.overdue(task.deadline):
            click.secho(f"{num + 1}. {task.title}", fg="red")
        else:
            click.echo(f"{num + 1}. {task.title}")


@click.command()
@click.argument("task")
def remove(task: str):
    """Remove a task in reminders."""
    task_list = app.get_task_list()
    target = app.find_task_by_title(task)
    if target is not None:
        task_list.remove(target)
    else:
        app.find_match(task)
    app.save_task_list(task_list)


@click.command()
@click.argument("task")
def completed(task: str):
    """Mark a task as completed in reminders."""
    task_list = app.get_task_list()
    target = app.find_task_by_title(task)
    if target is not None:
        target.completed = True
    else:
        app.find_match(task)
    app.save_task_list(task_list)


def add_cli(cli_app):
    """Add the list of commands to the command-line parser"""
    cli_app.add_command(add)
    cli_app.add_command(list_tasks)
    cli_app.add_command(remove)
    cli_app.add_command(completed)
    return cli_app


if __name__ == "__main__":
    cli = add_cli(cli)
    cli()
    # uvicorn.run(fastapi.app, host="0.0.0.0", port=8000)
