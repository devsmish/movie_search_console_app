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
    """
    total = len(results)
    if total == 0:
        print("Nothing found!")
        return
    print(f"\nResults found: {total}")

    current_page = 0
    total_pages = (total - 1) // page_size + 1

    while True:
        start = current_page * page_size
        end = start + page_size
        page_results = results[start:end]
        print(f"""
                            -------  Page  {current_page + 1}  of  {total_pages}  -------                      """)
        print(f"\n#    | Film_ID | Title                             | Genre                | Release Year")
        print("-" * 88)
        for i, row in enumerate(page_results, start=1):
            print(f"{i:<5}| {row['film_id']:<8}| {row['title']:<34}| {row['name']:<21}| {row['release_year']:>12}")

        navigation = []
        if current_page > 0:
            navigation.append("[p] Previous page")
        if current_page < total_pages - 1:
            navigation.append("[n] Next page")
        navigation.append("[q] Exit")
        print("\n" + " | ".join(navigation))

        choice = input("Your choice: ").strip().lower()

        if choice == "n" and current_page < total_pages - 1:
            current_page += 1
        elif choice == "p" and current_page > 0:
            current_page -= 1
        elif choice == "q":
            print("Exit viewing results")
            break
        else:
            print("\033[31mUnavailable command\033[0m")
