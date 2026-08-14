from app.db.mongo_queries import top5_queries, last5_queries
from app.i18n.translator import t, banner
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymongo.collection


def top5_requests(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays the top 5 most frequent search queries from MongoDB logs.

    Uses a predefined aggregation pipeline `top5_queries` to get the
    five most frequent search prompts and prints them in a tabular format.

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the report to the console and does not return any value.

    Notes:
        - Requires the aggregation pipeline `top5_queries` to be defined globally.
    """
    result = mongo_collection.aggregate(top5_queries)
    print(f"\n{banner('stats.top5.header')}")
    print(f"\n{t('stats.top5.col_query'):<45}| {t('stats.top5.col_count')}")
    print("-" * 88)
    for row in result:
        print(f"{row['_id']:<45}| {row['count']:<5}")


def last5_requests(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays the last 5 unique executed search queries from MongoDB logs.

    Uses a predefined aggregation pipeline `last5_queries` to retrieve
    the five most recent queries and prints them with details like
    query key, search type, results count, and execution duration.

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the report to the console and does not return any value.

    Notes:
        - Requires the aggregation pipeline `last5_queries` to be defined globally.
        - Duration is printed in milliseconds with 3 decimal places.
    """
    result = mongo_collection.aggregate(last5_queries)
    print(f"\n{banner('stats.last5.header')}")
    print(f"\n{t('stats.last5.col_query_key'):<40}| {t('stats.last5.col_search_type'):<18}| {t('stats.last5.col_results_count'):<14}| {t('stats.last5.col_duration')}")
    print("-" * 88)
    for row in result:
        print(f"{row['query_key']:<40}| {row['search_type']:<18}| {row['results_count']:<14}|\
{row['duration_ms']:>9.3f} ms")
