import requests
from airflow.models import Variable
from pymongo import MongoClient

def extract_worldbank_data(ti):
    url = "https://api.worldbank.org/v2/country/{}/indicator/NY.GDP.MKTP.CD?format=json"
    latin_american_countries = ["ARG", "BRA", "CHL", "COL", "CRI", "CUB", "ECU", "GTM", "HND", "MEX", "NIC", "PAN", "PRY", "PER", "SLV", "URY", "VEN"]
    all_data = []

    for country in latin_american_countries:
        response = requests.get(url.format(country))
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                all_data.extend(data[1])

    ti.xcom_push(key='raw_worldbank_data', value=all_data)

def transform_worldbank_data(ti):
    raw = ti.xcom_pull(task_ids='extract_worldbank', key='raw_worldbank_data')
    transformed = []

    for entry in raw:
        transformed.append({
            "country": entry.get("countryiso3code"),
            "date": entry.get("date"),
            "value": entry.get("value")
        })

    ti.xcom_push(key='transformed_worldbank_data', value=transformed)

def load_worldbank_data(ti):
    mongo_uri = "mongodb://mongodb:27017/admin"
    client = MongoClient(mongo_uri)
    db = client.big_data_project
    collection = db.worldbank_data

    data = ti.xcom_pull(task_ids='transform_worldbank', key='transformed_worldbank_data')
    if data:
        for document in data:
            # Check if the document already exists in the collection
            existing_doc = collection.find_one({"country": document["country"], "date": document["date"]})
            if not existing_doc:
                collection.insert_one(document)
        print(f"Inserted {len(data)} World Bank documents, avoiding duplicates.")
    else:
        print("No transformed World Bank data to load.")
