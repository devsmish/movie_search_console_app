from app.db.sql_connection import get_connection
from app.db.mongo_connection import get_mongo_collection
from app.utils.input_utils import safe_input
from app.menu.search_menu import search_menu
from app.menu.stats_menu import stats_menu


def main_menu():
    print("Movie Search App started")

    try:
        connection = get_connection()
        cursor = connection.cursor()
        mongo_collection = get_mongo_collection()
    except Exception as e:
        print(f"\033[31mStartup error: {e}\033[0m")
        return

    print("""
====================================MOVIE SEARCH APP====================================""")

    while True:
        print("""
=======================================MAIN MENU========================================
Select the option You would like to use (1, 2 or Q):
1. Searching for a movie in the library.
2. View Your search history or popular queries.
Q. Exit the program.""")
        initial_choice = safe_input(
            "Enter your option: ",
            interrupt_msg="\033[31mThe user terminated the program!\033[0m\nThe program was closed."
        )
        if initial_choice is None:
            return
        if initial_choice == "":
            print("\033[31mEmpty input is not allowed. Please try again.\033[0m")
            continue

        if initial_choice == "1":
            search_menu(cursor, mongo_collection)
        elif initial_choice == "2":
            stats_menu(mongo_collection)
        elif initial_choice.lower() == "q":
            print("App closed. Goodbye!")
            break
        else:
            print("\033[31mInvalid choice. Please try again.\033[0m")

    cursor.close()
    connection.close()
