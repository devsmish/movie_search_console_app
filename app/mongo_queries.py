# log examples
log_example_key = {
    "timestamp": "2026-03-25T15:34:00",
    "search_type": "keyword",
    "params": {
        "keyword": "matrix",
    },
    "results_count": 3,
    "duration_ms": 340,
    "success": True,
    "query_key": "keyword_JIN"
}

log_example_gy = {
    "timestamp": "2026-03-26T16:54:18",
    "search_type": "genre_years",
    "params": {
        "genres": "Action",
        "start_year": 1990,
        "end_year": 2025
 },
    "results_count": 250,
    "duration_ms": 250,
    "success": False,
    "query_key": "genres_years_Games_2005_2010"
}

log_example_genre = {
    "timestamp": "2026-03-26T16:54:18",
    "search_type": "genre",
    "params": {
        "genres": "Comedy"
 },
    "results_count": 250,
    "duration_ms": 250,
    "success": True,
    "query_key": "genre_Comedy"
}

log_example_years = {
    "timestamp": "2026-03-26T16:54:18",
    "search_type": "years",
    "params": {
        "start_year": 1990,
        "end_year": 2025
 },
    "results_count": 250,
    "duration_ms": 250,
    "success": False,
    "query_key": "years_1996_2001"
}

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
    "$project": {
      "_id": 0,
      "params": 0
    }
  },
  {
    "$sort": {
      "timestamp": -1
    }
  },
  {
    "$limit": 5
  }
]
