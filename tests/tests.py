import luigi
import pytest
import unittest
import subprocess

import sys; sys.path.append("../")
from datablocks.transform import Transform
from datablocks.runner import Runner


# class BareRunner(luigi.Task):
#     def __enter__(self, requirements):
#         self.requirements = requirements


class TestRunner(unittest.TestCase):
    def setUp(self):
        pass

    def test_bare_run(self):
        # Test running nothing - just an empty list.
        Runner([]).run()


class TestTransform(unittest.TestCase):
    def setUp(self):
        self.identity_transform = Transform("fixtures/empty_valid_errorless_notebook.ipynb", [])

    def test_transform_valid_errorless_notebook(self):
        Runner([self.identity_transform]).run()

    def test_transform_invalid_notebook(self):
        pass

    def test_transform_valid_notebook_with_error(self):
        pass


# bare_runner = """
# import luigi
# import sys; sys.path.append("../")
# from datablocks.transform import Transform
#
#
# class BareRunner(luigi.Task):
#     def requires(self):
#         return {0}
#         """.format([])
#         with open("bare_runner.py", "w") as f:
#             f.write(bare_runner)
#
#         # subprocess.run(['PYTHONPATH="."', 'luigi', '--module', 'transform', 'Transform', '--local-scheduler',
#         #                 '--fp="/home/alex/Desktop/datablocks/notebooks/test-notebook.ipynb"', '--requirements=[]'])
#         subprocess.run(["luigi"])
