## Pre-Reqiurement

### Install the virtualenv with pipenv
1. Check if your environment has pipenv by run `pipenv` in your terminal. if yes, jump to 2
Hoembrew is a popular open-source package management system for macOS(or Linux). Copy below command and run in your terminal
```sh
brew install pipenv
```

2. Create virtualenv with pipenv and install the packages \
    2.1. If you have the Pipfile.lock in your project \
    _(below command will create .venv under the project rood directory, if yo do not want, set **PIPENV_VENV_IN_PROJECT=0** or **do not include PIPENV_VENV_IN_PROJECT=1** in the below command)_

    ```sh
    export PIPENV_VENV_IN_PROJECT=1 && pipenv sync
    ```     
    If No, run \
    ```sh
    export PIPENV_VENV_IN_PROJECT=1 && pipenv shell
    ```

    >you will see the `.venv` folder is created under your project root directory.

    2.2. run `source .venv/bin/activate` to activate the virtualenv. \
    2.3. run `pipenv install` to install all packages needed from Pipfile \
    2.4. run `pip list` check if all necessary libraries are installed. or `pipenv graph` to check your installed dependencies


### Create a new Pipfile.lock if you installed new libraries.
When you are working on the DAG, the operator, the plugins, etc. might need additional libraries to support the functionalities. if you install them by `pip install`, then the additional library need to be included in Pipfile.lock. 

Run below command:

```sh
pipenv lock
```

## Set up Apache Airflow Local Development Environment
1. Initialize database - Apache Airflow requires a database to store its metadata. the database services as the backend for Airflow and is essential for metadata storage, scheduling and execution, etc.

```sh
airflow db init
```

below is the installation output
```sh
airflow db init                          
DB: sqlite:////Users/xxx/airflow/airflow.db
[2024-06-19T11:00:00.295-0500] {migration.py:216} INFO - Context impl SQLiteImpl.
[2024-06-19T11:00:00.298-0500] {migration.py:219} INFO - Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running stamp_revision  -> 686269002441
WARNI [airflow.models.crypto] empty cryptography key - values will not be stored encrypted.
Initialization done
```
2. Create a admin user.
```sh
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```
3. Start Airflow Services
```sh
airflow webserver --port 8080
```
you can access the Airflow web UI by navigating to `http://localhost:your_port` in your web brower. in this case is `http://localhost:8080`. if the 8080 could not be used, change to other ones.
4. **open a new terimial** and activate the virutal environment again, then start the scheduler:
```sh
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
airflow scheduler
```
5. Create and Run a DAG
5.1. create the dags folder under ~/airflow folder or your project root directory.
```sh
mkdir -p ./dags # create the dags under my project root directory
mkdir -p ~/airflow/dags # create the dags folder to the airlfow default path
```
5.2. Create a sample DAG:
Create a file named `first_dag.py` in the dags directory with the following content:
```python
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 1),
    'retries': 1,
}

dag = DAG(
    'first_dag',
    default_args=default_args,
    description='My first simple DAG',
    schedule_interval='@daily',
)

t1 = DummyOperator(
    task_id='task1',
    dag=dag,
)

t2 = DummyOperator(
    task_id='task2',
    dag=dag,
)

t1 >> t2

```
5.3. Verify the DAG:
* Go to the Airflow web UI (http://localhost:8080).
* You should see the first_dag listed. You can enable it and trigger runs manually.


### Below are the example of Pipfile 
```
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]

[packages]
apache-airflow = "*"
apache-airflow-providers-amazon = "*"
apache-airflow-providers-google = "*"
apache-airflow-providers-postgres = "*"
apache-airflow-providers-sqlite = "*"

[requires]
python_version = "3.9"
```

### How to fix `WARNING - Because we cannot use more than 1 thread (parsing_processes = 2) when using sqlite. So we set parallelism to 1.`
1. cd to `~/airflow`
2. vi airflow.cfg
3. change below configuration
```sh
[core]
parallelism = 1

load_examples = False
```
4. run `airflow db reset`
5. run `airflow db init`
6. run below command again
```sh
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```