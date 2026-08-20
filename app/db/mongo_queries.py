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

# Queries that returned no results at all — the most direct signal of a
# catalog gap, a too-narrow filter, or a mistyped/misspelled search term.
zero_result_queries = [
    {
        "$match": {"results_count": 0}
    },
    {
        "$group": {
            "_id": "$query_key",
            "count": {"$sum": 1},
            "last_seen": {"$max": "$timestamp"}
        }
    },
    {
        "$sort": {"count": -1, "last_seen": -1}
    },
    {
        "$limit": 10
    }
]

# How often each search type (keyword / genre / years / genre_years) is
# actually used, most-used first.
search_type_breakdown = [
    {
        "$group": {
            "_id": "$search_type",
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    }
]

# Average execution time per search type, slowest first — a quick way to
# spot which kind of search is the heaviest on the database.
avg_duration_by_search_type = [
    {
        "$group": {
            "_id": "$search_type",
            "avg_duration_ms": {"$avg": "$duration_ms"},
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"avg_duration_ms": -1}
    }
]

# Number of searches per calendar day, most recent day first. Formatting
# the date as a string inside the pipeline (rather than using $dateTrunc)
# keeps this compatible with older MongoDB versions (4.0+), not just 5.0+.
searches_per_day = [
    {
        "$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"_id": -1}
    },
    {
        "$limit": 14
    }
]

# Success rate per search type. "success" here reflects whether the search
# executed without an error (see execute_search()), not whether it found
# any results — a 0-result search still counts as successful.
success_rate_by_search_type = [
    {
        "$group": {
            "_id": "$search_type",
            "total": {"$sum": 1},
            "successful": {"$sum": {"$cond": ["$success", 1, 0]}}
        }
    },
    {
        "$project": {
            "total": 1,
            "successful": 1,
            "success_rate_pct": {
                "$multiply": [{"$divide": ["$successful", "$total"]}, 100]
            }
        }
    },
    {
        "$sort": {"_id": 1}
    }
]