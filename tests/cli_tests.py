"""Tests that ascertain that the CLI is working."""
# Note: initializing a .airflow folder is really slow. Hence we use a pytest mark shim called pytest-ordering to set
# the folder up at the beginning of the process and tear it down at the end, once, instead of repeating the process
# for many tests.

from click.testing import CliRunner
import unittest
import shutil
import pytest
from pathlib import Path


import sys; sys.path.append("../")
from datablocks import cli, orchestration


runner = CliRunner()


class TestInitialization(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_run(self):
        result = runner.invoke(cli.init, [])
        assert result.exit_code == 0


class TestReset(unittest.TestCase):
    @pytest.mark.run(order=2)
    def test_run(self):
        result = runner.invoke(cli.reset, [])
        assert result.exit_code == 0


class TestLink(unittest.TestCase):
    @pytest.mark.run(order=3)
    def test_depositor_link(self):
        try:
            result = runner.invoke(cli.link, ["test_depositor.py", "--outputs", "['bar.txt']"])
            assert result.exit_code == 0
        except ValueError:
            # https://github.com/pallets/click/issues/824#issue-241565723
            pass
        graph = orchestration.deserialize_from_file(".airflow/datablocks.yml")
        assert str(Path("test_depositor.py").resolve()) in [task.filename for task in graph]

    @pytest.mark.run(order=4)
    def test_transform_link(self):
        try:
            result = runner.invoke(cli.link, ["test_transform.py", "--inputs", "['bar.txt']",
                                              "--outputs", "['bar2.txt']"])
            assert result.exit_code == 0
        except ValueError:
            pass
        graph = orchestration.deserialize_from_file(".airflow/datablocks.yml")
        assert str(Path("test_transform.py").resolve()) in [task.filename for task in graph]

    @pytest.mark.run(order=5)
    def test_dummy_links(self):

        try:
            result = runner.invoke(cli.link, ["test_dummy_depositor.py", "--outputs", "['bar3.txt']", "--dummy"])
            assert result.exit_code == 0
            result = runner.invoke(cli.link, ["test_dummy_transform.py", "--inputs", "['bar3.txt']",
                                              "--outputs", "['bar4.txt']", "--dummy"])
            assert result.exit_code == 0
        except ValueError:
            pass

        graph = orchestration.deserialize_from_file(".airflow/datablocks.yml")
        assert str(Path("test_depositor.py").resolve()) in [task.filename for task in graph]


@pytest.mark.run(order=6)
def test_tear_down():
    # tearDown has to be done here, because a unittest tearDown in TestLink can surprisingly can run before the tests
    # finish. This is likely a bug with pytest-ordering.
    shutil.rmtree(".airflow")
