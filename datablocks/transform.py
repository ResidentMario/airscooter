import nbformat
import nbconvert
from datablocks.action import Action
import luigi
from nbconvert.preprocessors.execute import CellExecutionError


class Transform(luigi.Task):
    """Foo."""

    def __init__(self, fp, requires):
        super().__init__()
        self.fp = fp
        self.requires = requires
        nb = nbformat.read(fp, nbformat.current_nbformat)

        self.actions = parse_actions(nb)
        self.success = all(action.success for action in self.actions)

    def requires(self):
        return self.requires

    def run(self):
        # https://nbconvert.readthedocs.io/en/latest/execute_api.html
        ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=600, kernel_name='python3')
        try:
            out = ep.preprocess(self.nb, {'metadata': {'path': 'notebooks/'}})
            with open(self.fp, 'wt') as f:
                nbformat.write(out, f)
            self.actions = parse_actions(out)
        except CellExecutionError:
            self.actions = []  # temp


def parse_actions(nb):
    # Ignore non-code cells. Ignore first code cell, which should be boilerplate, and last, which should be file I/O.
    cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code'][1:-1]
    actions = [Action(cell) for cell in cells]
    return actions
