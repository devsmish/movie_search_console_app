from app.sql_connection import keywords_search, list_genres, range_years, combined_search
from app.mongo_connection import top5_requests, last5_requests
import datetime


def search_menu(cursor, mongo_collection):
    while True:
        print("""
========================МЕНЮ ПОИСКА=========================
Выберите критерий для поиска фильма (1, 2 или 0):
1. Поиск по ключевому слову.
2. Поиск по жанру или году выпуска.
0. Вернуться в предыдущее меню.""")
        search_choice = input("Enter your criterion: ")
        if search_choice == "1":
            get_keyword(cursor, mongo_collection)
        elif search_choice == "2":
            selection_genre(cursor, mongo_collection)
        elif search_choice == "0":
            break
        else:
            print("Invalid criterion. Please try again.")

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
            print("Invalid criterion. Please try again.")


def input_keyword():
    print("""
====================ВВОД КЛЮЧЕВОГО СЛОВА====================
Введите слово или фразу для поиска фильма либо 0, чтобы вернуться в предыдущее меню.""")

    return input("Enter your keyword: ")

def search_by_keyword(cursor, keyword):
    return keywords_search(keyword, cursor)

def log_keyword_search(mongo_collection, keyword, total, duration):
    mongo_collection.insert_one(
        {
            "timestamp": datetime.datetime.now(),
            "search_type": "keyword",
            "params": {
                "keyword": keyword,
            },
            "results_count": total,
            "duration_ms": duration,
            "success": True,
            "query_key": keyword
        }
    )

def print_keyword_results(results):
    if not results:
        print("Ничего не найдено")
        return
    for num, row in enumerate(results, start=1):
        print(f"{num}. {row}")

def get_keyword(cursor, mongo_collection):
    while True:
        keyword = input_keyword()

        if keyword == "":
            print("Пустой выбор. Попробуйте снова")
            continue

        if keyword == "0":
            break

        start_time = datetime.datetime.now()
        results = search_by_keyword(cursor, keyword)
        end_time = datetime.datetime.now()

        duration = (end_time - start_time).total_seconds() * 1000

        print_keyword_results(results)

        log_keyword_search(
            mongo_collection,
            keyword,
            len(results),
            duration
        )

def show_years(genre, cursor):
    result = range_years(genre, cursor)
    for row in result:
        print(f"Вы можете указать диапазон годов от {row['min_year']} до {row['max_year']}")

def selection_genre(cursor, mongo_collection):
    while True:
        print("""
===================ВЫБОР ЖАНРА ИЗ СПИСКА====================
Выберите жанр по коду или названию из списка либо 0, чтобы вернуться в предыдущее меню.""")
        genres = list_genres(cursor)
        genre_names = [genre["name"] for genre in genres]
        for name in genre_names:
            print(name)
        genre_choice = input("Choice your genre: ")
        if genre_choice == "0":
            break
        elif genre_choice not in genre_names:
            print("Invalid genre. Please try again.")
        else:
            show_years(genre_choice, cursor)
            input_year(cursor, genre_choice, mongo_collection)

def get_year_range():
    print("""
=======================ДИАПАЗОН ГОДОВ=======================
0. Вернуться в предыдущее меню.""")

    try:
        start_year = int(input("Enter your start year: "))
        end_year = int(input("Enter your end year: "))
    except ValueError:
        print("Введите корректные числа")
        return None, None

    current_year = datetime.datetime.now().year

    if start_year > end_year:
        print("Start year cannot be greater than end year")
        return None, None

    if start_year <= 1900 or end_year > current_year:
        print("Invalid year. Please try again.")
        return None, None

    return start_year, end_year

def print_genre_results(results):
    if not results:
        print("Ничего не найдено")
        return
    for num, row in enumerate(results, start=1):
        print(f"{num}. {row['film_id']} - {row['title']}, {row['name']}, {row['release_year']}, {row['description']}")

def log_genre_years_search(mongo_collection, genre, start_year, end_year, total, duration):
    mongo_collection.insert_one(
        {
            "timestamp": datetime.datetime.now(),
            "search_type": "genres-years",
            "params": {
                "genres": genre,
                "years": {
                    "start_year": start_year,
                    "end_year": end_year,
                }
            },
            "results_count": total,
            "duration_ms": duration,
            "success": True,
            "query_key": f"{genre}_{start_year}_{end_year}"
        }
    )

def input_year(cursor, genre_choice, mongo_collection):
    start_year, end_year = get_year_range()

    if start_year is None:
        return

    start_time = datetime.datetime.now()
    results = combined_search(cursor, genre_choice, start_year, end_year)
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000

    print_genre_results(results)

    log_genre_years_search(
        mongo_collection,
        genre_choice,
        start_year,
        end_year,
        len(results),
        duration
    )
