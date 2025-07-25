# Big Data ETL Project

## Description
This project implements an ETL (Extract, Transform, Load) system using Apache Airflow for task orchestration, MongoDB as the database, and Streamlit for visualizing processed data. The goal is to extract data from various sources, transform it, and load it into a database for analysis and visualization.

## Components

### 1. Apache Airflow
- **DAGs**: Orchestrate extraction, transformation, and loading tasks.
- **Data Sources**:
  - Frankfurter API: Exchange rates.
  - Restcountries API: Country information.
  - World Bank API: GDP data.

### 2. MongoDB
- Stores processed data from different sources.
- Collections:
  - `frankfurter_data`
  - `restcountries_data`
  - `worldbank_data`

### 3. Streamlit
- Interactive application for visualizing processed data.
- Charts:
  - Exchange rates by currency.
  - GDP evolution by country.
  - Comparisons between regions and countries.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/This-au-Chocolat/big-data-etl.git
   ```

2. Navigate to the project directory:
   ```bash
   cd big-data-etl
   ```

3. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. Verify that the services are running:
   - Access the Airflow interface at `http://localhost:8080`.
   - Access the Streamlit application at `http://localhost:8501`.

### Common Issues and Solutions

- **Docker not installed**:
  Ensure Docker and Docker Compose are installed on your system. Follow the [Docker installation guide](https://docs.docker.com/get-docker/).

- **Port conflicts**:
  If `8080` or `8501` are already in use, update the `docker-compose.yml` file to use different ports.

- **MongoDB connection issues**:
  Ensure the MongoDB container is running and accessible. Check logs with:
  ```bash
  docker logs <container_id>
  ```

- **Airflow DAGs not appearing**:
  Verify that the `dags` folder is correctly mounted in the Airflow container. Restart the container if necessary:
  ```bash
  docker-compose restart
  ```

## Usage

1. Access the Airflow interface at `http://localhost:8080`.
2. Run the DAGs to process the data.
3. Access the Streamlit application at `http://localhost:8501` to visualize the data.

## Project Structure
```
├── dags
│   ├── frankfurter_dag.py
│   ├── restcountries_dag.py
│   ├── worldbank_dag.py
│   ├── utils
│   │   ├── api_helpers.py
│   │   ├── mongo_utils.py
├── streamlit_app
│   ├── app.py
│   ├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
```

## Contributions
Contributions are welcome. Please open an issue or submit a pull request for suggestions or improvements.

## License
This project is licensed under the MIT License.