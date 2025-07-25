# dags/pipeline.py
import requests
from airflow.models import Variable
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
import json
from worldbank_functions import extract_worldbank_data, transform_worldbank_data
from restcountries_functions import extract_restcountries_data, transform_restcountries_data
from frankfurter_functions import extract_currency_data as extract_frankfurter_data, transform_currency_data as transform_frankfurter_data

# === WORLD BANK ===
def extract_worldbank_data(ti, country="MX"):
    url = f"http://api.worldbank.org/v2/country/{country}/indicator/NY.GDP.MKTP.CD?format=json"
    data = requests.get(url).json()
    ti.xcom_push(key=f'raw_worldbank_data_{country}', value=data)

def transform_worldbank_data(ti, country="MX"):
    raw_data = ti.xcom_pull(task_ids='extract_worldbank', key=f'raw_worldbank_data_{country}')
    if not raw_data or len(raw_data) < 2:
        print(f"No data to transform from World Bank for {country}")
        return
    records = raw_data[1]
    transformed = [{
        "indicator": r.get("indicator", {}).get("value"),
        "country": r.get("country", {}).get("value"),
        "date": datetime.strptime(r.get("date"), "%Y").isoformat() if r.get("date") else None,
        "value": float(r.get("value")) if r.get("value") else None,
        "growth_rate": (float(r.get("value")) / float(records[i - 1].get("value"))) - 1 if i > 0 and r.get("value") and records[i - 1].get("value") else None,
        "is_high_income_country": r.get("country", {}).get("value") in ["United States", "Germany", "Japan"]
    } for i, r in enumerate(records) if r.get("value") is not None]
    ti.xcom_push(key=f'transformed_worldbank_data_{country}', value=transformed)

# === RESTCOUNTRIES ===
def extract_restcountries_data(ti):
    url = "https://restcountries.com/v3.1/all"
    params = {
        "fields": "name,population,region,subregion,languages"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(f"DEBUG extract_restcountries_data: {type(data)}, len={len(data) if isinstance(data, list) else 'N/A'}")
    print(f"DEBUG extract_restcountries_data: content: {data}")
    # Si la respuesta es un dict con un mensaje de error, loguéalo y guarda una lista vacía
    if isinstance(data, dict):
        print(f"ERROR: La API de Restcountries devolvió un dict en vez de una lista. Respuesta: {data}")
        data = []
    elif isinstance(data, list) and len(data) > 0:
        print(f"DEBUG extract_restcountries_data: first element: {data[0]}")
    ti.xcom_push(key='raw_restcountries_data', value=data)

def transform_restcountries_data(ti):
    raw_data = ti.xcom_pull(task_ids='extract_restcountries', key='raw_restcountries_data')
    print(f"DEBUG transform_restcountries_data: raw_data type={type(raw_data)}, len={len(raw_data) if isinstance(raw_data, list) else 'N/A'}")
    if isinstance(raw_data, list) and len(raw_data) > 0:
        print(f"DEBUG transform_restcountries_data: first element: {raw_data[0]}")
    if not raw_data or not isinstance(raw_data, list):
        print(f"DEBUG: raw_data content: {raw_data}")
        print("No valid raw data from extract_restcountries")
        ti.xcom_push(key='transformed_restcountries_data', value=[])
        return

    transformed = []
    for c in raw_data:
        if not isinstance(c, dict):
            print(f"WARNING: Unexpected element type in raw_data: {type(c)} - {c}")
            continue
        try:
            obj = {
                "name": c.get("name", {}).get("common"),
                "population": c.get("population"),
                "region": c.get("region"),
                "subregion": c.get("subregion"),
                "languages": list(c.get("languages", {}).values()) if c.get("languages") else [],
                "population_density": c.get("population") / c.get("area") if c.get("population") and c.get("area") else None,
                "is_high_population_region": c.get("region") in ["Asia", "Africa"]
            }
            transformed.append(obj)
        except Exception as e:
            print(f"Error transforming country data: {e}")
            continue

    ti.xcom_push(key='transformed_restcountries_data', value=transformed)

# === FRANKFURTER ===
def extract_frankfurter_data(ti):
    # Obtener la fecha actual en formato YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.frankfurter.app/{current_date}"
    data = requests.get(url).json()
    ti.xcom_push(key='raw_frankfurter_data', value=data)

def transform_frankfurter_data(ti):
    raw_data = ti.xcom_pull(task_ids='extract_frankfurter', key='raw_frankfurter_data')
    transformed = [{
        "date": raw_data.get("date"),
        "base": raw_data.get("base"),
        "rates": json.dumps(raw_data.get("rates")),
        "average_rate": sum(raw_data.get("rates", {}).values()) / len(raw_data.get("rates", {})) if raw_data.get("rates") else None,
        "is_major_currency": raw_data.get("base") in ["USD", "EUR", "JPY"]
    }]
    ti.xcom_push(key='transformed_frankfurter_data', value=transformed)

# === ORCHESTRATION ===
def unified_data_pipeline(ti):
    # World Bank Pipeline
    countries = ["MX", "US", "BR", "CN"]  # Example list of countries
    for country in countries:
        extract_worldbank_data(ti, country=country)
        transform_worldbank_data(ti, country=country)

    # Restcountries Pipeline
    extract_restcountries_data(ti)
    transform_restcountries_data(ti)

    # Frankfurter Pipeline
    extract_frankfurter_data(ti)
    transform_frankfurter_data(ti)

    # Load All Data with Deduplication
    mongo_uri = "mongodb://mongodb:27017/"
    client = MongoClient(mongo_uri)
    db = client.big_data_project

    mapping = {
        'transformed_worldbank_data': 'worldbank_data',
        'transformed_restcountries_data': 'restcountries_data',
        'transformed_frankfurter_data': 'frankfurter_data',
    }

    for key, collection_name in mapping.items():
        data = ti.xcom_pull(task_ids='transform_' + collection_name.split('_')[0], key=key)
        print(f"DEBUG unified_data_pipeline: {collection_name} - documentos a insertar: {len(data) if data else 0}")
        if data:
            if collection_name in ['restcountries_data', 'frankfurter_data']:
                # Deduplication for batch data
                existing_records = set(db[collection_name].distinct("name" if collection_name == "restcountries_data" else "date"))
                new_data = [doc for doc in data if doc.get("name" if collection_name == "restcountries_data" else "date") not in existing_records]
                if new_data:
                    db[collection_name].insert_many(new_data)
                    print(f"✅ Inserted {len(new_data)} deduplicated documents into '{collection_name}'")
                else:
                    print(f"⚠️ No new data to insert for '{collection_name}' after deduplication")
            else:
                db[collection_name].insert_many(data)
                print(f"✅ Inserted {len(data)} documents into '{collection_name}'")
        else:
            print(f"⚠️ No data to insert for '{collection_name}'")
