import click

import src.reminder as app
from src.reminder import Task

# import uvicorn
# from src.main import fastapi


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
    target = app.find_task(title, task_list)
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
    target = app.find_task(task, task_list)
    if target is not None:
        task_list.remove(target)
    else:
        app.find_match(task, task_list)
    app.save_task_list(task_list)


@click.command()
@click.argument("task")
def completed(task: str):
    """Mark a task as completed in reminders."""
    task_list = app.get_task_list()
    target = app.find_task(task, task_list)
    if target is not None:
        target.completed = True
    else:
        app.find_match(task, task_list)
    app.save_task_list(task_list)


def add_cli(cli_app):
    cli_app.add_command(add)
    cli_app.add_command(list_tasks)
    cli_app.add_command(remove)
    cli_app.add_command(completed)
    return cli_app


if __name__ == "__main__":
    cli = add_cli(cli)
    cli()
    # uvicorn.run(fastapi.app, host="0.0.0.0", port=8000)
