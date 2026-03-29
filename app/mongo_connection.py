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
    print("""
==================================REPORT TOP-5 QUERIES==================================""")
    print("\nPrompt                                       | Count")
    print("-" * 88)
    for row in result:
        print(f"{row['_id']:<45}| {row['count']:<5}")

def last5_requests(mongo_collection):
    result = mongo_collection.aggregate(last5_queries)
    print("""
=================================REPORT LAST-5 QUERIES==================================""")
    print("\nQuery Key                               | Search Type       | Results Count | Duration, ms")
    print("-" * 88)
    for row in result:
        print(f"""
{row['query_key']:<40}| {row['search_type']:<18}| {row['results_count']:<14}| {row['duration_ms']:>9.3f} ms""")
