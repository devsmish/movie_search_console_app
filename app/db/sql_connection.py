import pymysql
from config import Config
from pymysql.cursors import DictCursor
from app.db.sql_queries import *


def get_connection():
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            cursorclass=DictCursor
        )

        connection.ping(reconnect=True)

        print("MySQL OK")
        return connection

    except Exception as e:
        raise Exception(f"MySQL connection error: {e}")

def keywords_search(keyword, cursor):
    cursor.execute(keyword_query, (f"%{keyword}%",))
    return cursor.fetchall()

def list_genres(cursor):
    cursor.execute(genres_list)
    return cursor.fetchall()

def genre_years_search(cursor, genre, start_year=1990, end_year=2025):
    cursor.execute(genres_years_query, (genre, start_year, end_year,))
    return cursor.fetchall()

def years_search(cursor, start_year=1990, end_year=2025):
    cursor.execute(years_query, (start_year, end_year,))
    return cursor.fetchall()

def genres_search(cursor, genre):
    cursor.execute(genres_query, (genre,))
    return cursor.fetchall()

def range_years(cursor):
    cursor.execute(range_years_query)
    return cursor.fetchall()
