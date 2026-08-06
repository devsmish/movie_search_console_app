# Example logged document shapes (kept only as reference — see README.md
# "Example Logged Data (MongoDB)" for the canonical example):
#
# {
#     "timestamp": <datetime>,
#     "search_type": "keyword" | "genre" | "years" | "genre_years",
#     "params": {...},          # search-type specific parameters
#     "results_count": <int>,
#     "duration_ms": <float>,
#     "success": <bool>,
#     "query_key": "<search_type>_<...params>"
# }

# db queries
top5_queries = [
    {
        "$group": {
            "_id": "$query_key",
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 5
    }
]

last5_queries = [
  {
    "$sort": {"timestamp": -1 }
  },
  {
    "$group": {
      "_id": "$query_key",
      "doc": {"$first": "$$ROOT" }  # the most recent log for each key
    }
  },
  {
    "$replaceRoot": {"newRoot": "$doc" } # replace the current document with the generated one
  },
  {
    "$sort": {"timestamp": -1 }
  },
  {
    "$limit": 5
  }
]