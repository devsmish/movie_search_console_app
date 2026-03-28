from pymongo import MongoClient
from config import Config
from app.mongo_queries import top5_queries, last5_queries


def get_mongo_collection():
    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[Config.MONGO_DATABASE]
        client.admin.command("ping")  # проверка
        print("MongoDB OK")
        return db[Config.MONGO_COLLECTION]
    except Exception as e:
        raise Exception(f"MongoDB connection error: {e}")

def top5_requests(mongo_collection):
    result = mongo_collection.aggregate(top5_queries)
    for row in result:
        print(f"Текст запроса '{row['_id']}' - количество: {row['count']}.")

def last5_requests(mongo_collection):
    result = mongo_collection.aggregate(last5_queries)
    for row in result:
        print(f"""Запрос '{row['query_key']}',тип запроса '{row['search_type']}', 
        количество результатов: {row['results_count']}, время запроса: {row['duration_ms']} мс""")
