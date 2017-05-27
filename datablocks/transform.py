import nbformat
from datablocks.action import Action


class Transform:

    def __init__(self, fp):
        self.fp = fp
        nb = nbformat.read(fp, nbformat.current_nbformat)

        self.actions = parse_actions(nb)
        self.success = all(action.success for action in self.actions)


def parse_actions(nb):
    # Ignore non-code cells. Ignore first code cell, which should be boilerplate, and last, which should be file I/O.
    cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code'][1:-1]
    actions = [Action(cell) for cell in cells]
    return actions
