from airflow import operators
import yaml


class Depositor:
    """Foo."""
    def __init__(self, name, filename, output, dummy=False):
        self.name = name
        self.filename = filename
        self.output = output
        self.dummy = dummy

    def datafy(self):
        return {'name': self.name,
                'filename': self.filename,
                'output': self.output,
                'type': 'depositor'}

    def as_airflow_string(self):
        op_type = self.filename.split(".")[1]
        if op_type == "sh":
            # noinspection PyUnresolvedReferences
            return """operators.BashOperator(bash_command={0}, task_id={1}, dag="dag")
""".format(self.filename, self.filename.split(".")[0])

    # def opify(self, dag):
    #     """
    #     Returns the requisite Airflow operator for performing the targeted operation.
    #     """
    #     op_type = self.filename.split(".")[1]
    #     if op_type == "sh":
    #         # noinspection PyUnresolvedReferences
    #         return operators.BashOperator(bash_command=self.filename,
    #                                       task_id=self.filename.split(".")[0],
    #                                       dag=dag)
    #     else:
    #         # TODO
    #         pass
