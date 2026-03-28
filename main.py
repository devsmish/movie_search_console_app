from app.func_menu import search_menu, stats_menu, safe_input
from app.sql_connection import get_connection
from app.mongo_connection import get_mongo_collection


def main():
    print("Movie Search App started")

    try:
        connection = get_connection()
        cursor = connection.cursor()
        mongo_collection = get_mongo_collection()
    except Exception as e:
        print(f"\033[31mStartup error: {e}\033[0m")
        return

    print("""
=========================SEARCH APP=========================""")

    while True:
        print("""
========================ГЛАВНОЕ МЕНЮ========================
Выберите опцию, которой вы хотели бы воспользоваться (1, 2 или Q):
1. Если хотите найти фильм.
2. Если хотите посмотреть статистику поиска.
Q. Если хотите завершить программу.""")
        initial_choice = safe_input(
            "Enter your option: ",
            interrupt_msg="\033[31mThe user terminated the program!\033[0m\nThe program was closed."
        )
        if initial_choice is None:
            return

        if initial_choice == "1":
            search_menu(cursor, mongo_collection)
        elif initial_choice == "2":
            stats_menu(mongo_collection)
        elif initial_choice.lower() == "q":
            print("App closed. Goodbye!")
            break
        else:
            print("\033[31mInvalid choice. Please try again.\033[0m")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
