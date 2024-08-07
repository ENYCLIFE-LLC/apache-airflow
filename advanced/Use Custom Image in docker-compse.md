```sh
docker build . -f Dockerfile --tag custom-airflow:0.0.4
```

```sh
echo "AIRFLOW_IMAGE_NAME=custom-airflow:0.0.1" >> .env
```

```sh
docker-compose down --volumes
docker-compose up --build
```
`--volumes`: Removes any existing volumes, which ensures you start with a clean database
`--build`: forces a rebuild of the Docker images
