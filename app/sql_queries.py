# MySQL Queries
keyword_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE UPPER(title) LIKE %s"""

count_keyword_query = """SELECT count(*) FROM sakila.film
WHERE UPPER(title) LIKE %s"""

genres_years_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE c.name = %s AND f.release_year BETWEEN %s AND %s"""

count_genres_years_query = """
SELECT count(*) FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE c.name = %s AND f.release_year BETWEEN %s AND %s"""

genres_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE c.name = %s"""

count_genres_query = """
SELECT count(*) FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE c.name = %s"""

years_query = """
SELECT f.film_id, f.title, c.name, f.release_year, f.description FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE f.release_year BETWEEN %s AND %s"""

count_years_query = """
SELECT count(*) FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE f.release_year BETWEEN %s AND %s"""

genres_list = """
SELECT category_id, name FROM sakila.category"""

range_genres_years_query = """
SELECT MIN(f.release_year) as min_year, MAX(f.release_year) as max_year FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id
WHERE c.name = %s"""

range_years_query = """
SELECT MIN(f.release_year) as min_year, MAX(f.release_year) as max_year FROM sakila.film as f
JOIN sakila.film_category as fc
ON f.film_id = fc.film_id
JOIN sakila.category as c
ON fc.category_id = c.category_id"""