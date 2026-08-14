from app.db.sql_connection import get_connection
from app.db.mongo_connection import get_mongo_collection
from app.utils.input_utils import safe_input
from app.menu.search_menu import search_menu
from app.menu.stats_menu import stats_menu
from app.i18n.translator import t, banner


def main_menu() -> None:
    """
    Entry point and main menu for the Movie Search App.

    Establishes connections to the SQL database and MongoDB, then displays
    the main menu to the user. Allows navigation to movie searches or
    statistics reports.

    Args:
        None

    Returns:
        None: Handles user interaction, executes searches and statistics
        flows, and closes database connections on exit.

    Notes:
        - Uses `safe_input` to handle user input safely.
        - Initializes `cursor` for SQL database operations.
        - Initializes `mongo_collection` for logging search requests.
        - Loops until the user chooses to exit the program.
        - Closes database connections when exiting.
    """
    print(t("app.started"))

    try:
        connection = get_connection()
        cursor = connection.cursor()
        mongo_collection = get_mongo_collection()
    except Exception as e:
        print(f"\033[31m{t('app.startup_error', error=e)}\033[0m")
        return

    print(f"\n{banner('app.banner_title')}")

    try:
        while True:
            print(f"""
{banner('menu.main.header')}
{t('menu.main.prompt')}
{t('menu.main.option_search')}
{t('menu.main.option_stats')}
{t('menu.main.option_exit')}""")
            initial_choice = safe_input(
                t("menu.main.input_prompt"),
                interrupt_msg=f"\033[31m{t('menu.main.interrupt')}\033[0m"
            )
            if initial_choice is None:
                return
            if initial_choice == "":
                print(f"\033[31m{t('errors.empty_input')}\033[0m")
                continue

            if initial_choice == "1":
                search_menu(cursor, mongo_collection)
            elif initial_choice == "2":
                stats_menu(mongo_collection)
            elif initial_choice.lower() == "q":
                print(t("menu.main.goodbye"))
                break
            else:
                print(f"\033[31m{t('errors.invalid_choice')}\033[0m")
    finally:
        cursor.close()
        connection.close()
