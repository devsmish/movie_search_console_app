from app.db.sql_connection import get_connection
from app.db.mongo_connection import get_mongo_collection
from app.utils.input_utils import safe_input
from app.utils.console_colors import red
from app.menu.search_menu import search_menu
from app.menu.stats_menu import stats_menu
from app.i18n.translator import t, banner
from config import Config, ConfigError


def main_menu() -> None:
    """
    Entry point and main menu for the Movie Search App.

    Validates required configuration, establishes connections to the SQL
    database and MongoDB, then displays the main menu to the user. Allows
    navigation to movie searches or statistics reports.

    Args:
        None

    Returns:
        None: Handles user interaction, executes searches and statistics
        flows, and closes database connections on exit.

    Notes:
        - Uses `safe_input` to handle user input safely.
        - Calls `Config.validate()` first, so a missing/misnamed .env
          variable is reported clearly instead of surfacing as a
          confusing low-level pymysql/pymongo connection error.
        - Initializes `cursor` for SQL database operations.
        - Initializes `mongo_collection` for logging search requests.
        - Loops until the user chooses to exit the program.
        - Closes database connections when exiting.
    """
    print(t("app.started"))

    try:
        Config.validate()
        connection = get_connection()
        cursor = connection.cursor()
        mongo_collection = get_mongo_collection()
    except ConfigError as e:
        print(red(t("config.missing_vars", vars=", ".join(e.missing))))
        return
    except Exception as e:
        print(red(t("app.startup_error", error=e)))
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
                interrupt_msg=red(t("menu.main.interrupt"))
            )
            if initial_choice is None:
                return
            if initial_choice == "":
                print(red(t("errors.empty_input")))
                continue

            if initial_choice == "1":
                search_menu(cursor, mongo_collection)
            elif initial_choice == "2":
                stats_menu(mongo_collection)
            elif initial_choice.lower() == "q":
                print(t("menu.main.goodbye"))
                break
            else:
                print(red(t("errors.invalid_choice")))
    finally:
        cursor.close()
        connection.close()
