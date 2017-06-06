import luigi
import sys; sys.path.append("../")
from datablocks.transform import Transform


class TestRunningTransform(luigi.Task):
    def requires(self):
        return [Transform("../notebooks/test-notebook.ipynb", [], "test_file_out.csv")]