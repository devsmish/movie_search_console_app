from app.db.sql_connection import list_genres, genres_search
from app.services.search_service import execute_search


def get_genres(cursor) -> str | None:
    """
    Prompts the user to select a genre from the database.

    Fetches the list of genres using `list_genres(cursor)` and displays them.
    The user can select a genre by number or title. Returns the selected genre name.

    Args:
        cursor: Database cursor used to fetch genres from the database.

    Returns:
        str | None: The name of the selected genre, or None if the user quits
        or an error occurs.

    Notes:
        - Handles KeyError if the genre data structure is invalid.
        - Handles errors in fetching genres and returns None if they occur.
    """
    while True:
        print("""
=============================SELECT A GENRE FROM THE LIST===============================
Select a genre by number or title from the list or [q] to return to the previous menu.""")
        try:
            genres = list_genres(cursor)
        except Exception as e:
            print(f"GET_GENRES: Error loading genres: {e}")
            return None
        try:
            genre_names = {genre['category_id']: genre["name"] for genre in genres}
        except KeyError as e:
            print(f"GET_GENRES: Data structure error: {e}")
            return None
        print(f"#   | Genre")
        for num, name in genre_names.items():
            print(f"{num:<4}| {name:<16}")
        choice = input("""
Select a genre by number or title. 
Press [q] to return to the previous menu: """).strip()
        if choice == "q":
            return None
        if choice.isdigit():
            genre = genre_names.get(int(choice))
            if genre:
                return genre
        else:
            for name in genre_names.values():
                if choice.lower() == name.lower():
                    return name
        print("\033[31mInvalid genre. Try again.\033[0m")

def genres_flow(cursor, mongo_collection) -> None:
    """
    Handles the flow for searching by genre.

    Repeatedly prompts the user to select a genre using `get_genres`.
    For each selected genre, executes a search via `execute_search` with
    the results logged to MongoDB.

    Args:
        cursor: Database cursor used to perform the genre search.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search.

    Returns:
        None: Results are printed to the console and logged to MongoDB.
    """
    while True:
        genre = get_genres(cursor)
        if genre is None:
            break
        execute_search(
            search_func=lambda: genres_search(cursor, genre),
            mongo_collection=mongo_collection,
            search_type="genre",
            params={"genre": genre}
        )
