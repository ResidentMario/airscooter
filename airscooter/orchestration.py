"""Orchestration layer."""

# import airflow
import yaml
from .transform import Transform
from .depositor import Depositor
import os
import subprocess
from datetime import datetime
import psutil


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
    Given a task graph YAML serialization, returns the list of airscooter objects (Transform and Depositor objects)
    making up this task graph.

    Parameters
    ----------
    yml_data: str, required
        The YAML representation being deserialized.

    Returns
    -------
    The resultant airscooter task list.
    """
    hash_table = dict()
    tasks = []
    for task_repr in yml_data['tasks']:
        if task_repr['type'] == 'depositor':
            task = Depositor(
                task_repr['name'],
                task_repr['filename'],
                task_repr['output'],
                dummy=task_repr['dummy']
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
    Given a task graph YAML serialization, returns the constituent list of airscooter task graph objects. I/O wrapper
    for `deserialize`.

    Parameters
    ----------
    yml_filename: str, required
        The name of the file the data will be read in from.

    Returns
    -------
    The resultant airscooter task list.
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
    # TODO: start_date corresponding with the current UTC date.
    datetime_as_str = "".join(["datetime(", str(datetime.now().year), ", ", str(datetime.now().month), ", ",
                               str(datetime.now().day), ")"])
    ret_str = """
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'start_date': -0-,
    'schedule_interval': '@once',
}

dag = DAG('airscooter_dag', default_args=default_args, schedule_interval=timedelta(1))
    """.replace("-0-", datetime_as_str)  # Avoids doubled-{} problems.

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
    Configures Airflow for use within Airscooter.

    Parameters
    ----------
    localize: bool, default True
        By default, overwrite the AIRFLOW_HOME environment variable and the values set in the airflow.cfg file to
        point at a local ".airflow" folder. This is desirable behavior for maintaining several separable DAGs on one
        machine, with each DAG corresponding with a single directory, and thus a single project or git repository
        thereof.

        If localize is set to False, airscooter will inherit the current global Airflow settings. This is the vanilla
        behavior, and may be preferable in advanced circumstances (which ones TBD).
    local_folder: str, default ".airflow"
        The name of the local folder that the DAG gets written to. Airscooter configures Airflow to work against this
        folder.
    init: bool, default False
        Whether or not to initialize the database.
    """
    if localize:
        os.environ['AIRFLOW_HOME'] = os.path.abspath("./.airflow")
        dag_folder_path = "./{0}".format(local_folder)
        if not os.path.isdir("./.airflow"):
            os.mkdir(dag_folder_path)

    if init:
        subprocess.call(["airflow", "initdb"], env=os.environ.copy())  # resetdb?


def run():
    """
    Runs a DAG.

    Parameters
    ----------
    pin, str or None, default None
        If this parameter is None, run the task with this name in the mode set by the run_mode parameter.
    run_mode, {'forward', 'backwards', 'all'}, default None
        If `pin` is None, do nothing. Otherwise, do the following. If set to 'forward', run this task and all tasks
        that come after it, stubbing out any unfulfilled requirements with dummy operators. If set to 'backwards',
        run this task and any tasks that come before, again with stubs. If set to 'all', run all dependent and
        expectant tasks, again with stubs. In this case, if this parameter is left as None, raises a ValueError.
    """
    # TODO: Use https://github.com/teamclairvoyant/airflow-rest-api-plugin
    def get_run_date():
        try:
            tasks = os.listdir("./.airflow/logs/airscooter_dag")
        except FileNotFoundError:
            return None

        sample_task = tasks[0]

        try:
            sample_task_logs = os.listdir("./.airflow/logs/airscooter_dag/" + sample_task)
        except FileNotFoundError:
            return None

        if len(sample_task_logs) == 0:
            return None
        else:
            latest_timestamp = sorted(sample_task_logs)[-1]
            return latest_timestamp

    webserver_process = subprocess.Popen(["airflow", "webserver"])
    scheduler_process = subprocess.Popen(["airflow", "scheduler"])

    try:
        # Schedule a DAG run. This command schedules a run and returns; it does not wait for the (potentially
        # threaded) process to actually complete. So we will need to wait for outputs ourselves later, before killing
        # the process itself.
        # See also https://issues.apache.org/jira/browse/AIRFLOW-43.
        subprocess.call(["airflow", "trigger_dag", "airscooter_dag"], env=os.environ.copy())

        # DAGs are added to the schedule in a paused state by default. It is possible to have them added to the
        # schedule in an unpaused state by editing the requisite config file, but I abstain from doing so in order to
        #  keep the defaults as close to the global default as possible. Instead we'll run another CLI command for
        # unpausing the graph.
        #
        # The nuance here is that the CLI returns prior to the DAG Run actually being scheduled, so unpause will have
        # no effect in the quick sequence in which it runs. I insert a 1-second sleep here as a brute-force way of
        # keeping this from happening.
        # TODO: This is a hack. There's got to be a better way of handling this.
        import time; time.sleep(1)
        subprocess.call(["airflow", "unpause", "airscooter_dag"], env=os.environ.copy())
    except:
        # If an exception was raised, proceed to killing the processes.
        pass
    else:
        # TODO: This could be improved by manipulating airflow's internal API somehow, instead of beating on the CLI.
        import time
        # If not, poll for the completion of the DAG run. Only continue when the deed is done.
        run_date = None
        while True:
            # airflow includes a command for getting the status of a DAG run. Unfortunately this command relies on
            # knowing the run date of the run. This is problematic for us because we trigger DAG runs whenever---we
            # are not *truly* using the scheduler.
            if not run_date:
                run_date = get_run_date()

            if run_date:
                status = subprocess.run(["airflow", "dag_state", "airscooter_dag", run_date],
                                        stdout=subprocess.PIPE).stdout
                run_status = status.split(b"\n")[-2]  # hacky, but necessary.
                if run_status == b'running':
                    time.sleep(1)
                else:
                    break
            else:
                time.sleep(1)

    finally:
        # TODO: Provide information on DAG run exit status.

        process = psutil.Process(webserver_process.pid)
        for proc in process.children():
            proc.kill()

        webserver_process.terminate()
        scheduler_process.terminate()
