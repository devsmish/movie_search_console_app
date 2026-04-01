from app.utils.input_utils import safe_input
from app.services.search_service import execute_search
from app.db.sql_connection import keywords_search


def input_keyword() -> str | None:
    """
    Prompts the user to enter a keyword for searching movies.

    Uses `safe_input` to handle user input safely, allowing interruption
    with a message and returning None if the user cancels or input is invalid.

    Args:
        None

    Returns:
        str | None: The keyword entered by the user, or None if input is
        interrupted or canceled.
    """
    print("""
=====================================ENTER KEYWORD======================================
Enter a word or phrase to search for a movie, or [q] to return to the previous menu.""")
    input_word = safe_input(
        "Enter your keyword: ",
        interrupt_msg="INPUT_KEYWORD: \033[31mThe user interrupted the program!\033[0m\n"
    )
    if input_word is None:
        return None
    return input_word


def keyword_flow(cursor, mongo_collection) -> None:
    """
    Handles the flow for searching movies by keyword.

    Repeatedly prompts the user to enter a keyword using `input_keyword`.
    For each valid keyword, executes a search via `execute_search` and logs
    the results to MongoDB.

    Args:
        cursor: Database cursor used for keyword search.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search.

    Returns:
        None: Results are printed to the console and logged to MongoDB.
    """
    while True:
        keyword = input_keyword()
        if keyword is None:
            print("Return to search menu")
            break
        if keyword == "":
            print("\033[31mEmpty selection. Try again.\033[0m")
            continue
        if keyword == "q":
            break

        execute_search(
            search_func=lambda: keywords_search(keyword, cursor),
            mongo_collection=mongo_collection,
            search_type="keyword",
            params={"keyword": keyword}
        )
