from pymongo import MongoClient
from app.config import Config

client = MongoClient(Config.MONGODB_URI)

def get_database():
    return client[Config.MONGODB_DB_NAME]