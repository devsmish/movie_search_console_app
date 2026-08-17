import pymysql
from config import Config
from pymysql.cursors import DictCursor
from app.db.sql_queries import *
from app.i18n.translator import t
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymysql.connections


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

        print(t("db.mysql_ok"))
        return connection

    except Exception as e:
        raise Exception(t("db.mysql_error", error=e))

MAX_KEYWORD_WORDS = 10
MAX_SELECTED_GENRES = 16


def keywords_search(keyword: str, cursor) -> list[dict]:
    """
    Searches for movies by one or more keywords/word-parts in the title.

    The input is split on whitespace into individual search terms. A film
    matches only if its title contains ALL of the entered terms as
    substrings, in any order and anywhere in the title — so "gone wind"
    and "wind gone" both match "Gone with the Wind", and each term can
    also be a partial word (e.g. "matr" matches "Matrix").

    Args:
        keyword (str): Keyword, phrase, or several words/word-parts to
            search for. Words are separated by whitespace.
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
        Returns an empty list without querying the database if `keyword`
        contains no usable words (e.g. empty or whitespace-only).

    Notes:
        - Duplicate words are ignored (searching "the the matrix" behaves
          the same as "the matrix").
        - At most MAX_KEYWORD_WORDS terms are used; any further words are
          silently dropped, so a very long pasted string can't blow up the
          query into dozens of AND-joined conditions.
    """
    words = list(dict.fromkeys(keyword.lower().split()))[:MAX_KEYWORD_WORDS]
    if not words:
        return []

    query = build_keyword(len(words))
    params = tuple(f"%{word}%" for word in words)
    cursor.execute(query, params)
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

def genre_years_search(
    cursor, genres: list[str], start_year: int = 1990, end_year: int = 2025
) -> list[dict]:
    """
    Searches for movies by one or more genres within a specified year range.

    A film matches if it belongs to ANY of the given genres (OR semantics —
    each film has exactly one genre in this schema, so "genres" here means
    "match any of these", not "must have all of these").

    Args:
        cursor: Active MySQL cursor (DictCursor).
        genres (list[str]): One or more genre names to match.
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
        Returns an empty list without querying the database if `genres`
        is empty.

    Notes:
        - Duplicate genres are ignored.
        - At most MAX_SELECTED_GENRES genres are used; further ones are
          silently dropped.
    """
    unique_genres = list(dict.fromkeys(genres))[:MAX_SELECTED_GENRES]
    if not unique_genres:
        return []

    query = build_genres_years(len(unique_genres))
    params = tuple(unique_genres) + (start_year, end_year)
    cursor.execute(query, params)
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

def genres_search(cursor, genres: list[str]) -> list[dict]:
    """
    Searches for movies by one or more genres.

    A film matches if it belongs to ANY of the given genres (OR semantics —
    each film has exactly one genre in this schema).

    Args:
        cursor: Active MySQL cursor (DictCursor).
        genres (list[str]): One or more genre names to match.

    Returns:
        list[dict]: List of movies belonging to any of the given genres:
            {
                "film_id": int,
                "title": str,
                "name": str,          # genre
                "release_year": int
                "description": str
            }
        Returns an empty list without querying the database if `genres`
        is empty.

    Notes:
        - Duplicate genres are ignored.
        - At most MAX_SELECTED_GENRES genres are used; further ones are
          silently dropped.
    """
    unique_genres = list(dict.fromkeys(genres))[:MAX_SELECTED_GENRES]
    if not unique_genres:
        return []

    query = build_genres(len(unique_genres))
    cursor.execute(query, tuple(unique_genres))
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

def build_keyword(word_count: int) -> str:
    """
    Builds a keyword search query that requires `word_count` independent
    substrings to ALL appear somewhere in the film title, in any order.

    This is what makes multi-word searches like "gone wind" match a title
    like "Gone with the Wind": each word is checked with its own
    `LOWER(f.title) LIKE %s`, and the individual checks are combined with
    AND, so word order and adjacency in the title don't matter. Each
    placeholder is still filled in with a separate `%word%` pattern by the
    caller, so this remains fully parameterized (no SQL injection risk)
    regardless of how many words the user typed.

    Args:
        word_count (int): Number of independent search terms (must be >= 1).

    Returns:
        str: A parameterized SQL query with `word_count` placeholders.

    Raises:
        ValueError: If word_count is less than 1.
    """
    if word_count < 1:
        raise ValueError("word_count must be at least 1")

    conditions = " AND ".join(["LOWER(f.title) LIKE %s"] * word_count)
    full_query = multiword_query + ' ' + conditions

    return full_query

def build_genres(genre_count: int) -> str:
    """
    Builds a genre search query that matches films belonging to ANY of
    `genre_count` given genres (an OR/IN condition, not AND).

    Genres are a many-to-one relationship in this schema (each film has
    exactly one category), so "search by several genres" means "match
    Action OR Comedy OR ...", unlike the AND semantics used for multi-word
    keyword search. A plain `%s` per genre, combined via SQL's `IN (...)`,
    keeps this fully parameterized regardless of how many genres are
    selected.

    Args:
        genre_count (int): Number of genres to match against (must be >= 1).

    Returns:
        str: A parameterized SQL query with `genre_count` placeholders.

    Raises:
        ValueError: If genre_count is less than 1.
    """
    if genre_count < 1:
        raise ValueError("genre_count must be at least 1")

    placeholders = ", ".join(["%s"] * genre_count)
    return build_genres_query.format(placeholders=placeholders)


def build_genres_years(genre_count: int) -> str:
    """
    Builds a combined genre + year-range search query, matching films that
    belong to ANY of `genre_count` given genres AND fall within the given
    release-year range.

    Args:
        genre_count (int): Number of genres to match against (must be >= 1).

    Returns:
        str: A parameterized SQL query with `genre_count + 2` placeholders
        (one per genre, plus start_year and end_year).

    Raises:
        ValueError: If genre_count is less than 1.
    """
    if genre_count < 1:
        raise ValueError("genre_count must be at least 1")

    placeholders = ", ".join(["%s"] * genre_count)
    return build_genres_years_query.format(placeholders=placeholders)
