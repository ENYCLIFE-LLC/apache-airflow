
## Setup Airflow Local Dev Env by [constraint](https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html#constraints-files)

**Airflow™ installation can be tricky because Airflow is both a library and an application.**

>Libraries usually keep their dependencies open and applications usually pin them, but we should do neither and both at the same time. We decided to keep our dependencies as open as possible (in pyproject.toml) so users can install different version of libraries if needed. This means that from time to time plain pip install apache-airflow will not work or will produce an unusable Airflow installation.


### Setup the airflow with constraint
Setup the airflow with constraint has sqlit database, scheduler, trggerer and webserver together. 
Triggers can be time-based, event-based, or condition-based, allowing for flexible and automated workflow scheduling and execution.

#### Create virtual env
```sh
export PIPENV_VENV_IN_PROJECT=1
pipenv --python 3.9
pipenv shell
```

#### Activate virtual Env
```sh
source .venv/bin/activate
```

#### Source constraints.sh

```sh
source constraints.sh
```

#### Install apache-airflow with constraint
```sh
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" 
```

#### run airflow standalone
```sh
airflow standalone
```


### pipenv install from requirements.txt 
```sh
pipenv install -r requirements.txt
```
>This command reads the requirements.txt file and installs the specified packages into the Pipfile and Pipfile.lock.