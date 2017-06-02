import nbformat
import nbconvert

import sys; sys.path.append("../")
from datablocks.action import Action

import luigi
from nbconvert.preprocessors.execute import CellExecutionError


class Transform(luigi.Task):
    """Foo."""
    fp = luigi.Parameter()
    requirements = luigi.ListParameter()
    outdir = luigi.Parameter()
    # nb = nbformat.read(fp, nbformat.current_nbformat)
    # self.actions = parse_actions(nb)
    # self.success = all(action.success for action in self.actions)

    def requires(self):
        return self.requirements

    def run(self):
        nb = nbformat.read(self.fp, nbformat.current_nbformat)
        # https://nbconvert.readthedocs.io/en/latest/execute_api.html
        ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=600, kernel_name='python3')
        try:
            ep.preprocess(nb, {'metadata': {'path': "/".join(self.fp.split("/")[:-1])}})
            with self.output().open('w') as f:
                nbformat.write(nb, f)
        except CellExecutionError:
            with self.output().open('w') as f:
                nbformat.write(nb, f)
            raise

    def output(self):
        return luigi.LocalTarget(self.fp)

# TODO: Incorporate this.
def parse_actions(nb):
    # Ignore non-code cells. Ignore first code cell, which should be boilerplate, and last, which should be file I/O.
    cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code'][1:-1]
    actions = [Action(cell) for cell in cells]
    return actions
