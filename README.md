# airscooter ![t](https://img.shields.io/badge/status-alpha-red.svg)

`airscooter` is a library and command-line utility for creating and executing simple graph-based workflows. A 
lightweight wrapper over [Apache Airflow](https://github.com/apache/incubator-airflow), it is designed 
to make workflows involving downloading, extracting, cleaning, and building datasets easily managable, 
reproducible, and triggerable.

## Installation

To install, make sure that you have a Python 3.6 environment. Then run:

```bash
pip install git+git://github.com/apache/incubator-airflow.git
pip install git+git://github.com/ResidentMario/airscooter.git
```

A `PyPi` release is on hold until `airflow@1.9.0` (or `airflow@1.8.1rc2`) is released, due to [a break bug](https://issues.apache.org/jira/browse/AIRFLOW-1165) that was only fixed recently.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for further details.
