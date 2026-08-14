from app.utils.input_utils import safe_input
from app.utils.year_utils import normalize_year_input
from app.db.sql_connection import range_years, years_search
from app.services.search_service import execute_search
from app.i18n.translator import t, banner
import datetime


DEFAULT_MIN_YEAR = 1990


def get_available_year_range(cursor) -> tuple[int, int]:
    """
    Fetches the actual available release-year range from the database.

    Args:
        cursor: Active MySQL cursor.

    Returns:
        tuple[int, int]: (min_year, max_year). Falls back to
        (DEFAULT_MIN_YEAR, current_year - 1) if the query fails or
        returns no data, so the app can still function.
    """
    fallback = (DEFAULT_MIN_YEAR, datetime.datetime.now().year - 1)
    try:
        result = range_years(cursor)
    except Exception as e:
        print(t("flows.years.range_error", error=e))
        return fallback

    if not result or result[0].get("min_year") is None or result[0].get("max_year") is None:
        return fallback

    return result[0]["min_year"], result[0]["max_year"]


def show_years(min_year: int, max_year: int) -> None:
    """
    Displays the available range of years to the user.

    Args:
        min_year (int): Minimum available release year.
        max_year (int): Maximum available release year.

    Returns:
        None: The function prints information to the console and does not return a value.
    """
    print(t("flows.years.range_info", min=min_year, max=max_year))


def get_year_range(min_year: int, max_year: int) -> dict | None:
    """
    Prompts the user to enter a year or a range of years.

    Validates user input, normalizes 2-digit years to 4-digit years, and
    ensures the selected years are within the provided range.

    Args:
        min_year (int): Minimum allowed year.
        max_year (int): Maximum allowed year.

    Returns:
        dict | None: A dictionary with 'start_year' and 'end_year' keys if input is valid,
        or None if the user quits or interrupts input.

    Notes:
        - Accepts formats like "2000-2010", "2000/2010", "2000 2010" or single years.
        - Prints error messages for invalid input or out-of-range years.
    """
    while True:
        user_input = safe_input(
            f"\n{t('flows.years.input_prompt', min=min_year, max=max_year)}",
            interrupt_msg=f"\033[31m{t('flows.years.interrupt')}\033[0m\n"
        )

        if user_input is None or user_input == "q":
            return None

        if not user_input:
            print(f"\033[31m{t('flows.years.empty')}\033[0m")
            continue

        try:
            user_input = user_input.replace(" ", "-")
            user_input = user_input.replace("/", "-")
            if "-" in user_input:
                parts = user_input.split("-")
                if len(parts) != 2:
                    raise ValueError

                start = normalize_year_input(parts[0])
                end = normalize_year_input(parts[1])
            else:
                year = normalize_year_input(user_input)
                start = end = year

            if start > end:
                print(f"\033[31m{t('flows.years.start_after_end')}\033[0m")
                continue

            if start < min_year or end > max_year:
                print(f"\033[31m{t('flows.years.out_of_range')}\033[0m")
                continue

            return {
                "start_year": start,
                "end_year": end
            }

        except ValueError:
            print(f"\033[31m{t('flows.years.bad_format')}\033[0m")


def years_flow(cursor, mongo_collection) -> None:
    """
    Handles the flow for searching movies by a specific year or range of years.

    Fetches the actual available year range from the database, displays it,
    prompts the user to enter a year or range with `get_year_range`, and
    executes the search via `execute_search`, logging results to MongoDB.

    Args:
        cursor: Database cursor used to fetch data and perform searches.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search.

    Returns:
        None: Results are printed to the console and logged to MongoDB.

    Notes:
        - The year range is validated against the actual min/max release
          years present in the database, not a hardcoded assumption.
        - The function exits if the user cancels input.
    """
    print(f"""
{banner('flows.years.header')}
{t('flows.years.instruction')}""")
    min_year, max_year = get_available_year_range(cursor)
    show_years(min_year, max_year)
    params = get_year_range(min_year, max_year)
    if params is None:
        return
    execute_search(
        search_func=lambda: years_search(
            cursor,
            params["start_year"],
            params["end_year"]
        ),
        mongo_collection=mongo_collection,
        search_type="years",
        params=params
    )
