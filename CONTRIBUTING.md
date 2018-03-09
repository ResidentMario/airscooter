`airscooter` is alpha-level software, and is still under active development.

## Development

### Cloning

To work on `airscooter` locally, you will need to clone it.

```sh 
git clone https://github.com/ResidentMario/missingno.git
```

You can then set up your own branch version of the code, and work on your changes for a pull request from there.

```sh
cd airscooter
git checkout -B new-branch-name
```

### Environment

I strongly recommend creating a new virtual environment when working on `airscooter` (e.g. not using the base system 
Python). You can do so with either [`conda`](https://conda.io/) or `virtualenv`. 

I personally recommend doing the following:

```sh
conda env create --name airscooter-dev --file /airscooter/envs/devenv.yml --yes
source activate airscooter
```

You should then create an [editable install](https://pip.pypa.io/en/latest/reference/pip_install/#editable-installs) of 
`airscooter` suitable for tweaking and further development. Do this by running:

```sh
pip install -e airscooter .
```

Note that `airscooter` is (currently) only tested on Python 3.6 or better. Also, due to 
[AIRFLOW-1165](https://issues.apache.org/jira/browse/AIRFLOW-1165), you need to be running on `airflow@1.8.1` or newer.

### Testing

`airflow` tests are located in the `tests` folder, and can be run via `pytest`. (e.g. via `pytest api_tests.py` 
from the command line). There are three test files:

* `api_tests.py` tests the user-level API.
* `cli_tests.py` tests the user-level CLI.
* `dag_tests.py` tests `airscooter` integration against `airflow`. These tests may take a while to execute.

## Documentation

`airflow` documentation is generated via [`sphinx`](http://www.sphinx-doc.org/en/stable/index.html) and served using [GitHub Pages](https://pages.github.com/). You can access it [here](https://residentmario.github.io/airscooter/index.html).

The website is automatically updated whenever the `gh-pages` branch on GitHub is updated. `gh-pages` is an orphan branch containing only documentation. The root documentation files are kept in the `master` branch, then pushed to `gh-pages` using the procedure outlined [here](http://www.willmcginnis.com/2016/02/29/automating-documentation-workflow-with-sphinx-and-github-pages/) (with one change: `git rm -rf *` instead of `git rm -rf .`).

So to update the documentation, edit the `.rst` files in the `docs` folder, then run `make html` there from the command line (optionally also running `make clean` beforehand). Then follow the procedure linked above to make these changes live.

The API reference is generated using the `sphinx-autodoc` extension. To regenerate the reference, run `sphinx-apidoc -o source/ ../airscooter` from the command line, again followed by `make html`.
