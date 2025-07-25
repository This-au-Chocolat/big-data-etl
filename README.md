# Simple Airflow Setup for Students

This is a basic Apache Airflow setup using Docker Compose. Perfect for learning and teaching!

## What is this?

- **Airflow**: A tool to schedule and run data workflows
- **Docker Compose**: A way to run multiple applications together easily
- **PostgreSQL**: A database that stores Airflow's information

## How to use it

### 1. Create the folders
```bash
mkdir dags logs
```
**Why?** These folders will be connected to the Airflow containers so you can put your DAG files in them.

### 2. Initialize the database (IMPORTANT!)
```bash
docker-compose run --rm webserver airflow db init
```
**What this does:**
- `docker-compose run` = Run a one-time command in a container
- `--rm` = Remove the container after the command finishes (clean up)
- `webserver` = Use the webserver service configuration
- `airflow db init` = Create all the database tables that Airflow needs

**Why separate?** We need to set up the database BEFORE starting the services. If we don't, Airflow will crash because it can't find its tables.

### 3. Create admin user
```bash
docker-compose run --rm webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow
```
**What this does:**
- Creates a user account so you can log into the web interface
- Username: `airflow`, Password: `airflow`

**Why separate?** We need a user account to access the web interface. This only needs to be done once.

### 4. Start Airflow
```bash
docker-compose up -d
```
**What this does:**
- `up` = Start all the services defined in docker-compose.yml
- `-d` = Run in the background (detached mode)

**Now you have:**
- PostgreSQL database running
- Airflow webserver running (web interface)
- Airflow scheduler running (task runner)

### 5. Access Airflow
Open your browser and go to: http://localhost:8080

- Username: `airflow`
- Password: `airflow`

### 6. Stop Airflow
```bash
docker-compose down
```

## Reset Everything (Start Fresh)

If you want to start completely from scratch (useful for teaching or if something goes wrong):

```bash
# 1. Stop everything
docker-compose down

# 2. Remove the database data (this deletes everything!)
docker volume rm 3-etl-airflow-orchestration_postgres_data

# 3. Now you can start fresh with the initialization steps above
```

**What this does:**
- `docker-compose down` = Stop all services
- `docker volume rm` = Delete the database data permanently
- Now you're back to a clean slate!

## What each service does

1. **postgres**: The database (stores DAGs, task history, etc.)
2. **webserver**: The web interface you see in the browser
3. **scheduler**: The brain that runs your tasks

## Where to put your DAGs

Put your Python DAG files in the `dags/` folder. They will automatically appear in the Airflow web interface.

## Example DAG

Create a file `dags/hello_world.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello_world():
    print("Hello from Airflow!")

dag = DAG(
    'hello_world',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily'
)

task = PythonOperator(
    task_id='hello_task',
    python_callable=hello_world,
    dag=dag
)
```

## Troubleshooting

- If you get permission errors, run: `sudo chown -R 50000:0 dags logs`
- If the web interface doesn't load, wait a few minutes for everything to start up
- **If you see "database not initialized" error**: Run the initialization commands in steps 2 and 3 above
- **If you see "database already initialized" error**: Use the "Reset Everything" section above

## Quick Reference

**First time setup:**
```bash
mkdir dags logs
docker-compose run --rm webserver airflow db init
docker-compose run --rm webserver airflow users create --username airflow --firstname Admin --lastname User --role Admin --email admin@example.com --password airflow
docker-compose up -d
```

**Every time after:**
```bash
docker-compose up -d    # Start
docker-compose down     # Stop
```

**Reset everything:**
```bash
docker-compose down
docker volume rm 3-etl-airflow-orchestration_postgres_data
``` 