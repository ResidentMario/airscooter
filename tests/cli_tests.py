"""Tests that ascertain that the CLI is working."""
from click.testing import CliRunner
import unittest
import shutil

import sys; sys.path.append("../")
from datablocks import cli, orchestration


runner = CliRunner()


# TODO: This test is very slow, so toggle out a --slow operator against pytest.
# class TestInitialization(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def test_run(self):
#         result = runner.invoke(cli.init, [])
#         assert result.exit_code == 0
#
#     def tearDown(self):
#         shutil.rmtree(".airflow")


# class TestReset(unittest.TestCase):
#     def test_run(self):
#         result = runner.invoke(cli.reset, [])
#         assert result.exit_code == 0
#
#     def tearDown(self):
#         shutil.rmtree(".airflow")


class TestLink(unittest.TestCase):
    def setUp(self):
        runner.invoke(cli.init, [])

    def test_depositor_link(self):
        result = runner.invoke(cli.link, ["test_depositor.py", "--outputs", "['bar2.txt']"])
        assert result.exit_code == 0
        graph = orchestration.deserialize_from_file(".airflow/datablocks.yml")
        assert "test_depositor.py" in [task.filename for task in graph]

    def tearDown(self):
        shutil.rmtree(".airflow")

# def test_hello_world():
#     @click.command()
#     @click.argument('name')
#     def hello(name):
#         click.echo('Hello %s!' % name)
#
#     runner = CliRunner()
#     result = runner.invoke(hello, ['Peter'])
#     assert result.exit_code == 0
#     assert result.output == 'Hello Peter!\n'
