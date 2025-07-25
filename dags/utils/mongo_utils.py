from pymongo import MongoClient

def get_mongo_client():
    return MongoClient("mongodb://mongodb:27017")

def get_collection(name):
    client = get_mongo_client()
    return client['etl_project'][name]
