import nbformat
import nbconvert

import luigi
from nbconvert.preprocessors.execute import CellExecutionError


class Transform(luigi.Task):
    """Foo."""
    notebook = luigi.Parameter()
    requirements = luigi.ListParameter()

    def requires(self):
        return self.requirements

    def run(self):
        nb = nbformat.read(self.notebook, nbformat.current_nbformat)
        # https://nbconvert.readthedocs.io/en/latest/execute_api.html
        ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=600, kernel_name='python3')
        try:
            ep.preprocess(nb, {'metadata': {'path': "/".join(self.notebook.split("/")[:-1])}})
            with self.output().open('w') as f:
                nbformat.write(nb, f)
        except CellExecutionError:
            pass  # TODO

    def output(self):
        return luigi.LocalTarget(self.notebook)
