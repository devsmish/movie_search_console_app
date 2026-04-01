from app.utils.input_utils import safe_input
from app.flows.keyword_flow import keyword_flow
from app.flows.years_flow import years_flow
from app.flows.genre_flow import genres_flow
from app.flows.genre_years_flow import genre_years_flow


def search_menu(cursor, mongo_collection) -> None:
    """
    Displays the search menu for movies and handles user selection.

    Allows the user to choose a search criterion:
    1. Search by keyword
    2. Search by genre
    3. Search by year or range of years
    4. Search by genre and year range
    Q. Return to the previous menu

    Args:
        cursor: Database cursor used for performing the searches.
        mongo_collection (pymongo.collection.Collection): MongoDB collection to log the search requests.

    Returns:
        None: The function handles user interaction, executes searches,
        and logs results, but does not return a value.

    Notes:
        - Uses `safe_input` to handle user input safely.
        - Calls the corresponding flow functions based on the user's selection.
        - Loops until the user chooses to quit.
    """
    while True:
        print("""
=====================================SEARCH MENU========================================
Select criterion to search for a movie (1, 2, 3, 4 or Q):
1. Search by keyword.
2. Search by genre.
3. Search by year or range of years.
4. Search by genre and year range.
Q. Return to the previous menu.""")

        search_choice = safe_input(
            "Enter your search criterion: ",
            interrupt_msg="\033[31mThe user interrupted the search menu!\033[0m\nReturn to the main menu"
        )
        if search_choice is None:
            return

        if search_choice == "1":
            keyword_flow(cursor, mongo_collection)
        elif search_choice == "2":
            genres_flow(cursor, mongo_collection)
        elif search_choice == "3":
            years_flow(cursor, mongo_collection)
        elif search_choice == "4":
            genre_years_flow(cursor, mongo_collection)
        elif search_choice.lower() == "q":
            break
        else:
            print("\033[31mInvalid criterion. Please try again.\033[0m")
