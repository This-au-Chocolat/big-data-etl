# Big Data ETL Project

## Description
This project implements an ETL (Extract, Transform, Load) system using Apache Airflow for task orchestration, MongoDB as the database, and Streamlit for visualizing processed data. The goal is to extract data from various sources, transform it, and load it into a database for analysis and visualization.

## Components

### 1. Apache Airflow
- **DAGs**: Orchestrate extraction, transformation, and loading tasks.
- **Data Sources**:
  - [Frankfurter API](https://www.frankfurter.app/): Exchange rates.
  - [Restcountries API](https://restcountries.com/): Country information.
  - [World Bank API](https://data.worldbank.org/): GDP data.

### 2. MongoDB vs PostgreSQL
- **MongoDB**: Used for this project due to its flexibility in handling semi-structured data like JSON, which is ideal for APIs.
- **PostgreSQL**: While suitable for structured data, it was not chosen as the APIs used return data in JSON format, making MongoDB a better fit.

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

## Usage

### Triggering the DAG and Checking Logs
1. Open the Airflow interface at `http://localhost:8080`.
2. Navigate to the DAGs section and trigger the desired DAG.
3. Check logs by clicking on the task instance in the DAG view.

### Opening the Streamlit Dashboard
1. Access the Streamlit application at `http://localhost:8501`.
2. Use the interactive dashboard to visualize processed data.

## Explanation of XCom Usage
- **XComs**: Used in Airflow to pass data between tasks.
  - Example: The `extract_currency_data` task pushes raw data to XComs, which is then pulled by the `transform_currency_data` task for processing.
  - This mechanism ensures modularity and allows tasks to communicate efficiently.

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