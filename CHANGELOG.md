# Changelog

All notable changes to this project will be documented in this file.

---

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