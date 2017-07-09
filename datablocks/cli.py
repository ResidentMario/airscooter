import click
from .orchestration import *
from .depositor import Depositor
from .transform import Transform
import os

from ast import literal_eval


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
def link(task, inputs, outputs):
    if outputs is None:
        raise ValueError("No output filenames provided.")

    _outputs = literal_eval(outputs) if outputs[0] == "[" else [outputs]
    _inputs = None if inputs is None else literal_eval(inputs) if inputs[0] == "[" else [inputs]
    task_id = task.split(".")[0]

    if inputs is None:
        # depositor
        _task = Depositor(task_id, task, _outputs)
    else:
        # transform
        pass

    if "datablocks.yml" not in os.listdir(".airflow"):
        graph = []
    else:
        graph = deserialize_from_file("./.airflow/datablocks.yml")

    # Write the update to file.
    # TODO: deal with doubled declarations (e.g. running the same command twice)
    graph.append(_task)
    serialize_to_file(graph, "./.airflow/datablocks.yml")

    click.echo(task + "\n" + str(inputs) + "\n" + str(outputs))
    click.echo(_task)

cli.add_command(init)
cli.add_command(link)
