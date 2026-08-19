from app.db.mongo_queries import (
    avg_duration_by_search_type,
    last5_queries,
    search_type_breakdown,
    searches_per_day,
    success_rate_by_search_type,
    top5_queries,
    zero_result_queries,
)
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
    result = list(mongo_collection.aggregate(top5_queries))
    print(f"\n{banner('stats.top5.header')}")
    if not result:
        print(f"\n{t('stats.no_data')}")
        return
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
    result = list(mongo_collection.aggregate(last5_queries))
    print(f"\n{banner('stats.last5.header')}")
    if not result:
        print(f"\n{t('stats.no_data')}")
        return
    print(f"\n{t('stats.last5.col_query_key'):<40}| {t('stats.last5.col_search_type'):<18}| {t('stats.last5.col_results_count'):<14}| {t('stats.last5.col_duration')}")
    print("-" * 88)
    for row in result:
        print(f"{row['query_key']:<40}| {row['search_type']:<18}| {row['results_count']:<14}|\
{row['duration_ms']:>9.3f} ms")


def zero_result_requests(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays the queries that most often returned zero results.

    Uses the `zero_result_queries` aggregation pipeline, which surfaces
    the most direct signal of a catalog gap, an overly narrow filter, or
    a mistyped/misspelled search term: searches that executed
    successfully but found nothing.

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the report to the console and does not return any value.
    """
    result = list(mongo_collection.aggregate(zero_result_queries))
    print(f"\n{banner('stats.zero_results.header')}")
    if not result:
        print(f"\n{t('stats.no_data')}")
        return
    print(f"\n{t('stats.zero_results.col_query'):<40}| {t('stats.zero_results.col_count'):<16}| {t('stats.zero_results.col_last_seen')}")
    print("-" * 88)
    for row in result:
        print(f"{row['_id']:<40}| {row['count']:<16}| {row['last_seen']}")


def search_type_breakdown_requests(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays how often each search type (keyword / genre / years /
    genre_years) has been used, most-used first, alongside each type's
    share of all logged searches.

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the report to the console and does not return any value.
    """
    result = list(mongo_collection.aggregate(search_type_breakdown))
    print(f"\n{banner('stats.search_type_breakdown.header')}")
    if not result:
        print(f"\n{t('stats.no_data')}")
        return
    total = sum(row["count"] for row in result)
    print(f"\n{t('stats.search_type_breakdown.col_type'):<20}| {t('stats.search_type_breakdown.col_count'):<10}| {t('stats.search_type_breakdown.col_share')}")
    print("-" * 88)
    for row in result:
        share = (row["count"] / total * 100) if total else 0
        print(f"{row['_id']:<20}| {row['count']:<10}| {share:>5.1f}%")


def avg_duration_requests(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays the average search execution time per search type, slowest
    first — a quick way to spot which kind of search is heaviest on the
    database.

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the report to the console and does not return any value.
    """
    result = list(mongo_collection.aggregate(avg_duration_by_search_type))
    print(f"\n{banner('stats.avg_duration.header')}")
    if not result:
        print(f"\n{t('stats.no_data')}")
        return
    print(f"\n{t('stats.avg_duration.col_type'):<20}| {t('stats.avg_duration.col_avg_duration'):<18}| {t('stats.avg_duration.col_count')}")
    print("-" * 88)
    for row in result:
        print(f"{row['_id']:<20}| {row['avg_duration_ms']:>16.3f} | {row['count']}")


def activity_by_day_requests(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays the number of searches performed per calendar day, for the
    most recent 14 days that have any logged activity.

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the report to the console and does not return any value.
    """
    result = list(mongo_collection.aggregate(searches_per_day))
    print(f"\n{banner('stats.activity_by_day.header')}")
    if not result:
        print(f"\n{t('stats.no_data')}")
        return
    print(f"\n{t('stats.activity_by_day.col_date'):<15}| {t('stats.activity_by_day.col_count')}")
    print("-" * 88)
    for row in result:
        print(f"{row['_id']:<15}| {row['count']}")


def success_rate_requests(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays the success rate of executed searches, broken down by search
    type. "Success" reflects whether the search ran without an internal
    error (see execute_search()), not whether it found any results — a
    0-result search still counts as successful.

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the report to the console and does not return any value.
    """
    result = list(mongo_collection.aggregate(success_rate_by_search_type))
    print(f"\n{banner('stats.success_rate.header')}")
    if not result:
        print(f"\n{t('stats.no_data')}")
        return
    print(f"\n{t('stats.success_rate.col_type'):<20}| {t('stats.success_rate.col_total'):<8}| {t('stats.success_rate.col_successful'):<12}| {t('stats.success_rate.col_rate')}")
    print("-" * 88)
    for row in result:
        print(f"{row['_id']:<20}| {row['total']:<8}| {row['successful']:<12}| {row['success_rate_pct']:>5.1f}%")
