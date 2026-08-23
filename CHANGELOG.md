# Changelog

All notable changes to this project will be documented in this file.

---

## [4.2.1] - 2026-08-23

### Fixed
- Fixed 19 failing unit tests resulting from the DB module query-builder refactoring.
- Updated test patches and imports to reference `build_*` query functions from `app.db.sql_queries` instead of legacy `sql_connection` local helpers.

### Added
- Unit test coverage for `ValueError` validation when `count < 1` in SQL query builders (`build_keyword`, `build_genres`, `build_genres_years`).

## [4.2.0] - 2026-08-22

### Added
- Five new statistics reports, accessible from the Statistics menu
  (options 3-7):
  - **Zero-result queries** — searches that executed successfully but
    found nothing, surfaced most-frequent-first
  - **Search type breakdown** — count and % share per search type
  - **Average duration by search type** — mean `duration_ms`, slowest
    search type first
  - **Search activity by day** — searches per calendar day, most recent
    14 active days
  - **Success rate by search type** — % of searches that ran without an
    internal error, per search type
- Corresponding aggregation pipelines in `app/db/mongo_queries.py`:
  `zero_result_queries`, `search_type_breakdown`,
  `avg_duration_by_search_type`, `searches_per_day`,
  `success_rate_by_search_type`
- A shared "No data yet." message (`stats.no_data`, localized in all 4
  languages) shown by every report — including the existing top5/last5 —
  when there are no logs to report on yet, instead of an empty table
- Tests for all 5 new pipelines and report functions, plus updated
  statistics-menu routing tests (265 tests total)

- Three more statistics reports (menu options 8-10), building on the
  structured `genres` list and `start_year`/`end_year` fields introduced
  by multi-genre search:
  - **Popular year ranges (by decade)** — `years`/`genre_years` searches
    bucketed by decade of `start_year`
  - **Top individual genres** — genre popularity via `$unwind` on
    `params.genres`, independent of which other genres it was searched
    alongside
  - **Genre co-occurrence** — which genre pairs are most often searched
    together (e.g. "Action + Comedy")
- `app.db.mongo_queries.year_range_popularity` and
  `top_individual_genres` aggregation pipelines
- `app.db.mongo_queries.genre_combinations_raw`: a deliberately minimal
  `$match` + `$project` pipeline that fetches raw genre lists rather than
  computing pairwise co-occurrence inside MongoDB itself — generating all
  unique pairs within an array in an aggregation pipeline needs either a
  fragile self-`$unwind`-and-filter or MongoDB 5.2+'s `$sortArray`;
  counting the pairs in plain Python via `itertools.combinations` is
  simpler, more portable across MongoDB versions, and easier to test
- Tests for all 3 new pipelines and report functions, including the
  Python-side pair-counting logic (order-independence, de-duplication of
  repeated genres within one search, 3-genre searches expanding into 3
  pairs) — 295 tests total

## [4.1.0] - 2026-08-18

### Added
- Multi-genre search: selecting several genres at once (e.g. "1,3" or
  "action, comedy" in the genre menu) now matches films belonging to ANY
  of them (OR semantics — a film has exactly one genre in this schema),
  for both the plain genre search and the combined genre+years search
- `app.db.sql_queries.build_genres_query(genre_count)` and
  `build_genres_years_query(genre_count)`: build dynamically-sized,
  fully parameterized `IN (...)` queries for one or more genres
- A genre cap (`MAX_SELECTED_GENRES = 16` in `sql_connection.py`) as a
  defensive limit, mirroring the existing keyword-search word cap
- Updated the genre-selection prompt in all 4 locales with a short tip
  about comma-separated multi-genre selection
- Tests covering multi-genre selection, de-duplication, order
  preservation, the "one invalid entry rejects the whole input" rule, and
  the new query builders

### Changed
- `genres_search()` and `genre_years_search()` now take a `list[str]` of
  genre names instead of a single `str`
- Logged search params for `"genre"` and `"genre_years"` searches now use
  a `"genres"` list field instead of a single `"genre"` string field, and
  `build_query_key()` joins multiple genre names with `+`
  (e.g. `genre_Action+Comedy`)

## [4.0.0] - 2026-08-17

### Added
- Multi-word / partial-word keyword search: entering several words or
  word fragments (e.g. "gone wind") now matches titles containing all of
  them, in any order (e.g. "Gone with the Wind"), instead of only
  matching the exact typed phrase as one literal substring
