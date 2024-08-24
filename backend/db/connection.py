# db/connection.py

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config.db_config import URI

def get_db_client():
    # Create a new client and connect to the server
    client = MongoClient(URI, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Connected to MongoDB!")
        return client
    except Exception as e:
        print(e)
        return None
