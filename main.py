from app.func_menu import *
from app.sql_connection import get_connection


def main():
    print("Movie Search App started")
    connection = get_connection()
    cursor = connection.cursor()

    print("""
=========================SEARCH APP=========================""")

    while True:
        print("""
========================ГЛАВНОЕ МЕНЮ========================
Выберите опцию, которой вы хотели бы воспользоваться (1, 2 или 0):
1. Если хотите найти фильм.
2. Если хотите посмотреть статистику поиска.
0. Если хотите завершить программу.""")
        initial_choice = input("Enter your option: ")
        if initial_choice == "1":
            search_menu(cursor)
        elif initial_choice == "2":
            stats_menu()
        elif initial_choice == "0":
            print("App closed. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
