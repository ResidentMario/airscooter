`airscooter` is alpha-level software, and is still under active development.

# Environment

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

# Tests

`airflow` tests are located in the `tests` folder, and can be run via `pytest`. (e.g. via `pytest api_tests.py` 
from the command line).

# Documentation

`airflow` documentation is generated via [`sphinx`](http://www.sphinx-doc.org/en/stable/index.html) and served using [GitHub Pages](https://pages.github.com/). You can access it [here](https://residentmario.github.io/airscooter/index.html).

The website is automatically updated whenever the `gh-pages` branch on GitHub is updated. `gh-pages` is an orphan branch containing only documentation. The root documentation files are kept in the `master` branch, then pushed to `gh-pages` using the procedure outlined [here](http://www.willmcginnis.com/2016/02/29/automating-documentation-workflow-with-sphinx-and-github-pages/) (with one change: `git rm -rf *` instead of `git rm -rf .`).

So to update the documentation, edit the `.rst` files in the `docs` folder, then run `make html` there from the command line (optionally also running `make clean` beforehand). Then follow the procedure linked above to make these changes live.

The API reference is generated using the `sphinx-autodoc` extension. To regenerate the reference, run `sphinx-apidoc -o source/ ../airscooter` from the command line, again followed by `make html`.
