"""
Tests that ascertain that the API is working. Everything short of actually running a DAG (expensive and
difficult-to-test, see `dag_tests.py`) is tested here.
"""

import sys; sys.path.append("../")
from airscooter.depositor import Depositor
from airscooter.transform import Transform
from airscooter import orchestration

from airflow import DAG

from datetime import datetime
import os
import shutil
import subprocess

import unittest


# Sample default DAG arguments.
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}


# Helper functions.
def replace_once_right(string, a, b):
    i = string.rfind(a)
    return string[:i] + string[i:].replace(a, b)


def set_up_files():
    with open("foo.sh", "w") as f:
        f.write("echo HELLO")

    with open("foo2.sh", "w") as f:
        f.write("echo HELLO")

    with open("foo.csv", "w") as f:
        f.write("1,2,3\n9,8,7")


def tear_files_down():
    os.remove("foo.sh")
    os.remove("foo2.sh")
    os.remove("foo.csv")


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
        set_up_files()
        self.dep_sh = Depositor("TestTransform", "foo.sh", "foo.csv")
        self.dag = DAG('dag', default_args=default_args)

    def test_this(self):
        # noinspection PyUnresolvedReferences
        from airflow.operators.bash_operator import BashOperator
        d = self.dep_sh.as_airflow_string()
        # dag -> self.dag
        d = replace_once_right(d, "dag", "self.dag")
        bash_operator = eval(d)
        assert bash_operator.bash_command.rstrip() == "echo HELLO"

    def tearDown(self):
        tear_files_down()


class TestShellTransform(unittest.TestCase):
    def setUp(self):
        set_up_files()
        self.dep_sh = Depositor("TestTransform", "foo.sh", "foo.csv")
        self.trans_sh = Transform("TestTransform", "foo2.sh", "foo.csv", "foo2.csv", requirements=[self.dep_sh])
        self.dag = DAG('dag', default_args=default_args)

    def test_this(self):
        from airflow.operators.bash_operator import BashOperator
        t = self.trans_sh.as_airflow_string()
        # dag -> self.dag
        t = replace_once_right(t, "dag", "self.dag")
        bash_t = eval(t)
        assert bash_t.bash_command == "echo HELLO "

    def tearDown(self):
        tear_files_down()


class TestOrchestrationSerialization(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestDepositor", "foo.sh", "foo.csv")
        self.trans_sh = Transform("TestTransform", "foo2.sh", "foo.csv", "foo2.csv", requirements=[self.dep_sh])
        self.dag = DAG('dag', default_args=default_args)

    def test_deserialization(self):
        # Serialization test.
        orchestration.serialize_to_file([self.dep_sh, self.trans_sh], "foo.yml")
        assert "foo.yml" in os.listdir(".")

        # Deserialization test.
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

    def tearDown(self):
        if 'foo.yml' in os.listdir("."):
            os.remove('foo.yml')


def test_orchestration_configure():
    orchestration.configure()
    assert os.environ['AIRFLOW_HOME'] == os.path.abspath("./.airflow")


class TestOrchestrationAirflowString(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestDepositor", "foo.sh", "foo.csv")
        self.trans_sh = Transform("TestTransform", "foo2.sh", "foo.csv", "foo2.csv", requirements=[self.dep_sh])
        self.dag = DAG('dag', default_args=default_args)

        if ".airflow" not in os.listdir("."):
            os.mkdir(".airflow")
        if "dags" not in os.listdir(".airflow"):
            os.mkdir(".airflow/dags")

        set_up_files()

    def test_write(self):
        orchestration.write_airflow_string([self.dep_sh, self.trans_sh], ".airflow/dags/airscooter_dag.py")
        assert "airscooter_dag.py" in os.listdir(".airflow/dags/")

    def test_write_airflow_availability(self):
        if 'AIRFLOW_HOME' not in os.environ:
            orchestration.configure()

        orchestration.write_airflow_string([self.dep_sh, self.trans_sh], ".airflow/dags/airscooter_dag.py")
        # Note: subprocess.run is Python 3.5+.
        result = subprocess.run(["airflow", "list_dags"], env=os.environ.copy(), stdout=subprocess.PIPE).stdout
        expected = b"airscooter_dag"
        assert expected in result

    def tearDown(self):
        shutil.rmtree(".airflow")
        tear_files_down()


class TestOrchestrationWithDummies(unittest.TestCase):
    def setUp(self):
        self.dep_sh = Depositor("TestDepositor", "foo.sh", "foo.csv", dummy=True)
        self.trans_sh = Transform("TestTransform", "foo2.sh", "foo.csv", "foo2.csv",
                                  requirements=[self.dep_sh], dummy=True)
        self.dag = DAG('dag', default_args=default_args)

        if ".airflow" not in os.listdir("."):
            os.mkdir(".airflow")
        if "dags" not in os.listdir(".airflow"):
            os.mkdir(".airflow/dags")

        set_up_files()

    def test_write(self):
        orchestration.write_airflow_string([self.dep_sh, self.trans_sh], ".airflow/dags/airscooter_dag.py")
        assert "airscooter_dag.py" in os.listdir(".airflow/dags/")

    def tearDown(self):
        shutil.rmtree(".airflow")
        tear_files_down()
