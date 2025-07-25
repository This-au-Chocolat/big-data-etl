FROM apache/airflow:2.8.1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache --upgrade pip setuptools wheel psycopg2-binary \
    && pip install --no-cache --upgrade apache-airflow-providers-postgres \
    && pip install --no-cache --upgrade apache-airflow-providers-sftp \
    && pip install --no-cache --upgrade apache-airflow-providers-ssh    
USER airflow