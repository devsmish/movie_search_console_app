from app.utils.pagination import print_results_paginated
from app.services.log_service import log_request
import datetime


def execute_search(search_func, mongo_collection, search_type, params) -> None:
    """
    Executes a search function, displays results, and logs the request.

    This function measures the execution time of the search function,
    handles errors during search and result display, prints the results
    in a paginated format, and logs the search request to MongoDB.

    Args:
        search_func (Callable): A function that performs the search and returns a list of results.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search request.
        search_type (str): Type of search (e.g., 'keyword', 'genre', etc.).
        params (dict): Dictionary of parameters used for the search.

    Returns:
        None: Results are printed to the console and logged to MongoDB. The function does not return any value.

    Notes:
        - Exceptions in the search, printing, or logging are caught and printed to the console.
        - Duration is measured in milliseconds.
    """
    start_time = datetime.datetime.now()
    success = True
    results = []

    try:
        results = search_func()
    except Exception as e:
        print(f"EXECUTE_SEARCH: Error searching in the database or in the query: {e}")
        success = False

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000

    try:
        print_results_paginated(results)
    except Exception as e:
        print(f"EXECUTE_SEARCH: Results output error: {e}")

    try:
        log_request(
            mongo_collection,
            search_type,
            params,
            len(results),
            duration,
            success
        )
    except Exception as e:
        print(f"EXECUTE_SEARCH: Logging error: {e}")
