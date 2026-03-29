from app.sql_connection import keywords_search, list_genres, range_years, combined_search, years_search, genres_search
from app.mongo_connection import top5_requests, last5_requests
import datetime


def search_menu(cursor, mongo_collection):
    while True:
        print("""
=====================================SEARCH MENU========================================
Select criterion to search for a movie (1, 2, 3, 4 or Q):
1. Search by keyword.
2. Search by genre.
3. Search by year or range of years.
4. Search by genre and year range.
Q. Return to the previous menu.""")

        search_choice = safe_input(
            "Enter your search criterion: ",
            interrupt_msg="\033[31mThe user interrupted the search menu!\033[0m\nReturn to the main menu"
        )
        if search_choice is None:
            return

        if search_choice == "1":
            keyword_flow(cursor, mongo_collection)
        elif search_choice == "2":
            genres_flow(cursor, mongo_collection)
        elif search_choice == "3":
            years_flow(cursor, mongo_collection)
        elif search_choice == "4":
            combined_flow(cursor, mongo_collection)
        elif search_choice.lower() == "q":
            break
        else:
            print("\033[31mInvalid criterion. Please try again.\033[0m")

def stats_menu(mongo_collection):
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

def execute_search(search_func, mongo_collection, search_type, params):
    start_time = datetime.datetime.now()
    success = True
    results = []

    try:
        results = search_func()
    except Exception as e:
        print(f"EXECUTE_SEARCH: Error searching in the database or in the query: {e}")
        success = False

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000

    try:
        print_results_paginated(results)
    except Exception as e:
        print(f"EXECUTE_SEARCH: Results output error: {e}")

    try:
        log_request(
            mongo_collection,
            search_type,
            params,
            len(results),
            duration,
            success
        )
    except Exception as e:
        print(f"EXECUTE_SEARCH: Logging error: {e}")

def build_query_key(search_type, params):
    try:
        if search_type == "keyword":
            return f"{search_type}_{params['keyword']}"
        if search_type == "genre":
            return f"{search_type}_{params['genre']}"
        if search_type == "years":
            return f"{search_type}_{params['start_year']}_{params['end_year']}"
        if search_type == "genre_years":
            return f"{search_type}_{params['genre']}_{params['start_year']}_{params['end_year']}"
    except KeyError as e:
        print(f"UNKNOWN_QUERY: Error in keys: {e}")
        return "unknown_query"

def log_request(mongo_collection, search_type, params, total, duration, success):
    try:
        mongo_collection.insert_one(
            {
            "timestamp": datetime.datetime.now(),
            "search_type": search_type,
            "params": params,
            "results_count": total,
            "duration_ms": duration,
            "success": success,
            "query_key": build_query_key(search_type, params)
        }
        )
    except Exception as e:
        print("LOG_REQUEST: Connection error or invalid document generated")
        print(f"MongoDB write error: {e}")

def input_keyword():
    print("""
=====================================ENTER KEYWORD======================================
Enter a word or phrase to search for a movie, or [q] to return to the previous menu.""")
    input_word = safe_input(
        "Enter your keyword: ",
        interrupt_msg="INPUT_KEYWORD: \033[31mThe user interrupted the program!\033[0m\n"
    )
    if input_word is None:
        return None
    return input_word

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
\n                        -------  Page  {current_page + 1}  of  {total_pages}  -------                        \n""")
        print(f"#    | Film_ID | Title                             | Genre                | Release Year")
        for i, row in enumerate(page_results, start=start + 1):
            try:
                print(f"""
{i:<5}| {row['film_id']:<8}| {row['title']:<34}| {row['name']:<21}| {row['release_year']:>12}""")
            except Exception as e:
                print(f"Line display error: {e}")

        nav = []
        if current_page > 0:
            nav.append("[p] Previous page")
        if current_page < total_pages - 1:
            nav.append("[n] Next page")
        nav.append("[q] Exit")
        print("\n" + " | ".join(nav))

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

def keyword_flow(cursor, mongo_collection):
    while True:
        keyword = input_keyword()
        if keyword is None:
            print("Return to search menu")
            break
        if keyword == "":
            print("\033[31mEmpty selection. Try again.\033[0m")
            continue
        if keyword == "q":
            break

        execute_search(
            search_func=lambda: keywords_search(keyword, cursor),
            mongo_collection=mongo_collection,
            search_type="keyword",
            params={"keyword": keyword}
        )

def get_genres(cursor):
    while True:
        print("""
