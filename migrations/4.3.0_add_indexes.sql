-- Migration: 4.3.0 - add indexes backing the app's search filters
--
-- Every search flow in app/db/sql_queries.py filters on one of:
--   c.name             (genres_query, build_genres_query, ...)
--   f.release_year      (years_query, genres_years_query, ...)
--   LOWER(f.title)       (keyword_query, build_keyword_query)
-- Without indexes these run as full table scans against `category`
-- and `film`. This migration adds the missing indexes.
--
-- Safe to run more than once: CREATE INDEX fails loudly with a
-- "Duplicate key name" error if the index already exists rather than
-- silently doing nothing, so prefer `scripts/apply_indexes.py`
-- (idempotent, checks information_schema first) over running this file
-- directly against a database that may already have these indexes.
-- This .sql file is kept as a plain, reviewable reference of exactly
-- what gets created.

CREATE INDEX idx_category_name        ON category (name);
CREATE INDEX idx_film_release_year    ON film (release_year);

-- LOWER(f.title) LIKE %s can't use a plain index on `title` (the LOWER()
-- wrapper prevents that), so a functional index is added for MySQL 8.0.13+.
-- On older MySQL, this line will fail; either upgrade or drop it — the
-- keyword search still works without it, just without this speedup.
CREATE INDEX idx_film_title_lower     ON film ((LOWER(title)));
