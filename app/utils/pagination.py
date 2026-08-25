import os

from app.utils.input_utils import safe_input
from app.utils.formatting import (
    Column,
    default_export_filename,
    format_table,
    to_csv,
    to_json,
    write_export_file,
)
from app.i18n.translator import t

# Directory export files are written to, relative to the process's
# working directory. Kept as a module constant (rather than hardcoded
# inline) so it's easy to find/change in one place.
EXPORT_DIR = "exports"


def _result_columns() -> list["Column"]:
    """
    Column definitions for the console table. Widths match the layout;
    format_table() now truncates any value that doesn't fit, instead of
    letting it silently push the table out of alignment.
    """
    return [
        Column(key="film_id", header=t("pagination.col_film_id"), max_width=8),
        Column(key="title", header=t("pagination.col_title"), max_width=34),
        Column(key="name", header=t("pagination.col_genre"), max_width=21),
        Column(key="release_year", header=t("pagination.col_year"), max_width=12, align="right"),
    ]


def _export_columns() -> list["Column"]:
    """
    Column definitions for CSV/JSON export. Unlike _result_columns(),
    max_width is left at its default and is simply ignored by
    to_csv()/to_json() — export formats never truncate. Also includes
    `description`, which the console table has no room to show but which
    every search query already fetches from the database.
    """
    return [
        Column(key="film_id", header=t("pagination.col_film_id")),
        Column(key="title", header=t("pagination.col_title")),
        Column(key="name", header=t("pagination.col_genre")),
        Column(key="release_year", header=t("pagination.col_year")),
        Column(key="description", header=t("pagination.col_description")),
    ]


def _export_results(results: list[dict]) -> None:
    """
    Prompts for an export format and writes the full result set (not
    just the currently-displayed page) to a timestamped file under
    EXPORT_DIR.

    Args:
        results (list[dict]): The complete, unpaginated result set.

    Returns:
        None: Prints a success or error message; writes a file as a
        side effect.
    """
    fmt = safe_input(
        t("pagination.export_prompt_format"),
        interrupt_msg=f"\033[31m{t('pagination.interrupt')}\033[0m\n",
    )
    if fmt is None:
        return
    if fmt not in ("csv", "json"):
        print(f"\033[31m{t('pagination.export_invalid_format')}\033[0m")
        return

    columns = _export_columns()
    text = to_csv(results, columns) if fmt == "csv" else to_json(results, columns)
    filepath = os.path.join(EXPORT_DIR, default_export_filename("search_results", fmt))

    try:
        write_export_file(text, filepath)
        print(t("pagination.export_success", count=len(results), path=filepath))
    except OSError as e:
        print(f"\033[31m{t('pagination.export_error', error=e)}\033[0m")


def print_results_paginated(results: list[dict], page_size: int = 10) -> None:
    """
    Displays a list of results in a paginated format in the console.

    The function prints results page by page, showing film details such as
    film_id, title, genre, and release year. Users can navigate using
    'n' (next page), 'p' (previous page), 'e' (export all results to a
    file), or 'q' (exit).

    Args:
        results (list[dict]): A list of dictionaries, each representing a film/document
            with at least the keys: 'film_id', 'title', 'name' (genre), and 'release_year'.
        page_size (int, optional): Number of results displayed per page. Defaults to 10.

    Returns:
        None: Prints results directly to the console; does not return any value.

    Notes:
        - Column headers are localized; film/genre data itself comes from
          the database (Sakila dataset) and is not translated.
        - Table rendering is delegated to app.utils.formatting.format_table(),
          which truncates any value too long for its column instead of
          letting it push the table out of alignment.
        - 'e' exports the *entire* result set (all pages), not just the
          page currently on screen, to CSV or JSON under EXPORT_DIR.
    """
    total = len(results)
    if total == 0:
        print(t("pagination.nothing_found"))
        return
    print(f"\n{t('pagination.results_found', total=total)}")

    columns = _result_columns()
    current_page = 0
    total_pages = (total - 1) // page_size + 1

    while True:
        start = current_page * page_size
        end = start + page_size
        page_results = results[start:end]
        print(f"\n                            {t('pagination.page_indicator', current=current_page + 1, total=total_pages)}                      ")
        print(f"\n{format_table(page_results, columns, numbered=True, num_header=t('pagination.col_num'))}")

        navigation = []
        if current_page > 0:
            navigation.append(t("pagination.nav_prev"))
        if current_page < total_pages - 1:
            navigation.append(t("pagination.nav_next"))
        navigation.append(t("pagination.nav_export"))
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
        elif choice == "e":
            _export_results(results)
        elif choice == "q":
            print(t("pagination.exit_message"))
            break
        else:
            print(f"\033[31m{t('pagination.unavailable')}\033[0m")
