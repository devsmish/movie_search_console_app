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
    cursor.execute(keyword_search, (f"%{keyword}%",))
    return cursor.fetchall()

def list_genres(cursor):
    cursor.execute(genres_list)
    return cursor.fetchall()

def range_years(genres, cursor):
    cursor.execute(range_of_years, (genres,))
    return cursor.fetchall()

def combined_search(cursor, genre, start_year=1990, end_year=2025):
    cursor.execute(genres_years_search, (genre, start_year, end_year,))
    return cursor.fetchall()