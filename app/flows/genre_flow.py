from app.db.sql_connection import list_genres, genres_search
from app.services.search_service import execute_search


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
