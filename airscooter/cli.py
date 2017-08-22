import click
from .orchestration import configure, deserialize_from_file, serialize_to_file, write_airflow_string
from .orchestration import run as orchestrate_run
from .depositor import Depositor
from .transform import Transform
import os
import itertools
from pathlib import Path

from pkg_resources import iter_entry_points
from click_plugins import with_plugins

from ast import literal_eval


@with_plugins(iter_entry_points('airscooter.cli_plugins'))
@click.group()
def cli():
    pass


@click.command()
def init():
    configure(init=True)
    click.echo('Initialized the database')


@click.command()
def reset():
    configure()
    click.echo('Reset the database')


@click.command()
@click.argument('task')
@click.option('--inputs', help='A filename or list of filenames for data being inputted.')
@click.option('--outputs', help='A filename or list of filenames for data being outputted.')
@click.option('--dummy/--no-dummy', default=False, help='Initialize the new task as a no-op dummy.')
def link(task, inputs, outputs, dummy):
    if outputs is None:
        raise ValueError("No output filenames provided.")

    def restringify(inp):
        """Click automatically strips out escape characters on input, we need to add them back manually."""
        return inp.replace("[", "[\"").replace("]", "\"]").replace(" ", "").replace(",", "\", \"")

    _outputs = literal_eval(restringify(outputs)) if outputs[0] == "[" else [outputs]
    _inputs = None if inputs is None else literal_eval(restringify(inputs)) if inputs[0] == "[" else [inputs]
    task_id = task.split(".")[0]
    is_transform = inputs is not None
    is_dummy = dummy is not False

    # Transform potential relative paths to absolute ones.
    _outputs = [str(Path(out).resolve()) for out in _outputs]
    _inputs = [str(Path(inp).resolve()) for inp in _inputs] if _inputs else None

    if is_transform:
        _task = Transform(task_id, task, _inputs, _outputs, requirements=[], dummy=is_dummy)
    else:  # is_depositor
        _task = Depositor(task_id, task, _outputs, dummy=is_dummy)

    if "airscooter.yml" not in os.listdir(".airflow"):
        graph = []
    else:
        graph = deserialize_from_file("./.airflow/airscooter.yml")

    # Before writing to file, check to make sure that this task is not already in the graph.
    if _task.name not in [task.name for task in graph]:
        # In the case of a transform, we need to assign requirements manually before serialization.
        if is_transform:
            existing_outputs = list(itertools.chain(*[task.output for task in graph]))
            # Is this input already an output of some process in task graph?
            # Add it as a requirement if yes, raise if no.
            for input in _inputs:
                try:
                    output_index = existing_outputs.index(input)
                    _task.requirements.append(graph[output_index])
                except ValueError:
                    raise ValueError("This task depends on files that are not yet in the task graph.")

        graph.append(_task)
    else:
        raise ValueError("The given script is already included in the task graph.")

    serialize_to_file(graph, "./.airflow/airscooter.yml")

    if not os.path.exists("./.airflow/dags/"):
        os.mkdir("./.airflow/dags/")
    write_airflow_string(graph, "./.airflow/dags/airscooter_dag.py")

    # click.echo(task + "\n" + str(inputs) + "\n" + str(outputs))
    # click.echo(_task)


@click.command()
@click.argument('starting_task', required=False)
def run(starting_task):

    if starting_task:
        raise NotImplementedError("Subgraph runs has not been implemented yet.")

    configure(init=False)
    orchestrate_run()


cli.add_command(init)
cli.add_command(reset)
cli.add_command(link)
cli.add_command(run)