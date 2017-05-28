import sys; sys.path.append("../")
import luigi


class Reducer(luigi.Task):
    """Foo."""
    fp = luigi.Parameter()
    requirements = luigi.ListParameter()

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
            with open(self.fp, 'wt') as f:
                nbformat.write(nb, f)
        except CellExecutionError:
            with open(self.fp, 'wt') as f:
                nbformat.write(nb, f)
            raise


# TODO: Incorporate this.
def parse_actions(nb):
    # Ignore non-code cells. Ignore first code cell, which should be boilerplate, and last, which should be file I/O.
    cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code'][1:-1]
    actions = [Action(cell) for cell in cells]
    return actions