=============================SELECT A GENRE FROM THE LIST===============================
Select a genre by number or title from the list or [q] to return to the previous menu.""")
        try:
            genres = list_genres(cursor)
        except Exception as e:
            print(f"GET_GENRES: Error loading genres: {e}")
            return None
        try:
            genre_names = {genre['category_id']: genre["name"] for genre in genres}
        except KeyError as e:
            print(f"GET_GENRES: Data structure error: {e}")
            return None
        print(f"#   | Genre")
        for num, name in genre_names.items():
            print(f"{num:<4}| {name:<16}")
        choice = input("""
Select a genre by number or title. 
Press [q] to return to the previous menu: """).strip()
        if choice == "q":
            return None
        if choice.isdigit():
            genre = genre_names.get(int(choice))
            if genre:
                return genre
        else:
            for name in genre_names.values():
                if choice.lower() == name.lower():
                    return name
        print("\033[31mInvalid genre. Try again.\033[0m")

def genres_flow(cursor, mongo_collection):
    while True:
        genre = get_genres(cursor)
        if genre is None:
            break
        execute_search(
            search_func=lambda: genres_search(cursor, genre),
            mongo_collection=mongo_collection,
            search_type="genre",
            params={"genre": genre}
        )

def normalize_year_input(year):
    current_year = datetime.datetime.now().year % 100  # последние 2 цифры

    if isinstance(year, str):
        year = year.strip()
        if len(year) == 2 and year.isdigit():
            year_int = int(year)
        else:
            try:
                return int(year)
            except ValueError:
                raise ValueError("\033[31mIncorrect year!\033[0m")
    else:
        year_int = year

    if year_int <= current_year:
        return 2000 + year_int
    else:
        return 1900 + year_int

def show_years(cursor):
    try:
        result = range_years(cursor)
    except Exception as e:
        print(f"Error getting year range: {e}")
        return
    for row in result:
        print(f"You can specify a range of years from {row['min_year']} to {row['max_year']}")

def get_year_range(min_year, max_year):
    while True:
        user_input = input(f"""
Enter a year or range ({min_year}-{max_year}) or [q] to return to the previous menu: """"").strip()

        if user_input == "q":
            return None

        if not user_input:
            print("\033[31mEmpty input. Try again.\033[0m")
            continue

        try:
            user_input = user_input.replace(" ", "-")
            user_input = user_input.replace("/", "-")
            if "-" in user_input:
                parts = user_input.split("-")
                if len(parts) != 2:
                    raise ValueError

                start = normalize_year_input(parts[0])
                end = normalize_year_input(parts[1])
            else:
                year = normalize_year_input(user_input)
                start = end = year

            if start > end:
                print("\033[31mStart year cannot be greater than end year!\033[0m")
                continue

            if start < min_year or end > max_year:
                print("\033[31mYear out of range\033[0m")
                continue

            return {
                "start_year": start,
                "end_year": end
            }

        except ValueError:
            print("\033[31mPlease enter the correct format (for example: 2000-2010, 2000/2010 or 2000 2010)\033[0m")

def years_flow(cursor, mongo_collection):
    print("""
=====================================RANGE OF YEARS=====================================
Select a year or range of years or [q] to return to the previous menu.""")
    min_year = 1990
    max_year = datetime.datetime.now().year - 1
    show_years(cursor)
    params = get_year_range(min_year, max_year)
    if params is None:
        return
    execute_search(
        search_func=lambda: years_search(
            cursor,
            params["start_year"],
            params["end_year"]
        ),
        mongo_collection=mongo_collection,
        search_type="years",
        params=params
    )

def combined_flow(cursor, mongo_collection):
    genre = get_genres(cursor)
    if not genre:
        return

    params_years = get_year_range(1900, datetime.datetime.now().year)
    if not params_years:
        return

    start_year = params_years["start_year"]
    end_year = params_years["end_year"]

    execute_search(
        search_func=lambda: combined_search(cursor, genre, start_year, end_year),
        mongo_collection=mongo_collection,
        search_type="genre_years",
        params={
            "genre": genre,
            "start_year": start_year,
            "end_year": end_year
        }
    )

def safe_input(prompt, interrupt_msg=None, allow_empty=True):
    try:
        value = input(prompt).strip()

        if not allow_empty and value == "":
            print("\033[31mEmpty input is not allowed\033[0m")
            return None

        return value

    except KeyboardInterrupt:
        print(f"\033[31m{interrupt_msg or 'Input interrupted by user'}\033[0m")
        return None
