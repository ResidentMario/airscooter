import sys; sys.path.append("../")
from datablocks.depositor import Depositor
from datablocks.transform import Transform
from datablocks import orchestration

from airflow import DAG

from datetime import datetime, timedelta
import os

import unittest
import pytest


# Default DAG arguments.
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}


# Helper functions.
def replace_once_right(string, a, b):
    i = string.rfind(a)
    return string[:i] + string[i:].replace(a, b)


# datafy tests.
def test_transform_datafy():
    dep_sh = Depositor("TestDepositor", "foo.sh", "foo.csv")
    trans_sh = Transform("TestTransform", "foo.sh", "foo.csv", "foo2.csv", requirements=[dep_sh])
    t = trans_sh.datafy()
    assert all([key in t for key in ['name', 'filename', 'input', 'output', 'type', 'requirements']])
    assert t['requirements'] == ["TestDepositor"]


# Shell script tests.
class TestShellDepositor(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestTransform", "foo.sh", "foo.csv")
        self.dag = DAG('dag', default_args=default_args)

    def test_this(self):
        # noinspection PyUnresolvedReferences
        from airflow.operators.bash_operator import BashOperator
        d = self.dep_sh.as_airflow_string()
        # dag -> self.dag
        d = replace_once_right(d, "dag", "self.dag")
        bash_operator = eval(d)
        assert bash_operator.bash_command == "foo.sh"


class TestShellTransform(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestTransform", "foo.sh", "foo.csv")
        self.trans_sh = Transform("TestTransform", "foo2.sh", "foo.csv", "foo2.csv", requirements=[self.dep_sh])
        self.dag = DAG('dag', default_args=default_args)

    def test_this(self):
        from airflow.operators.bash_operator import BashOperator
        t = self.trans_sh.as_airflow_string()
        # dag -> self.dag
        t = replace_once_right(t, "dag", "self.dag")
        bash_t = eval(t)
        assert bash_t.bash_command == "foo2.sh"


class TestOrchestrationSerialization(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestDepositor", "foo.sh", "foo.csv")
        self.trans_sh = Transform("TestTransform", "foo2.sh", "foo.csv", "foo2.csv", requirements=[self.dep_sh])
        self.dag = DAG('dag', default_args=default_args)

    def test_serialization(self):
        orchestration.serialize_to_file([self.dep_sh, self.trans_sh], "foo.yml")
        assert "foo.yml" in os.listdir(".")

    def test_deserialization(self):
        import pdb; pdb.set_trace()
        dag_objects = orchestration.deserialize_from_file("foo.yml")

        assert len(dag_objects) == 2
        assert isinstance(dag_objects[0], Depositor)
        assert isinstance(dag_objects[1], Transform)

        # Depositor result == expected
        assert dag_objects[0].__dict__ == self.dep_sh.__dict__

        # Transform result == expected
        result = dag_objects[1].__dict__.copy()
        result.pop('requirements')
        expected = self.trans_sh.__dict__.copy()
        expected.pop('requirements')
        assert result == expected


class TestOrchestrationAirflowString(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestDepositor", "foo.sh", "foo.csv")
        self.trans_sh = Transform("TestTransform", "foo2.sh", "foo.csv", "foo2.csv", requirements=[self.dep_sh])
        self.dag = DAG('dag', default_args=default_args)

        with open("foo.sh", "w") as f:
            f.write("printf 'a,b,c\n1,2,3' >> foo.csv")

        with open("foo2.sh", "w") as f:
            f.write("echo HELLO")

    def test_write(self):
        orchestration.write_airflow_string([self.dep_sh, self.trans_sh], "foo_dag.py")
        assert "foo_dag.py" in os.listdir(".")

    def test_run(self):
        # TODO
        pass

    def tearDown(self):
        for filename in ['foo.sh', 'foo.csv', 'foo2.sh', 'foo_dag.py', 'foo.yml']:
            if filename in os.listdir("."):
                os.remove(filename)