from pymongo import MongoClient
from config import Config


def get_mongo_collection():
    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[Config.MONGO_DATABASE]
        client.admin.command("ping")  # проверка
        print("MongoDB OK")
        return db[Config.MONGO_COLLECTION]
    except Exception as e:
        raise Exception(f"MongoDB connection error: {e}")
