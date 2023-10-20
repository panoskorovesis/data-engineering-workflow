# Data Engineering Workflow

This project constitutes my solutions to the [Data Engineering ZoomCamp 2022 Course](https://github.com/DataTalksClub/data-engineering-zoomcamp)

During this course the following milestones are achieved:

1. Local hosting of a __Postgress DataBase using Docker__
2. Local hosting of an __Airflow using Docker__
3. An __ETL pipeline__ creation to fill the database with data
4. More comming soon

## Setup

### Postgress DataBase

In order to __create__ the postgress db simply execute the following command:

```sh
docker compose -f ./database/docker-compose.yaml up -d --build
```

After the initial creation, in order to activate the database execute the previous command without the `--build`

```sh
docker compose -f ./database/docker-compose.yaml up -d
```