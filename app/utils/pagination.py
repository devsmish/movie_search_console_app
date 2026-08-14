from app.utils.input_utils import safe_input
from app.i18n.translator import t


def print_results_paginated(results: list[dict], page_size: int = 10) -> None:
    """
    Displays a list of results in a paginated format in the console.

    The function prints results page by page, showing film details such as
    film_id, title, genre, and release year. Users can navigate using
    'n' (next page), 'p' (previous page), or 'q' (exit).

    Args:
        results (list[dict]): A list of dictionaries, each representing a film/document
            with at least the keys: 'film_id', 'title', 'name' (genre), and 'release_year'.
        page_size (int, optional): Number of results displayed per page. Defaults to 10.

    Returns:
        None: Prints results directly to the console; does not return any value.

    Raises:
        KeyError: If any expected key ('film_id', 'title', 'name', 'release_year') is missing in a result.

    Notes:
        - Column headers are localized; film/genre data itself comes from
          the database (Sakila dataset) and is not translated.
    """
    total = len(results)
    if total == 0:
        print(t("pagination.nothing_found"))
        return
    print(f"\n{t('pagination.results_found', total=total)}")

    current_page = 0
    total_pages = (total - 1) // page_size + 1

    while True:
        start = current_page * page_size
        end = start + page_size
        page_results = results[start:end]
        print(f"\n                            {t('pagination.page_indicator', current=current_page + 1, total=total_pages)}                      ")
        print(f"\n{t('pagination.col_num'):<5}| {t('pagination.col_film_id'):<8}| {t('pagination.col_title'):<34}| {t('pagination.col_genre'):<21}| {t('pagination.col_year'):>12}")
        print("-" * 88)
        for i, row in enumerate(page_results, start=1):
            print(f"{i:<5}| {row['film_id']:<8}| {row['title']:<34}| {row['name']:<21}| {row['release_year']:>12}")

        navigation = []
        if current_page > 0:
            navigation.append(t("pagination.nav_prev"))
        if current_page < total_pages - 1:
            navigation.append(t("pagination.nav_next"))
        navigation.append(t("pagination.nav_exit"))
        print("\n" + " | ".join(navigation))

        choice = safe_input(
            t("pagination.input_prompt"),
            interrupt_msg=f"\033[31m{t('pagination.interrupt')}\033[0m\n"
        )

        if choice is None:
            print(t("pagination.exit_message"))
            break
        elif choice == "n" and current_page < total_pages - 1:
            current_page += 1
        elif choice == "p" and current_page > 0:
            current_page -= 1
        elif choice == "q":
            print(t("pagination.exit_message"))
            break
        else:
            print(f"\033[31m{t('pagination.unavailable')}\033[0m")
