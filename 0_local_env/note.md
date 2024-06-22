source constraints.sh
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" 

if install google-re2 failed like: ERROR: Could not build wheels for google-re2, which is required to install pyproject.toml-based projects
brew install re2

pip freeze > reuqirements.txt

pip install pipenv

pipenv install

pipenv install -r requirements.txt

This command reads the requirements.txt file and installs the specified packages into the Pipfile and Pipfile.lock.



https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html#constraints-files


```sh
export PIPENV_VENV_IN_PROJECT=1
pipenv --python 3.9
pipenv shell
```

```sh
airflow standalone
```