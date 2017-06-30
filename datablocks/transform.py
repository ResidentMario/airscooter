# import nbformat
# import nbconvert
# from nbconvert.preprocessors.execute import CellExecutionError
from airflow import operators


class Transform:
    """Foo."""
    def __init__(self, filename, input, output, requirements=None):
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
