import pymysql
from config import Config
from pymysql.cursors import DictCursor
from app.db.sql_queries import *


def get_connection() -> "pymysql.connections.Connection":
    """
    Establishes a connection to the MySQL database.

    Uses configuration parameters from the Config class and verifies
    the connection by sending a ping request.

    Returns:
        pymysql.connections.Connection: Active MySQL connection object.

    Raises:
        Exception: If connection to the database fails.
    """
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            cursorclass=DictCursor
        )

        connection.ping(reconnect=True)

        print("MySQL OK")
        return connection

    except Exception as e:
        raise Exception(f"MySQL connection error: {e}")

def keywords_search(keyword: str, cursor) -> list[dict]:
    """
    Searches for movies by keyword in title.

    Args:
        keyword (str): Keyword or phrase to search for.
        cursor: Active MySQL cursor (DictCursor).

    Returns:
        list[dict]: List of matching movies where each item contains:
            {
                "film_id": int,
                "title": str,
                "name": str,          # genre
                "release_year": int
                "description": str
            }
    """
    cursor.execute(keyword_query, (f"%{keyword}%",))
    return cursor.fetchall()

def list_genres(cursor) -> list[dict]:
    """
    Retrieves a list of all available movie genres.

    Args:
        cursor: Active MySQL cursor (DictCursor).

    Returns:
        list[dict]: List of genres where each item contains:
            {
                "category_id": int,
                "name": str
            }
    """
    cursor.execute(genres_list)
    return cursor.fetchall()

def genre_years_search(cursor, genre: str, start_year: int = 1990, end_year: int = 2025) -> list[dict]:
    """
    Searches for movies by genre within a specified year range.

    Args:
        cursor: Active MySQL cursor (DictCursor).
        genre (str): Genre name.
        start_year (int, optional): Start of year range. Defaults to 1990.
        end_year (int, optional): End of year range. Defaults to 2025.

    Returns:
        list[dict]: List of movies matching the criteria:
            {
                "film_id": int,
                "title": str,
                "name": str,          # genre
                "release_year": int
                "description": str
            }
    """
    cursor.execute(genres_years_query, (genre, start_year, end_year,))
    return cursor.fetchall()

def years_search(cursor, start_year: int = 1990, end_year: int = 2025) -> list[dict]:
    """
    Searches for movies within a specified year range.

    Args:
        cursor: Active MySQL cursor (DictCursor).
        start_year (int, optional): Start of year range. Defaults to 1990.
        end_year (int, optional): End of year range. Defaults to 2025.

    Returns:
        list[dict]: List of movies released within the given range:
            {
                "film_id": int,
                "title": str,
                "name": str,          # genre
                "release_year": int
                "description": str
            }
    """
    cursor.execute(years_query, (start_year, end_year,))
    return cursor.fetchall()

def genres_search(cursor, genre: str) -> list[dict]:
    """
    Searches for movies by a specific genre.

    Args:
        cursor: Active MySQL cursor (DictCursor).
        genre (str): Genre name.

    Returns:
        list[dict]: List of movies belonging to the given genre:
            {
                "film_id": int,
                "title": str,
                "name": str,          # genre
                "release_year": int
                "description": str
            }
    """
    cursor.execute(genres_query, (genre,))
    return cursor.fetchall()

def range_years(cursor) -> list[dict]:
    """
    Retrieves the minimum and maximum release years available in the dataset.

    Args:
        cursor: Active MySQL cursor (DictCursor).

    Returns:
        list[dict]: List containing a single record with:
            {
                "min_year": int,
                "max_year": int
            }
    """
    cursor.execute(range_years_query)
    return cursor.fetchall()
