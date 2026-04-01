from app.utils.year_utils import normalize_year_input
from app.db.sql_connection import range_years, years_search
from app.services.search_service import execute_search
import datetime


def show_years(cursor) -> None:
    """
    Displays the available range of years from the database.

    Uses `range_years(cursor)` to fetch the minimum and maximum years
    for which data is available and prints them to the console.

    Args:
        cursor: Database cursor used to fetch the year range.

    Returns:
        None: The function prints information to the console and does not return a value.
    """
    try:
        result = range_years(cursor)
    except Exception as e:
        print(f"Error getting year range: {e}")
        return
    for row in result:
        print(f"You can specify a range of years from {row['min_year']} to {row['max_year']}")


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
        or None if the user quits.

    Notes:
        - Accepts formats like "2000-2010", "2000/2010", "2000 2010" or single years.
        - Prints error messages for invalid input or out-of-range years.
    """
    while True:
        user_input = input(f"""
Enter a year or range ({min_year}-{max_year}) or [q] to return to the previous menu: """).strip()

        if user_input == "q":
            return None

        if not user_input:
            print("\033[31mEmpty input. Try again.\033[0m")
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
                print("\033[31mStart year cannot be greater than end year!\033[0m")
                continue

            if start < min_year or end > max_year:
                print("\033[31mYear out of range\033[0m")
                continue

            return {
                "start_year": start,
                "end_year": end
            }

        except ValueError:
            print("\033[31mPlease enter the correct format (for example: 2000-2010, 2000/2010 or 2000 2010)\033[0m")


def years_flow(cursor, mongo_collection) -> None:
    """
    Handles the flow for searching movies by a specific year or range of years.

    Displays the available year range using `show_years`, prompts the user
    to enter a year or range with `get_year_range`, and executes the search
    via `execute_search`, logging results to MongoDB.

    Args:
        cursor: Database cursor used to fetch data and perform searches.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search.

    Returns:
        None: Results are printed to the console and logged to MongoDB.

    Notes:
        - The default year range is 1990 to the previous year.
        - The function exits if the user cancels input.
    """
    print("""
=====================================RANGE OF YEARS=====================================
Select a year or range of years or [q] to return to the previous menu.""")
    min_year = 1990
    max_year = datetime.datetime.now().year - 1
    show_years(cursor)
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
