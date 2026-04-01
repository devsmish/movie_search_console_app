from pymongo import MongoClient
from config import Config


def get_mongo_collection() -> "pymongo.collection.Collection":
    """
    Retrieves a MongoDB collection from the database.

    The function connects to MongoDB using the URI from the configuration,
    checks server availability with a 'ping' command, and returns the specified collection.

    Args:
        None

    Returns:
        pymongo.collection.Collection: A MongoDB collection object that allows
        performing operations such as find, insert, update, and delete. Documents
        in the collection are represented as Python dictionaries (dict) with keys
        and values corresponding to the structure of MongoDB documents.

    Raises:
        Exception: If the connection to MongoDB fails or the collection is unavailable.
    """
    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[Config.MONGO_DATABASE]
        client.admin.command("ping")  # проверка
        print("MongoDB OK")
        return db[Config.MONGO_COLLECTION]
    except Exception as e:
        raise Exception(f"MongoDB connection error: {e}")
