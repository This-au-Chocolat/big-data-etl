# dags/restcountries_functions.py

import requests
from pymongo import MongoClient

def extract_restcountries_data(ti):
    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching Restcountries data: {e}")
        data = []
    ti.xcom_push(key='raw_restcountries_data', value=data)

def transform_restcountries_data(ti):
    raw_data = ti.xcom_pull(task_ids='extract_restcountries', key='raw_restcountries_data')
    print(f"DEBUG: raw_data type: {type(raw_data)}, length: {len(raw_data) if isinstance(raw_data, list) else 'N/A'}")
    if not raw_data or not isinstance(raw_data, list):
        print(f"DEBUG: raw_data content: {raw_data}")
        print("No valid raw data from extract_restcountries")   
        ti.xcom_push(key='transformed_restcountries_data', value=[])
        return

    transformed = []
    for country in raw_data:
        if not isinstance(country, dict):
            print(f"WARNING: Unexpected element type in raw_data: {type(country)} - {country}")
            continue
        try:
            transformed.append({
                "name": country.get("name", {}).get("common"),
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population"),
                "area": country.get("area"),
                "capital": country.get("capital", [None])[0] if country.get("capital") else None,
                "cca3": country.get("cca3"),
                "languages": list(country.get("languages", {}).values()) if country.get("languages") else [],
                "currencies": list(country.get("currencies", {}).keys()) if country.get("currencies") else [],
                "borders": country.get("borders", []),
                "flag": country.get("flags", {}).get("png")
            })
        except Exception as e:
            print(f"Error transforming country data: {e}")
            print(f"DEBUG: country content: {country}")
            continue

    print(f"DEBUG: transformed length: {len(transformed)}")
    ti.xcom_push(key='transformed_restcountries_data', value=transformed)

def load_restcountries_data(ti):
    mongo_uri = "mongodb://mongodb:27017/"
    client = MongoClient(mongo_uri)
    db = client.big_data_project
    collection = db.restcountries

    data = ti.xcom_pull(task_ids='transform_restcountries', key='transformed_restcountries_data')
    print(f"DEBUG: documentos a insertar en restcountries: {len(data) if data else 0}")
    if data:
        # Verificar duplicados antes de insertar datos en MongoDB
        existing_countries = set(collection.distinct("name"))
        new_data = [doc for doc in data if doc.get("name") not in existing_countries]

        if new_data:
            collection.insert_many(new_data)
            print(f"Inserted {len(new_data)} country records into MongoDB.")
        else:
            print("No se insertaron datos duplicados.")
    else:
        print("No transformed country data to load.")
