from app.sql_connection import *
from app.mongo_connection import *
import datetime


def search_menu(cursor):
    while True:
        print("""
========================МЕНЮ ПОИСКА=========================
Выберите критерий для поиска фильма (1, 2 или 0):
1. Поиск по ключевому слову.
2. Поиск по жанру или году выпуска.
0. Вернуться в предыдущее меню.""")
        search_choice = input("Enter your criterion: ")
        if search_choice == "1":
            input_keyword(cursor)
        elif search_choice == "2":
            input_genre(cursor)
        elif search_choice == "0":
            break
        else:
            print("Invalid criterion. Please try again.")

def stats_menu():
    while True:
        print("""
======================МЕНЮ СТАТИСТИКИ=======================
Выберите вариант статистики для просмотра (1, 2 или 0):
1. ТОП5 поисковых запросов.
2. 5 последних поисковых запросов.
0. Вернуться в предыдущее меню.""")
        statistic_choice = input("Enter your statistic: ")
        if statistic_choice == "1":
            top5_requests()
        elif statistic_choice == "2":
            last5_requests()
        elif statistic_choice == "0":
            break
        else:
            print("Invalid criterion. Please try again.")

def input_keyword(cursor):
    while True:
        print("""
====================ВВОД КЛЮЧЕВОГО СЛОВА====================
Введите слово или фразу для поиска фильма
0. Вернуться в предыдущее меню.""")
        keyword = input("Enter your keyword: ")
        if keyword == "":
            print("Пустой выбор. Попробуйте ввести ключевое слово повторно")
        elif keyword == "0":
            break
        else:
            results = keywords_search(keyword, cursor)
            for row in results:
                print(row)

def show_genres(cursor):
    return list_genres(cursor)

def show_years(genre, cursor):
    result = range_years(genre, cursor)
    for row in result:
        print(f"Вы можете указать диапазон годов от {row['min_year']} до {row['max_year']}")

def input_genre(cursor):
    while True:
        print("""
===================ВЫБОР ЖАНРА ИЗ СПИСКА====================
0. Вернуться в предыдущее меню.""")
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
            input_year(cursor, genre_choice)

def input_year(cursor, genre_choice):
    print("""
=======================ДИАПАЗОН ГОДОВ=======================
0. Вернуться в предыдущее меню.""")
    try:
        start_year = int(input("Enter your start year: "))
        end_year = int(input("Enter your end year: "))
    except ValueError:
        print("Введите корректные числа")
        return
    if start_year <= 1900 or end_year > datetime.datetime.now().year:
        print("Invalid year. Please try again.")
    else:
        result = combined_search(cursor, genre_choice, start_year, end_year)
        for num, row in enumerate(result, start=1):
            # print(f"{num}. {row}")
            print(f"{num}. {row['film_id']} - {row['title']}, {row['name']}, {row['release_year']}, {row['description']}")
