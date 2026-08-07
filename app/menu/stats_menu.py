from app.utils.input_utils import safe_input
from app.services.stats_service import top5_requests, last5_requests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymongo.collection


def stats_menu(mongo_collection: "pymongo.collection.Collection") -> None:
    """
    Displays the statistics menu for MongoDB search logs.

    Allows the user to select between different reports:
    - Top-5 most frequent search queries
    - 5 most recent search queries

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the selected report to the console and does not return any value.

    Notes:
        - Uses `safe_input` to handle user input safely.
        - Calls `top5_requests` or `last5_requests` depending on user selection.
        - The menu loops until the user chooses to quit.
    """
    while True:
        print("""
===================================STATISTICS MENU======================================
Select a report option to view (1, 2 or Q):
1. TOP-5 search queries.
2. 5 most recent search queries.
Q. Return to the previous menu.""")
        statistic_choice = safe_input(
            "Choice your statistic report: ",
            interrupt_msg="\033[31mThe user interrupted the statistic menu!\033[0m\nReturn to the main menu"
        )
        if statistic_choice is None:
            return

        if statistic_choice == "1":
            top5_requests(mongo_collection)
        elif statistic_choice == "2":
            last5_requests(mongo_collection)
        elif statistic_choice.lower() == "q":
            break
        else:
            print("\033[31mInvalid criterion. Please try again.\033[0m")
