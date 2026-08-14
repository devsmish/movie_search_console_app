from app.utils.input_utils import build_query_key
from app.i18n.translator import t
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymongo.collection


def log_request(
    mongo_collection: "pymongo.collection.Collection",
    search_type: str,
    params: dict,
    total: int,
    duration: float,
    success: bool
) -> None:
    """
    Logs a search request into a MongoDB collection.

    Inserts a document containing details about the search, including
    timestamp, search type, parameters, result count, execution duration,
    success status, and a generated query key.

    Args:
        mongo_collection (pymongo.collection.Collection): The MongoDB collection where logs are stored.
        search_type (str): Type of search (e.g., 'keyword', 'genre', etc.).
        params (dict): Dictionary of search parameters.
        total (int): Number of results returned by the search.
        duration (float): Execution duration of the search in milliseconds.
        success (bool): True if the search was successful, False otherwise.

    Returns:
        None: The function inserts a document into MongoDB and does not return a value.

    Raises:
        Exception: Any exceptions during the insert operation are caught, and an error message is printed.
    """
    try:
        mongo_collection.insert_one(
            {
                "timestamp": datetime.datetime.now(),
                "search_type": search_type,
                "params": params,
                "results_count": total,
                "duration_ms": duration,
                "success": success,
                "query_key": build_query_key(search_type, params)
            }
        )
    except Exception as e:
        print(f"LOG_REQUEST: {t('db.log_write_error')}")
        print(t("db.log_write_detail", error=e))
