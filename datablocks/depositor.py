from airflow import operators


class Depositor:
    """Foo."""
    def __init__(self, filename, output, dummy=False):
        self.filename = filename
        self.output = output
        self.dummy = dummy
        self.requirements = None

    def opify(self, dag):
        """
        Returns the requisite Airflow operator for performing the targeted operation.
        """
        op_type = self.filename.split(".")[1]
        if op_type == "sh":
            # noinspection PyUnresolvedReferences
            return operators.BashOperator(bash_command=self.filename,
                                          task_id=self.filename.split(".")[0],
                                          dag=dag)
        else:
            # TODO
            pass
