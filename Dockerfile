FROM apache/airflow:2.9.2
RUN pip install --no-cache-dir apache-airflow-providers-amazon apache-airflow-providers-github
USER airflow