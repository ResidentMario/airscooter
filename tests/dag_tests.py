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
import subprocess

import unittest
# import pytest


# Default DAG arguments.
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now() + timedelta(seconds=3),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'schedule_interval': None
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}


class TestRun(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestDepositor", ".airflow/temp/foo.sh", ".airflow/temp/foo.csv")
        self.trans_sh = Transform("TestTransform", ".airflow/temp/foo2.sh", ".airflow/temp/foo.csv",
                                  ".airflow/temp/foo2.csv", requirements=[self.dep_sh])
        self.dag = DAG('dag', default_args=default_args)

        orchestration.configure(init=True)

        if ".airflow" not in os.listdir("."):
            os.mkdir(".airflow")
        if "dags" not in os.listdir(".airflow"):
            os.mkdir(".airflow/dags")
        if "temp" not in os.listdir(".airflow"):
            os.mkdir(".airflow/temp")

        with open(".airflow/temp/foo.sh", "w") as f:
            # f.write("echo HELLO")
            f.write("printf 'a,b,c\n1,2,3' >> ~/Desktop/foo.csv")

        # with open(".airflow/temp/foo2.sh", "w") as f:
        #     f.write("printf 'Success!' >> success.txt")

        orchestration.write_airflow_string([self.dep_sh], "./.airflow/dags/datablocks_dag.py")
        # orchestration.write_airflow_string([self.dep_sh, self.trans_sh], "./.airflow/dags/datablocks_dag.py")

        # with open(".airflow/temp/foo.sh", "w") as f:
        #     f.write("ECHO FOO\n"
        #             "printf 'a,b,c\n1,2,3' >> foo.csv")

    def test_run(self):
        orchestration.run()
        import pdb; pdb.set_trace()

    def tearDown(self):
        shutil.rmtree(".airflow")
