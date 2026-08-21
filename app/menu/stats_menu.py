from app.utils.input_utils import safe_input
from app.services.stats_service import top5_requests, last5_requests
from app.i18n.translator import t, banner
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
        print(f"""
{banner('menu.stats.header')}
{t('menu.stats.prompt')}
{t('menu.stats.option_top5')}
{t('menu.stats.option_last5')}
{t('menu.stats.option_back')}""")
        statistic_choice = safe_input(
            t("menu.stats.input_prompt"),
            interrupt_msg=f"\033[31m{t('menu.stats.interrupt')}\033[0m"
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
            print(f"\033[31m{t('errors.invalid_choice')}\033[0m")
