import airflow
import datetime


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


def create_dag(depositors=None, transforms=None):
    """
    Creates a DAG by composing inputted elements.
    """
    depositors = [] if depositors is None else depositors
    transforms = [] if transforms is None else transforms

    # Initialize the DAG.
    dag = airflow.DAG('my_task', default_args=default_args)

    # Create operations.
    import pdb; pdb.set_trace()
    # depositor_ops = [depositor.opify() for depositor in depositors]
    # transform_ops = [transform.opify() for transform in transforms]
    # transform_requirements = [transform.requirements for transform in transforms]

    # Link operations.
    for transform in transforms:
        tasks = create_links(transform, dag)

    # Add tasks to the graph.
    # TODO: This raises a depracataion warning because we are adding a task to the graph multiple times.
    # Investigate doing this a better way.
    for task in tasks:
        dag.add_task(task)

    return dag


def create_links(transform, dag):
    """
    Recursively create the job links.
    """
    # TODO
    if transform.requirements:
        ops = []
        this_op = transform.opify(dag)
        ops.append(this_op)
        for prior_transform in transform.requirements:
            ops += create_links(prior_transform, dag)
            prior_op = prior_transform.opify(dag)
            this_op.set_upstream(prior_op)
        return ops
    else:
        return [transform.opify(dag)]


def run(dag):
    # TODO: https://airflow.incubator.apache.org/code.html?highlight=dag_run#airflow.operators.TriggerDagRunOperator
    pass