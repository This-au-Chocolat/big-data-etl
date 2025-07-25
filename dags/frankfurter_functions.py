import requests
from airflow.models import Variable
from pymongo import MongoClient

def extract_currency_data(ti):
    url = "https://api.frankfurter.app"
    start_date = "2025-06-01"
    end_date = "2025-07-01"
    response = requests.get(f"{url}/{start_date}..{end_date}")
    data = response.json()
    ti.xcom_push(key='raw_currency_data', value=data)

def transform_currency_data(ti):
    raw = ti.xcom_pull(task_ids='extract_currency', key='raw_currency_data')
    rates = raw.get("rates", {})

    if "MXN" not in rates:
        rates["MXN"] = None  # Add MXN with a default value if missing

    transformed = [{"currency": k, "rate": v} for k, v in rates.items()]
    ti.xcom_push(key='transformed_currency_data', value=transformed)

def load_currency_data(ti):
    mongo_uri = "mongodb://mongodb:27017/admin"  # Updated URI to use container name
    client = MongoClient(mongo_uri)
    db = client.big_data_project
    collection = db.frankfurter_data  # Updated collection name

    data = ti.xcom_pull(task_ids='transform_currency', key='transformed_currency_data')
    print(f"Data to be inserted: {data}")  # Debug statement

    if data:
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Rename 'rate' to 'rates' and add 'date' field in each document
            for item in data:
                item['rates'] = item.pop('rate', {})
                item['date'] = item['currency']  # Assuming 'currency' contains the date
            collection.insert_many(data)
            print(f"Inserted {len(data)} currency documents.")
        else:
            print("Data format is invalid. Expected a list of dictionaries.")
    else:
        print("No transformed currency data to load.")
