#!/usr/bin/env bash
PYTHONPATH="." luigi --module transform Transform --local-scheduler --fp="/home/alex/Desktop/datablocks/notebooks/test-notebook.ipynb"