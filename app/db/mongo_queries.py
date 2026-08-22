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

# Popularity of the searched release-year range, bucketed by decade of
# start_year (e.g. 1993 -> 1990). Covers both plain year searches and
# combined genre+years searches.
year_range_popularity = [
    {
        "$match": {"search_type": {"$in": ["years", "genre_years"]}}
    },
    {
        "$group": {
            "_id": {
                "$subtract": ["$params.start_year", {"$mod": ["$params.start_year", 10]}]
            },
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 10
    }
]

# How often each individual genre is searched, regardless of which other
# genres it was combined with in a given search (e.g. a search for
# "Action, Comedy" counts once towards Action and once towards Comedy).
top_individual_genres = [
    {
        "$match": {"search_type": {"$in": ["genre", "genre_years"]}}
    },
    {
        "$unwind": "$params.genres"
    },
    {
        "$group": {
            "_id": "$params.genres",
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 10
    }
]

# Raw fetch of the genre lists from searches that selected 2+ genres at
# once. Deliberately NOT computing the pairwise co-occurrence counts in
# the aggregation pipeline itself: generating all unique pairs within an
# array requires either a fragile self-$unwind-and-filter or MongoDB
# 5.2+'s $sortArray, neither of which is worth the complexity here. It's
# far simpler, more portable, and easier to test to fetch the raw genre
# lists and let genre_co_occurrence_requests() (in stats_service.py) do
# the pair-counting in plain Python via itertools.combinations.
genre_combinations_raw = [
    {
        "$match": {
            "search_type": {"$in": ["genre", "genre_years"]},
            "params.genres.1": {"$exists": True}  # at least 2 genres selected
        }
    },
    {
        "$project": {"_id": 0, "genres": "$params.genres"}
    }
]
