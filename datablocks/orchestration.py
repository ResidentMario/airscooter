import airflow
import datetime
import yaml
from .transform import Transform
from .depositor import Depositor


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
    tasks_yml = [task.datafy() for task in tasks]
    yml_repr = yaml.dump({'tasks': tasks_yml})
    return yml_repr


def write_yml(tasks, yml_filename):
    yml_repr = serialize_tasks(tasks)

    with open(yml_filename, "w") as f:
        f.write(yml_repr)


def reconstitute_objects(yml_data):
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


def reconstitute_objects_from_file(yml_filename):
    with open(yml_filename, "r") as f:
        yml_data = yaml.load(f.read())

    return reconstitute_objects(yml_data)


def create_airflow_string(tasks):
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

dag = DAG('tutorial_2', default_args=default_args, schedule_interval=timedelta(1))
    """

    dependencies_str = ""
    # tasks_hash_table = dict()

    for i, task in enumerate(tasks):
        ret_str += "\n\n" + task.name + " = " + task.as_airflow_string()
        # tasks_hash_table[task.name] = task

    for i, task in enumerate(tasks):
        if hasattr(task, "requirements"):
            for requirement in task.requirements:
                dependencies_str += "\n{0}.set_upstream({1})\n".format(task.name, requirement.name)

    ret_str = ret_str + dependencies_str
    return ret_str

# def create_dag(depositors=None, transforms=None):
#     """
#     Creates a DAG by composing inputted elements.
#     """
#     depositors = [] if depositors is None else depositors
#     transforms = [] if transforms is None else transforms
#
#     # Initialize the DAG.
#     dag = airflow.DAG('my_task', default_args=default_args)
#
#     # Create operations.
#     import pdb; pdb.set_trace()
#     # depositor_ops = [depositor.opify() for depositor in depositors]
#     # transform_ops = [transform.opify() for transform in transforms]
#     # transform_requirements = [transform.requirements for transform in transforms]
#
#     # Link operations.
#     for transform in transforms:
#         tasks = create_links(transform, dag)
#
#     # Add tasks to the graph.
#     # TODO: This raises a depracataion warning because we are adding a task to the graph multiple times.
#     # Investigate doing this a better way.
#     for task in tasks:
#         dag.add_task(task)
#
#     return dag
#
#
# def create_links(transform, dag):
#     """
#     Recursively create the job links.
#     """
#     # TODO
#     if transform.requirements:
#         ops = []
#         this_op = transform.opify(dag)
#         ops.append(this_op)
#         for prior_transform in transform.requirements:
#             ops += create_links(prior_transform, dag)
#             prior_op = prior_transform.opify(dag)
#             this_op.set_upstream(prior_op)
#         return ops
#     else:
#         return [transform.opify(dag)]
#
#
# def run(dag):
#     # TODO: https://airflow.incubator.apache.org/code.html?highlight=dag_run#airflow.operators.TriggerDagRunOperator
#     pass