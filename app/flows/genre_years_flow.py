from app.flows.genre_flow import get_genres
from app.flows.years_flow import get_year_range
from app.db.sql_connection import genre_years_search
from app.services.search_service import execute_search
import datetime


def genre_years_flow(cursor, mongo_collection):
    genre = get_genres(cursor)
    if not genre:
        return

    params_years = get_year_range(1900, datetime.datetime.now().year)
    if not params_years:
        return

    start_year = params_years["start_year"]
    end_year = params_years["end_year"]

    execute_search(
        search_func=lambda: genre_years_search(cursor, genre, start_year, end_year),
        mongo_collection=mongo_collection,
        search_type="genre_years",
        params={
            "genre": genre,
            "start_year": start_year,
            "end_year": end_year
        }
    )
