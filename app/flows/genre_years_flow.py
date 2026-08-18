from app.flows.genre_flow import get_genres
from app.flows.years_flow import get_year_range, get_available_year_range, show_years
from app.db.sql_connection import genre_years_search
from app.services.search_service import execute_search


def genre_years_flow(cursor, mongo_collection) -> None:
    """
    Handles the flow for searching by one or more genres within a specific
    year range.

    Prompts the user to select genres using `get_genres` and a year range
    using `get_year_range`, validated against the actual min/max release
    years available in the database. Then executes a search via
    `execute_search` and logs the results to MongoDB.

    Args:
        cursor: Database cursor used to perform the genre and year-range search.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search.

    Returns:
        None: Results are printed to the console and logged to MongoDB.

    Notes:
        - If the user cancels genre selection or year range input, the function exits.
        - A film matches if it belongs to ANY of the selected genres AND
          falls within the selected year range.
        - `start_year` and `end_year` are included in the search parameters.
        - Uses the same year-range source as `years_flow` to keep validation
          bounds consistent across search types.
    """
    genres = get_genres(cursor)
    if not genres:
        return

    min_year, max_year = get_available_year_range(cursor)
    show_years(min_year, max_year)
    params_years = get_year_range(min_year, max_year)
    if not params_years:
        return

    start_year = params_years["start_year"]
    end_year = params_years["end_year"]

    execute_search(
        search_func=lambda: genre_years_search(cursor, genres, start_year, end_year),
        mongo_collection=mongo_collection,
        search_type="genre_years",
        params={
            "genres": genres,
            "start_year": start_year,
            "end_year": end_year
        }
    )
