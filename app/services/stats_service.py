from app.db.mongo_queries import top5_queries, last5_queries


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
        print(f"{row['query_key']:<40}| {row['search_type']:<18}| {row['results_count']:<14}|\
{row['duration_ms']:>9.3f} ms")
