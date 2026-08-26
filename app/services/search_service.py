from app.utils.pagination import print_results_paginated
from app.services.log_service import log_request
from app.utils.app_logger import get_logger
from app.i18n.translator import t
import datetime

_logger = get_logger(__name__)


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
        - In addition to the console message, each failure is also written
          (with a traceback) to the rotating file log at logs/app.log via
          app.utils.app_logger, for after-the-fact debugging.
        - Duration is measured in milliseconds.
    """
    start_time = datetime.datetime.now()
    success = True
    results = []

    try:
        results = search_func()
    except Exception as e:
        print(f"EXECUTE_SEARCH: {t('search_service.search_error', error=e)}")
        _logger.error(
            "Search execution failed (search_type=%s, params=%s): %s",
            search_type, params, e, exc_info=True,
        )
        success = False

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000

    try:
        print_results_paginated(results)
    except Exception as e:
        print(f"EXECUTE_SEARCH: {t('search_service.output_error', error=e)}")
        _logger.error(
            "Failed to display results (search_type=%s): %s",
            search_type, e, exc_info=True,
        )

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
        print(f"EXECUTE_SEARCH: {t('search_service.logging_error', error=e)}")
        _logger.error(
            "Failed to log search request (search_type=%s): %s",
            search_type, e, exc_info=True,
        )
