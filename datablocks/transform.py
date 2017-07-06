# import nbformat
# import nbconvert
# from nbconvert.preprocessors.execute import CellExecutionError
from airflow import operators
import yaml


class Transform:
    """Foo."""
    def __init__(self, name, filename, input, output, requirements=None):
        self.name = name
        self.filename = filename
        self.input = input
        self.output = output
        self.requirements = [] if requirements is None else requirements

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

    def datafy(self):
        return {'name': self.name,
                'filename': self.filename,
                'input': self.input,
                'output': self.output,
                'requirements': [r.name for r in self.requirements],
                'type': 'transform'}

    # def run2(self):
    #     nb = nbformat.read(self.notebook, nbformat.current_nbformat)
    #     # https://nbconvert.readthedocs.io/en/latest/execute_api.html
    #     ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=600, kernel_name='python3')
    #     try:
    #         ep.preprocess(nb, {'metadata': {'path': "/".join(self.notebook.split("/")[:-1])}})
    #         with self.output().open('w') as f:
    #             nbformat.write(nb, f)
    #     except CellExecutionError:
    #         pass  # TODO
