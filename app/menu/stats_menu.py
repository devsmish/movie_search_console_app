from app.utils.input_utils import safe_input
from app.services.stats_service import (
    activity_by_day_requests,
    avg_duration_requests,
    last5_requests,
    search_type_breakdown_requests,
    success_rate_requests,
    top5_requests,
    zero_result_requests,
)
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
    - Zero-result queries
    - Search type breakdown
    - Average duration by search type
    - Search activity by day
    - Success rate by search type

    Args:
        mongo_collection (pymongo.collection.Collection): MongoDB collection containing search logs.

    Returns:
        None: The function prints the selected report to the console and does not return any value.

    Notes:
        - Uses `safe_input` to handle user input safely.
        - The menu loops until the user chooses to quit.
    """
    while True:
        print(f"""
{banner('menu.stats.header')}
{t('menu.stats.prompt')}
{t('menu.stats.option_top5')}
{t('menu.stats.option_last5')}
{t('menu.stats.option_zero_results')}
{t('menu.stats.option_search_type_breakdown')}
{t('menu.stats.option_avg_duration')}
{t('menu.stats.option_activity_by_day')}
{t('menu.stats.option_success_rate')}
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
        elif statistic_choice == "3":
            zero_result_requests(mongo_collection)
        elif statistic_choice == "4":
            search_type_breakdown_requests(mongo_collection)
        elif statistic_choice == "5":
            avg_duration_requests(mongo_collection)
        elif statistic_choice == "6":
            activity_by_day_requests(mongo_collection)
        elif statistic_choice == "7":
            success_rate_requests(mongo_collection)
        elif statistic_choice.lower() == "q":
            break
        else:
            print(f"\033[31m{t('errors.invalid_choice')}\033[0m")
