from app.sql_connection import keywords_search, list_genres, range_years, combined_search, years_search, genres_search
from app.mongo_connection import top5_requests, last5_requests
import datetime


def search_menu(cursor, mongo_collection):
    while True:
        print("""
========================МЕНЮ ПОИСКА=========================
Выберите критерий для поиска фильма (1, 2, 3, 4 или 0):
1. Поиск по ключевому слову.
2. Поиск по жанру.
3. Поиск по диапазону годов.
4. Поиск по жанру и диапазону годов.
0. Вернуться в предыдущее меню.""")
        search_choice = input("Enter your criterion: ")
        if search_choice == "1":
            keyword_flow(cursor, mongo_collection)
        elif search_choice == "2":
            genres_flow(cursor, mongo_collection)
        elif search_choice == "3":
            years_flow(cursor, mongo_collection)
        elif search_choice == "4":
            combined_flow(cursor, mongo_collection)
        elif search_choice == "0":
            break
        else:
            print("\033[31mInvalid criterion. Please try again.\033[0m")

def stats_menu(mongo_collection):
    while True:
        print("""
======================МЕНЮ СТАТИСТИКИ=======================
Выберите вариант статистики для просмотра (1, 2 или 0):
1. ТОП5 поисковых запросов.
2. 5 последних поисковых запросов.
0. Вернуться в предыдущее меню.""")
        statistic_choice = input("Enter your statistic: ")
        if statistic_choice == "1":
            top5_requests(mongo_collection)
        elif statistic_choice == "2":
            last5_requests(mongo_collection)
        elif statistic_choice == "0":
            break
        else:
            print("\033[31mInvalid criterion. Please try again.\033[0m")

def execute_search(search_func, mongo_collection, search_type, params):
    start_time = datetime.datetime.now()
    try:
        results = search_func()
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        results = []

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000

    print_results(results)

    log_request(
        mongo_collection,
        search_type,
        params,
        len(results),
        duration
    )

def build_query_key(search_type, params):
    if search_type == "keyword":
        return f"{search_type}_{params['keyword']}"

    if search_type == "genre":
        return f"{search_type}_{params['genre']}"

    if search_type == "years":
        return f"{search_type}_{params['start_year']}_{params['end_year']}"

    if search_type == "genre_years":
        return f"{search_type}_{params['genre']}_{params['start_year']}_{params['end_year']}"

def log_request(mongo_collection, search_type, params, total, duration):

    mongo_collection.insert_one(
        {
        "timestamp": datetime.datetime.now(),
        "search_type": search_type,
        "params": params,
        "results_count": total,
        "duration_ms": duration,
        "success": False if total == 0 else True,
        "query_key": build_query_key(search_type, params)
    }
    )

def input_keyword():
    print("""
====================ВВОД КЛЮЧЕВОГО СЛОВА====================
Введите слово или фразу для поиска фильма либо 0, чтобы вернуться в предыдущее меню.""")

    return input("Enter your keyword: ")

def print_results(results):
    if not results:
        print("Ничего не найдено")
        return
    for num, row in enumerate(results, start=1):
        print(f"{num}. {row['film_id']} - {row['title']}, {row['name']}, {row['release_year']}, {row['description']}")

def keyword_flow(cursor, mongo_collection):
    while True:
        keyword = input_keyword()
        if keyword == "":
            print("\033[31mПустой выбор. Попробуйте снова\033[0m")
            continue
        if keyword == "0":
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
===================ВЫБОР ЖАНРА ИЗ СПИСКА====================
Выберите жанр по коду или названию из списка либо 0, чтобы вернуться в предыдущее меню.""")
        genres = list_genres(cursor)
        genre_names = {genre['category_id']: genre["name"] for genre in genres}
        for num, name in genre_names.items():
            print(f"{num}. {name}")
        choice = input("Your choice: ").strip()
        if choice == "0":
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
            return int(year)
    else:
        year_int = year

    if year_int <= current_year:
        return 2000 + year_int
    else:
        return 1900 + year_int

def show_years(cursor):
    result = range_years(cursor)
    print(result)
    for row in result:
        print(f"Вы можете указать диапазон годов от {row['min_year']} до {row['max_year']}")

def get_year_range(min_year, max_year):
    user_input = input(f"Введите год или диапазон ({min_year}-{max_year}): ").strip()
    if not user_input:
        return None
    try:
        user_input = user_input.replace(" ", "-")
        user_input = user_input.replace("/", "-")
        if "-" in user_input:
            start, end = user_input.split("-")
            start_year = normalize_year_input(start)
            end_year = normalize_year_input(end)
        else:
            year = normalize_year_input(user_input)
            start_year = end_year = year
        if start_year > end_year:
            print("\033[31mStart year cannot be greater than end year!\033[0m")
            return None, None
        if start_year <= 1900 or end_year > datetime.datetime.now().year:
            print("\033[31mInvalid year. Please try again.\033[0m")
            return None, None
        return {
            "years": {
                "start_year": start_year,
                "end_year": end_year
            }
        }
    except ValueError:
        print("\033[31mВведите корректные числа\033[0m")
        return None

def years_flow(cursor, mongo_collection):
    print("""
=======================ДИАПАЗОН ГОДОВ=======================
Выберите год или диапазон годов либо 0 чтобы вернуться в предыдущее меню.""")
    min_year = 1990
    max_year = datetime.datetime.now().year
    show_years(cursor)
    params = get_year_range(min_year, max_year)
    if params is None:
        return
    flat_params = {
        "start_year": params["years"]["start_year"],
        "end_year": params["years"]["end_year"]
    }
    execute_search(
        search_func=lambda: years_search(
            cursor,
            params["years"]["start_year"],
            params["years"]["end_year"]
        ),
        mongo_collection=mongo_collection,
        search_type="years",
        params=flat_params
    )

def combined_flow(cursor, mongo_collection):
    genre = get_genres(cursor)
    if not genre:
        return

    params_years = get_year_range(1900, datetime.datetime.now().year)
    start_year = params_years["years"]["start_year"]
    end_year = params_years["years"]["end_year"]
    if not start_year:
        return

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
