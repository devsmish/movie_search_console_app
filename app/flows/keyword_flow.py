from app.utils.input_utils import safe_input
from app.utils.console_colors import red
from app.services.search_service import execute_search
from app.db.sql_connection import keywords_search
from app.i18n.translator import t, banner


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
    print(f"""
{banner('flows.keyword.header')}
{t('flows.keyword.instruction')}""")
    input_word = safe_input(
        t("flows.keyword.input_prompt"),
        interrupt_msg=red(t("flows.keyword.interrupt")) + "\n"
    )
    if input_word is None:
        return None
    return input_word.strip().lower()


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
            print(t("flows.keyword.cancelled"))
            break
        if keyword == "":
            print(red(t("errors.empty_selection")))
            continue
        if keyword == "q":
            break

        execute_search(
            search_func=lambda: keywords_search(keyword, cursor),
            mongo_collection=mongo_collection,
            search_type="keyword",
            params={"keyword": keyword}
        )
