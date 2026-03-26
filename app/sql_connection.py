import pymysql
from config import Config
from pymysql.cursors import DictCursor
from app.sql_queries import *


def get_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        cursorclass=DictCursor
    )

def keywords_search(keyword, cursor):
    cursor.execute(keyword_query, (f"%{keyword}%",))
    return cursor.fetchall()

def list_genres(cursor):
    cursor.execute(genres_list)
    return cursor.fetchall()

def range_genres_years(genres, cursor):
    cursor.execute(range_genres_years_query, (genres,))
    return cursor.fetchall()

def combined_search(cursor, genre, start_year=1990, end_year=2025):
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
