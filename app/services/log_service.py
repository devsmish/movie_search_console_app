from app.utils.input_utils import build_query_key
import datetime


def log_request(mongo_collection, search_type, params, total, duration, success):
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
        print("LOG_REQUEST: Connection error or invalid document generated")
        print(f"MongoDB write error: {e}")
