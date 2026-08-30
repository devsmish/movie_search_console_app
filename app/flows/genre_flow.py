from app.utils.input_utils import safe_input
from app.utils.console_colors import red
from app.db.sql_connection import list_genres, genres_search
from app.services.search_service import execute_search
from app.i18n.translator import t, banner


def get_genres(cursor) -> list[str] | None:
    """
    Prompts the user to select one or more genres from the database.

    Fetches the list of genres once using `list_genres(cursor)` and displays
    them. The user can select genres by number or title, and may enter
    several separated by commas (e.g. "1,3" or "action, comedy") to search
    across multiple genres at once.

    Args:
        cursor: Database cursor used to fetch genres from the database.

    Returns:
        list[str] | None: The list of selected genre names (in the order
        entered, duplicates removed), or None if the user quits,
        interrupts input, or an error occurs.

    Notes:
        - Handles KeyError if the genre data structure is invalid.
        - Handles errors in fetching genres and returns None if they occur.
        - Genre names come from the database (Sakila dataset) and are not
          translated — only the surrounding UI text is localized.
        - If any comma-separated entry doesn't match a genre, the whole
          input is rejected and the user is asked to try again, rather
          than silently accepting a partial selection.
    """
    try:
        genres = list_genres(cursor)
    except Exception as e:
        print(t("flows.genre.load_error", error=e))
        return None
    try:
        genre_names = {genre['category_id']: genre["name"] for genre in genres}
    except KeyError as e:
        print(t("flows.genre.data_error", error=e))
        return None

    print(f"""
{banner('flows.genre.header')}
{t('flows.genre.instruction')}""")
    print(f"{t('flows.genre.col_num'):<4}| {t('flows.genre.col_genre')}")
    for num, name in genre_names.items():
        print(f"{num:<4}| {name:<16}")

    lookup_by_name = {name.lower(): name for name in genre_names.values()}

    while True:
        choice = safe_input(
            f"\n{t('flows.genre.input_prompt')}",
            interrupt_msg=red(t("flows.genre.interrupt")) + "\n"
        )
        if choice is None or choice == "q":
            return None

        tokens = [token.strip() for token in choice.split(",") if token.strip()]
        if not tokens:
            print(red(t("flows.genre.invalid")))
            continue

        selected = []
        all_valid = True
        for token in tokens:
            if token.isdigit():
                genre = genre_names.get(int(token))
            else:
                genre = lookup_by_name.get(token)
            if genre is None:
                all_valid = False
                break
            if genre not in selected:
                selected.append(genre)

        if all_valid and selected:
            return selected

        print(red(t("flows.genre.invalid")))


def genres_flow(cursor, mongo_collection) -> None:
    """
    Handles the flow for searching by one or more genres.

    Repeatedly prompts the user to select genres using `get_genres`.
    For each selection, executes a search via `execute_search` with
    the results logged to MongoDB.

    Args:
        cursor: Database cursor used to perform the genre search.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search.

    Returns:
        None: Results are printed to the console and logged to MongoDB.
    """
    while True:
        genres = get_genres(cursor)
        if genres is None:
            break
        execute_search(
            search_func=lambda: genres_search(cursor, genres),
            mongo_collection=mongo_collection,
            search_type="genre",
            params={"genres": genres}
        )
