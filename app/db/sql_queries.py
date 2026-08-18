# MySQL Queries
#
# Note: tables are referenced without a hardcoded schema prefix on purpose —
# the connection already selects the target database via Config.MYSQL_DATABASE
# (see app/db/sql_connection.py), so queries work regardless of which
# database name is configured (e.g. not necessarily "sakila").

# Kept as a plain string (rather than build_keyword_query(1)) for backward
# compatibility and as a readable reference for the single-word case.
# Actual keyword searches always go through build_keyword_query() so that
# multi-word / partial-word input works — see keywords_search().
keyword_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id
WHERE LOWER(f.title) LIKE %s"""

multiword_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id
WHERE"""

genres_years_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id
WHERE c.name = %s AND f.release_year BETWEEN %s AND %s"""

genres_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id
WHERE c.name = %s"""

build_genres_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id
WHERE c.name IN ({placeholders})"""

build_genres_years_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id
WHERE c.name IN ({placeholders}) AND f.release_year BETWEEN %s AND %s"""

years_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id
WHERE f.release_year BETWEEN %s AND %s"""

genres_list = """
SELECT category_id, name FROM category"""

range_years_query = """
SELECT MIN(f.release_year) as min_year, MAX(f.release_year) as max_year FROM film as f
JOIN film_category as fc
ON f.film_id = fc.film_id
JOIN category as c
ON fc.category_id = c.category_id"""
