import airflow


def create_dag(depositors=None, transforms=None):
    """
    Creates a DAG by composing inputted elements.
    """
    depositors = depositors if depositors is None else []
    transforms = transforms if transforms is None else []

    # Initialize the DAG.
    dag = airflow.DAG('my_task')

    # Create operations.
    depositor_ops = [depositor.opify() for depositor in depositors]
    transform_ops = [transform.opify() for transform in transforms]
    transform_requirements = [transform.requirements for transform in transforms]

    # Link operations.



    pass


def create_links(transform):
    """
    Recursively create the job links.
    """
    # TODO
    if transform.requirements:
        op = transform.opify()
        for prior_transform in transform.requirements:
            create_links(prior_transform)
            op.set_upstream()
    else:
        return transform.opify()
