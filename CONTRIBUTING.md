`airscooter` is alpha-level software, and is still under active development.

Non-developmental installation requires Python >= 3.6 (due to [this bug](https://issues.apache.org/jira/browse/AIRFLOW-1165)) and 
`apache-airflow` trunk. A copy of the necessary dependencies is kept at `envs/env.yml`.

To install a development version, make sure you have Python >= 3.6, clone this repository, then do an editable `pip` 
install from root: 

```bash
git clone https://github.com/ResidentMario/airscooter.git
cd airscooter
pip install -e .
```

A copy of the packages necessary for development is kept in `envs/devenv.yml`.

`airflow` tests are located in the `tests` folder, and can be run via `pytest` (e.g. via `pytest tests/api_tests.py` 
from the command line).