def print_results_paginated(results, page_size=10):
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
