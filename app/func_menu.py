from app.sql_connection import keywords_search, list_genres, range_years, combined_search, years_search, genres_search
from app.mongo_connection import top5_requests, last5_requests
import datetime


def search_menu(cursor, mongo_collection):
    while True:
        print("""
========================МЕНЮ ПОИСКА=========================
Выберите критерий для поиска фильма (1, 2, 3, 4 или Q):
1. Поиск по ключевому слову.
2. Поиск по жанру.
3. Поиск по диапазону годов.
4. Поиск по жанру и диапазону годов.
Q. Вернуться в предыдущее меню.""")
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
======================МЕНЮ СТАТИСТИКИ=======================
Выберите вариант статистики для просмотра (1, 2 или Q):
1. ТОП5 поисковых запросов.
2. 5 последних поисковых запросов.
Q. Вернуться в предыдущее меню.""")
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
        print(f"EXECUTE_SEARCH: Ошибка поиска в БД или в запросе: {e}")
        success = False

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000

    try:
        print_results_paginated(results)
    except Exception as e:
        print(f"EXECUTE_SEARCH: Ошибка вывода результатов: {e}")

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
        print(f"EXECUTE_SEARCH: Ошибка логирования: {e}")

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
        print(f"UNKNOWN_QUERY: Ошибка в ключах: {e}")
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
        print("LOG_REQUEST: Ошибка соединения или сформирован некорректный документ")
        print(f"Ошибка записи в MongoDB: {e}")

def input_keyword():
    print("""
====================ВВОД КЛЮЧЕВОГО СЛОВА====================
Введите слово или фразу для поиска фильма либо [q], чтобы вернуться в предыдущее меню.""")
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
        print("Ничего не найдено")
        return
    print(f"\nНайдено результатов: {total}")

    current_page = 0
    total_pages = (total - 1) // page_size + 1

    while True:
        start = current_page * page_size
        end = start + page_size
        page_results = results[start:end]
        print(f"\n--- Страница {current_page + 1} из {total_pages} ---")
        for i, row in enumerate(page_results, start=start + 1):
            try:
                print(f"{i}. {row['film_id']} - {row['title']}, {row['name']}, {row['release_year']}")
            except Exception as e:
                print(f"Ошибка отображения строки: {e}")

        nav = []
        if current_page > 0:
            nav.append("[p] Назад")
        if current_page < total_pages - 1:
            nav.append("[n] Вперед")
        nav.append("[q] Выход")
        print("\n" + " | ".join(nav))

        choice = input("Ваш выбор: ").strip().lower()

        if choice == "n" and current_page < total_pages - 1:
            current_page += 1
        elif choice == "p" and current_page > 0:
            current_page -= 1
        elif choice == "q":
            print("Выход из просмотра результатов")
            break
        else:
            print("\033[31mНедоступная команда\033[0m")

def keyword_flow(cursor, mongo_collection):
    while True:
        keyword = input_keyword()
        if keyword is None:
            print("Возврат в меню...")
            break
        if keyword == "":
            print("\033[31mПустой выбор. Попробуйте снова\033[0m")
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
===================ВЫБОР ЖАНРА ИЗ СПИСКА====================
Выберите жанр по коду или названию из списка либо [q], чтобы вернуться в предыдущее меню.""")
        try:
            genres = list_genres(cursor)
        except Exception as e:
            print(f"GET_GENRES: Ошибка загрузки жанров: {e}")
            return None
        try:
            genre_names = {genre['category_id']: genre["name"] for genre in genres}
        except KeyError as e:
            print(f"GET_GENRES: Ошибка структуры данных: {e}")
            return None
        for num, name in genre_names.items():
            print(f"{num}. {name}")
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
        print(f"Ошибка получения диапазона лет: {e}")
        return
    for row in result:
        print(f"Вы можете указать диапазон годов от {row['min_year']} до {row['max_year']}")

def get_year_range(min_year, max_year):
    while True:
        user_input = input(f"Введите год или диапазон ({min_year}-{max_year}) или [q] для выхода: ").strip()

        if user_input == "q":
            return None

        if not user_input:
            print("\033[31mПустой ввод\033[0m")
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
                print("\033[31mГод вне допустимого диапазона\033[0m")
                continue

            return {
                "start_year": start,
                "end_year": end
            }

        except ValueError:
            print("\033[31mВведите корректный формат (например: 2000-2010, 2000/2010 или 2000 2010)\033[0m")

def years_flow(cursor, mongo_collection):
    print("""
=======================ДИАПАЗОН ГОДОВ=======================
Выберите год или диапазон годов либо [q] чтобы вернуться в предыдущее меню.""")
    min_year = 1990
    max_year = datetime.datetime.now().year
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
            print("\033[31mПустой ввод запрещён\033[0m")
            return None

        return value

    except KeyboardInterrupt:
        print(f"\033[31m{interrupt_msg or 'Ввод прерван пользователем'}\033[0m")
        return None
