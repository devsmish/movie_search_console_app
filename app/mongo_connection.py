from pymongo import MongoClient
from config import Config
from app.mongo_queries import top5_queries, last5_queries


def get_mongo_collection():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DATABASE]
    return db[Config.MONGO_COLLECTION]

def top5_requests(mongo_collection):
    result = mongo_collection.aggregate(top5_queries)
    for row in result:
        print(f"Текст запроса '{row['_id']}' - количество: {row['count']}.")

def last5_requests(mongo_collection):
    result = mongo_collection.aggregate(last5_queries)
    for row in result:
        print(f"""Запрос '{row['query_key']}',тип запроса '{row['search_type']}', 
        количество результатов: {row['results_count']}, время запроса: {row['duration_ms']} мс""")