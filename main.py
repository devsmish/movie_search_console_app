def main():
    print("Movie Search App started")

    print("""
=========================SEARCH MENU=========================""")

    while True:
        print("""
========================ГЛАВНОЕ МЕНЮ=========================
Выберите опцию, которой вы хотели бы воспользоваться (1, 2 или 0):
1. Если хотите найти фильм.
2. Если хотите посмотреть статистику поиска.
0. Если хотите завершить программу.""")
        initial_choice = input("Enter your option: ")
        if initial_choice == "1":
            while True:
                print("""
=========================МЕНЮ ПОИСКА=========================
Выберите критерий для поиска фильма (1, 2 или 0):
1. Поиск по ключевому слову.
2. Поиск по жанру или году выпуска.
0. Вернуться в предыдущее меню.""")
                search_choice = input("Enter your criterion: ")
                if search_choice == "1":
                    pass
                elif search_choice == "2":
                    pass
                elif search_choice == "0":
                    break
                else:
                    print("Invalid criterion. Please try again.")
        elif initial_choice == "2":
            while True:
                print("""
======================МЕНЮ СТАТИСТИКИ========================
Выберите вариант статистики для просмотра (1, 2 или 0):
1. ТОП5 поисковых запросов.
2. 5 последних поисковых запросов.
0. Вернуться в предыдущее меню.""")
                statistic_choice = input("Enter your statistic: ")
                if statistic_choice == "1":
                    pass
                elif statistic_choice == "2":
                    pass
                elif statistic_choice == "0":
                    break
                else:
                    print("Invalid criterion. Please try again.")
        elif initial_choice == "0":
            print("App closed. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
    