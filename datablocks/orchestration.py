"""Orchestration layer."""

import airflow
import datetime
import yaml
from .transform import Transform
from .depositor import Depositor
import os
import subprocess

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2015, 6, 1),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}


def serialize_tasks(tasks):
    """
    Transforms a list of tasks into a YAML serialization thereof.

    Requires
    --------
    tasks: list, required
        A list of tasks.

    Returns
    -------
    yml_repr, str
        A YAML serialization thereof.
    """
    tasks_dict = [task.datafy() for task in tasks]
    yml_repr = yaml.dump({'tasks': tasks_dict})
    return yml_repr


def serialize_to_file(tasks, yml_filename):
    """
    Given a list of tasks, writes a simplified YAML serialization thereof to a file. This method enables task graph
    persistence: at the CLI level, additional tasks getting written to the graph check and write to this data to
    maintain a consistent state.

    Requires
    --------
    tasks: list, required
        A list of tasks.
    yml_filename: str, required
        The filename to which the YAML representation will be written.
    """
    yml_repr = serialize_tasks(tasks)

    with open(yml_filename, "w") as f:
        f.write(yml_repr)


def deserialize(yml_data):
    """
    Given a task graph YAML serialization, returns the list of datablocks objects (Transform and Depositor objects)
    making up this task graph.

    Parameters
    ----------
    yml_data: str, required
        The YAML representation being deserialized.

    Returns
    -------
    The resultant datablocks task list.
    """
    hash_table = dict()
    tasks = []
    for task_repr in yml_data['tasks']:
        if task_repr['type'] == 'depositor':
            task = Depositor(
                task_repr['name'],
                task_repr['filename'],
                task_repr['output']
            )
        else:
            task = Transform(
                task_repr['name'],
                task_repr['filename'],
                task_repr['input'],
                task_repr['output']
            )
        tasks.append(task)
        hash_table[task_repr['name']] = task

    for yml_repr, task in zip(yml_data['tasks'], tasks):
        if isinstance(task, Transform):
            task.requirements = [hash_table[name] for name in yml_repr['requirements']]

    return tasks


def deserialize_from_file(yml_filename):
    """
    Given a task graph YAML serialization, returns the constituent list of datablocks task graph objects. I/O wrapper
    for `deserialize`.

    Parameters
    ----------
    yml_filename: str, required
        The name of the file the data will be read in from.

    Returns
    -------
    The resultant datablocks task list.
    """
    with open(yml_filename, "r") as f:
        yml_data = yaml.load(f.read())

    return deserialize(yml_data)


def create_airflow_string(tasks):
    """
    Given a task graph (as a list of tasks), generates an Airflow DAG file.

    Parameters
    ----------
    tasks: list of {Transform, Depositor} objects, required
        The tasks constituting the task graph to be written as a DAG.

    Returns
    -------
    The Airflow DAG as a string, ready to be written to the file.
    """
    ret_str = """
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('datablocks_dag', default_args=default_args, schedule_interval=timedelta(1))
    """

    dependencies_str = ""

    for i, task in enumerate(tasks):
        ret_str += "\n\n" + task.name + " = " + task.as_airflow_string()

    for i, task in enumerate(tasks):
        if hasattr(task, "requirements"):
            for requirement in task.requirements:
                dependencies_str += "\n{0}.set_upstream({1})\n".format(task.name, requirement.name)

    ret_str = ret_str + dependencies_str
    return ret_str


def write_airflow_string(tasks, filename):
    """
    Writes the Airflow DAG file for the given tasks. I/O wrapper for `create_airflow_string`.

    Parameters
    ----------
    tasks: list of {Transform, Depositor} objects, required
        The tasks constituting the task graph to be written as a DAG.
    filename: str, required
        The filename the DAG will be written to.
    """
    with open(filename, "w") as f:
        f.write(create_airflow_string(tasks))


def configure(localize=True, local_folder=".airflow", init=False):
    """
    Configures Airflow for use within Datablocks.

    Parameters
    ----------
    localize: bool, default True
        By default, overwrite the AIRFLOW_HOME environment variable and the values set in the airflow.cfg file to
        point at a local ".airflow" folder. This is desirable behavior for maintaining several separable DAGs on one
        machine, with each DAG corresponding with a single directory, and thus a single project or git repository
        thereof.

        If localize is set to False, datablocks will inherit the current global Airflow settings. This is the vanilla
        behavior, and may be preferable in advanced circumstances (which ones TBD).
    local_folder: str, default ".airflow"
        The name of the local folder that the DAG gets written to. Datablocks configures Airflow to work against this
        folder.
    int, bool, default False
        Whether or not to initialize the database.
    """
    if localize:
        os.environ['AIRFLOW_HOME'] = os.path.abspath("./.airflow")
        print(os.path.abspath("./.airflow"))
        dag_folder_path = "./{0}".format(local_folder)
        if not os.path.isdir("./.airflow"):
            os.mkdir(dag_folder_path)

    if init:
        subprocess.call(["airflow", "initdb"], env=os.environ.copy())  # resetdb?


def run(dag_id):
    subprocess.call(["airflow", "trigger_dag", dag_id])
