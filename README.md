# airscooter ![t](https://img.shields.io/badge/status-alpha-red.svg)

`airscooter` is a library and command-line utility for creating and executing simple graph-based workflows. A 
lightweight wrapper over [Apache Airflow](https://github.com/apache/incubator-airflow), it is designed 
to make workflows involving downloading, extracting, cleaning, and building datasets easily managable, 
reproducible, and triggable.

## Quickstart

Forthcoming.

## Installation

To install, make sure that you have a Python 3.6 environment. Then run:

```bash
pip install git+git://github.com/apache/incubator-airflow.git
pip install git+git://github.com/ResidentMario/airscooter.git
```

## Development

`airscooter` is alpha-level software, and is still under active development.

* Python 3.6 or better (py-2 compatibility is possible, though it would be difficult to implement).
* Airflow trunk (via `pip install git+git://github.com/apache/incubator-airflow.git`; `pip install cryptography`), 
due to [this bug](https://issues.apache.org/jira/browse/AIRFLOW-1165).