- `app.db.sql_queries.build_keyword_query(word_count)`: builds a
  dynamically-sized, still fully parameterized query with one
  `LOWER(f.title) LIKE %s` condition per search term, AND-joined
- A word cap (`MAX_KEYWORD_WORDS = 10` in `sql_connection.py`) so a very
  long pasted string can't blow up the query into dozens of conditions
- Updated the keyword-search prompt in all 4 locales with a short tip
  about multi-word/partial-word search
- Tests covering word splitting, de-duplication, the word cap, and
  empty/whitespace-only input for the new search behavior

## [3.0.0] - 2026-08-15

### Added
- Pytest-based unit test suite: 176 tests, ~99% coverage of `app/`
- `../tests/conftest.py` with reusable fakes: `FakeCursor` (mocks a pymysql
  DictCursor) and `FakeMongoCollection` (mocks a pymongo Collection), plus
  a `frozen_now` fixture for deterministic date/time-dependent tests
- `../pytest.ini` and `requirements.txt` (pytest, pytest-cov)
- Regression tests locking in the earlier bug fixes: keyword search
  case-sensitivity, hardcoded `sakila.` schema, guaranteed connection
  cleanup via `try/finally` in `main_menu`
- A "Testing" section in README.md documenting how to run the suite

## [2.0.0] - 2026-08-14

### Added
- Multi-language UI: English, Deutsch, Русский, Українська
- Language selection prompt at application startup, before any other menu
- `app/i18n/` module: `translator.py` (t()/set_language()/banner() helpers),
  `language_select.py`, and per-language JSON dictionaries under `locales/`

### Changed
- All menu text, prompts, and error messages now come from the active
  locale instead of being hardcoded in English
- Section banners (`=== HEADER ===`) are now generated dynamically
  (centered around the translated header text) instead of using a fixed
  number of hardcoded `=` characters, so they stay visually consistent
  regardless of translation length

### Fixed
- Keyword search was case-broken: `UPPER(title) LIKE %s` was compared
  against an already-lowercased pattern and could never match. Fixed to
  `LOWER(f.title) LIKE %s`
- `.env.example` referenced `MONGO_URL` while the code expected
  `MONGO_URI`, and was missing `MONGO_COLLECTION` entirely
- `requirements.txt` was saved as UTF-16 and could break `pip install -r`;
  re-saved as UTF-8
- Year-range validation used a hardcoded `1990` lower bound instead of the
  actual minimum release year available in the database
- `genre_years_flow` used an inconsistent upper year bound compared to
  `years_flow`; both now share the same DB-derived range
- SQL queries no longer hardcode the `sakila.` schema prefix, so they work
  with whatever database name is configured via `MYSQL_DATABASE`
- Database connections are now guaranteed to close via `try/finally`, even
  if an unhandled exception occurs mid-session
- Replaced remaining raw `input()` calls with `safe_input()` for consistent
  Ctrl+C handling across the whole app
- Removed unused dead-code example documents from `mongo_queries.py`

---

## [1.0.1] - 2026-08-07

### Fixed
- Fixed keyword search casing mismatch (`UPPER` vs `lower`) preventing search results from being returned
- Synchronized `.env.example` with `config.py` (`MONGO_URI` key name and added missing `MONGO_COLLECTION`)
- Re-saved `requirements.txt` in standard UTF-8 encoding to fix `pip install` failures
- Replaced hardcoded minimum year validation (`1990`) with dynamic database-driven bounds
- Standardized maximum year limits calculation across all search flows

### Changed
- Replaced direct `input()` calls with `safe_input` in genre, year range, and pagination flows to handle `Ctrl+C` cleanly
- Ensured database connections and cursors are always closed using `try/finally` in main menu loop
- Removed hardcoded `sakila.` schema prefix from SQL queries to support custom database names via `.env`
- Optimized `get_genres` by moving genre list database retrieval outside the input loop
- Moved unused log structure variables in `mongo_queries.py` to docstrings
- Added proper type annotations under `TYPE_CHECKING` for `pymysql` and `pymongo`

---

## [1.0.0] - 2026-04-01

### Added
- First stable release with modular CLI interface

---

## [0.9.2] - 2026-03-31

### Added
- Ensure "last 5 searches" returns only unique queries

### Changed
- Improved MongoDB aggregation logic for search history

---

## [0.9.1] - 2026-03-30

### Fixed
- Handle empty input in search flow

---

## [0.9.0] - Initial functional milestone

### Added
- Functional architecture implementation
- Search features (keyword, genre, year, combined)
- MongoDB logging and statistics

### Changed
- Refactored menu logic
- Improved pagination and result display