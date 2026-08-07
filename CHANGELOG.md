# Changelog

All notable changes to this project will be documented in this file.

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