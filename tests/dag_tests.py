"""
Tests datablocks-enabled airflow DAG runs.
"""

import sys; sys.path.append("../")
from datablocks.depositor import Depositor
from datablocks.transform import Transform
from datablocks import orchestration

from airflow import DAG

from datetime import datetime, timedelta
import os
import shutil

import unittest


# Default DAG arguments.
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now() + timedelta(seconds=3),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'schedule_interval': None
}


# class TestBasicRun(unittest.TestCase):
#     """Tests that transforms and depositors work, and that operations of the bash type work in practice."""
#     def setUp(self):
#         if ".airflow" not in os.listdir("."):
#             os.mkdir(".airflow")
#         if "dags" not in os.listdir(".airflow"):
#             os.mkdir(".airflow/dags")
#         if "temp" not in os.listdir(".airflow"):
#             os.mkdir(".airflow/temp")
#
#         self.write_dir = os.getcwd() + "/.airflow/temp/"
#
#         with open(self.write_dir + "foo.sh", "w") as f:
#             f.write("printf 'a,b,c\n1,2,3' >> {0}/foo.csv".format(self.write_dir))
#
#         with open(".airflow/temp/foo2.sh", "w") as f:
#             f.write("printf 'Success!' >> {0}/foo2.csv".format(self.write_dir))
#
#         self.dep_sh = Depositor("TestDepositor", ".airflow/temp/foo.sh", ".airflow/temp/foo.csv")
#         self.trans_sh = Transform("TestTransform", ".airflow/temp/foo2.sh", ".airflow/temp/foo.csv",
#                                   ".airflow/temp/foo2.csv", requirements=[self.dep_sh])
#         self.dag = DAG('dag', default_args=default_args)
#
#         orchestration.configure(init=True)
#
#         orchestration.write_airflow_string([self.dep_sh, self.trans_sh], "./.airflow/dags/datablocks_dag.py")
#
#     def test_run(self):
#         orchestration.run()
#
#         # TestDepositor (bash) success
#         assert "foo.csv" in os.listdir(os.getcwd() + "/.airflow/temp/")
#         # TestTransform (bash) success
#         assert "foo2.csv" in os.listdir(os.getcwd() + "/.airflow/temp/")
#
#     def tearDown(self):
#         shutil.rmtree(".airflow")


class TestOtherOperators(unittest.TestCase):
    """Tests non bash-type operators (.py and .ipynb for now)."""
    def setUp(self):
        if ".airflow" not in os.listdir("."):
            os.mkdir(".airflow")
        if "dags" not in os.listdir(".airflow"):
            os.mkdir(".airflow/dags")
        if "temp" not in os.listdir(".airflow"):
            os.mkdir(".airflow/temp")

        self.write_dir = os.getcwd() + "/.airflow/temp/"

        with open(self.write_dir + "foo.py", "w") as f:
            # noinspection SqlNoDataSourceInspection,SqlDialectInspection
            f.write("""import pandas\nwith open('{0}/foo.csv', 'w') as f: f.write('1,2,3')""".format(self.write_dir))

        with open(".airflow/temp/foo2.py", "w") as f:
            # noinspection SqlNoDataSourceInspection,SqlDialectInspection
            f.write("""with open('{0}/foo2.csv', 'w') as f: f.write('1,2,3')""".format(self.write_dir))

        import subprocess
        subprocess.run(["cp", "./fixtures/test_nb.ipynb",
                        os.getcwd() + "/.airflow/temp/foo3.ipynb"])

        # with open(".airflow/temp/foo3.py", "w") as f:
        #     # noinspection SqlNoDataSourceInspection,SqlDialectInspection
        #     f.write("""with open('{0}/foo2.csv', 'w') as f: f.write('1,2,3')""".format(self.write_dir))

        #     nb = nbformat.read(self.notebook, nbformat.current_nbformat)
        #     # https://nbconvert.readthedocs.io/en/latest/execute_api.html
        #     ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=600, kernel_name='python3')
        #     try:
        #         ep.preprocess(nb, {'metadata': {'path': "/".join(self.notebook.split("/")[:-1])}})
        #         with self.output().open('w') as f:
        #             nbformat.write(nb, f)
        #     except CellExecutionError:
        #         pass

        self.py_dep_sh = Depositor("TestDepositor", ".airflow/temp/foo.py", ".airflow/temp/foo.csv")
        self.py_trans_sh = Transform("TestPyTransform", ".airflow/temp/foo2.py", ".airflow/temp/foo.csv",
                                     ".airflow/temp/foo2.csv", requirements=[self.py_dep_sh])
        self.ipynb_trans_sh = Transform("TestJupyterTransform", ".airflow/temp/foo3.ipynb", ".airflow/temp/foo.csv",
                                        ".airflow/temp/foo3.csv", requirements=[self.py_dep_sh])
        self.dag = DAG('dag', default_args=default_args)

        orchestration.configure(init=True)

        orchestration.write_airflow_string([self.py_dep_sh, self.py_trans_sh, self.ipynb_trans_sh],
                                           "./.airflow/dags/datablocks_dag.py")

    def test_run(self):
        orchestration.run()

        # TestDepositor (bash) success
        assert "foo.csv" in os.listdir(os.getcwd() + "/.airflow/temp/")
        # TestTransform (python) success
        assert "foo2.csv" in os.listdir(os.getcwd() + "/.airflow/temp/")

        import pdb; pdb.set_trace()
        # TestTransform (ipynb) success
        assert "foo3.csv" in os.listdir(os.getcwd() + "/.airflow/temp/")

    def tearDown(self):
        shutil.rmtree(".airflow")
