# Changelog

All notable changes to this project will be documented in this file.

---

## [4.3.4] - 2026-08-23

Fifth and final release in the staged 4.3.x series that started in
[4.3.0](#430---2026-08-22). This one closes it out with test coverage
for the entry point and a CI workflow.

### Added
- `tests/test_main.py`: new coverage for `app/main.py` —
  - `_force_utf8_console()`'s fallback paths: a stream that lacks
    `reconfigure()` entirely (`AttributeError`), a stream whose
    `reconfigure()` raises `ValueError`, and confirmation that stdout
    failing doesn't prevent stderr from still being reconfigured.
  - That `reconfigure()` is actually called with
    `encoding="utf-8", errors="replace"` on both streams (the previous
    test only checked the no-op case).
  - That `_force_utf8_console()` runs first, before `choose_language()`
    — and that it still runs even when the language choice is
    cancelled.
  - 6 new tests; `tests/test_main.py` now has 9 (previously 3).
- `../.github/workflows/tests.yml`: runs `pytest --cov=app
  --cov-report=term-missing` on every push and pull request targeting
  `main`, across a Python 3.11 / 3.12 / 3.13 matrix. No live MySQL/Mongo
  needed — the whole suite runs against the fakes in
  `tests/conftest.py`, same as running it locally.
- A `Tests` status badge and an updated `Testing` section in the README
  (test count, coverage note, and a mention of the new CI workflow).

### Notes
- Total suite size after this release: 384 tests, ~99% coverage of the
  `app/` package (per `pytest --cov=app`).
- The `if __name__ == "__main__": main()` guard at the bottom of
  `app/main.py` was deliberately left untested — it's a one-line
  standard idiom, and the only ways to exercise it directly
  (`runpy`/subprocess) either re-import the module fresh (defeating
  `unittest.mock.patch` on the already-imported module) or spawn a real
  interactive process, neither of which is worth the added fragility
  for a single line of boilerplate.

## [4.3.3] - 2026-08-23

Fourth release in the staged 4.3.x series (see [4.3.0](#430---2026-08-22)
for the full plan). This one adds a rotating file log alongside the
existing console error messages.

### Added
- `app/utils/app_logger.py`: `get_logger(name, log_dir=None,
  max_bytes=None, backup_count=None)` returns a logger backed by a
  `RotatingFileHandler` writing to `logs/app.log` (~1 MB per file, 3
  rotated backups by default). Idempotent per logger name (repeated
  calls never attach duplicate handlers), set to WARNING level, and
  does not propagate to the root logger (so nothing leaks onto the
  console via this path — the existing `print()` calls remain the
  console-facing message, unchanged).
  `reset_logger(name)` is provided for tests that need to reconfigure
  an already-set-up logger (e.g. pointed at a different directory).
- `app/services/log_service.py`: a MongoDB insert failure is now also
  logged (with a full traceback) via the new file logger, in addition
  to the existing console message.
- `app/services/search_service.py`: all three failure points (search
  execution, result display, request logging) are now also logged via
  the file logger, in addition to their existing console messages.
- 17 new tests: `../tests/test_app_logger.py` (the logger utility in
  isolation, including rotation) plus new `TestLogRequestFileLogging`
  / `TestExecuteSearchFileLogging` classes in the existing service test
  files — 378 tests total.
- `logs/` added to `.gitignore` (mirroring the existing `exports/`
  entry from 4.3.2).

### Notes
- Console-facing behavior is unchanged: every message a user sees while
  running the app looks exactly the same as before. The file log is
  additive — a persistent, greppable record with full tracebacks for
  debugging after the session has ended, which the console alone never
  provided.
- `app/services/stats_service.py` reports still print directly (no
  operational failure states to log there beyond what MongoDB's own
  driver would raise) and were left as-is, consistent with the 4.3.2
  decision to leave that module's formatting untouched.

## [4.3.2] - 2026-08-23

Third release in the staged 4.3.x series (see [4.3.0](#430---2026-08-22)
for the full plan). This one is the big one: a shared output-formatting
module plus a results-export feature.

### Added
- `../app/utils/formatting.py`: a new shared module for turning
  `list[dict]` data into a console table, CSV text, or JSON text.
  - `Column`: a small dataclass describing one column (`key`, `header`,
    `max_width`, `align`), shared across all three output formats.
  - `format_table()`: renders a fixed-width plain-text table. Every
    value is truncated (with a trailing "…") to its column's
    `max_width`, so a table can no longer be pushed out of alignment by
    an unexpectedly long value — every line is guaranteed to be the
    same width.
  - `to_csv()` / `to_json()`: render the same rows without truncation
    (full values, since these formats are for other programs to
    consume, not a fixed-width terminal). `to_json()` can optionally
    re-key output to each column's `header` for human-readable field
    names, and falls back to `str()` for values that aren't natively
    JSON-serializable (e.g. `datetime`).
  - `default_export_filename()` / `write_export_file()`: timestamped
    filenames and a small helper that creates missing parent
    directories before writing.
- **Results export**: `app/utils/pagination.py` gained a new **[e]**
  navigation option. It exports the *entire* result set currently being
  browsed (not just the page on screen) to CSV or JSON under a new
  `exports/` directory (gitignored), with a timestamped filename.
  Export columns include `description`, which every search query already
  fetches but the console table has no room to display.
- New locale keys (`col_description`, `nav_export`,
  `export_prompt_format`, `export_invalid_format`, `export_success`,
  `export_error`) added to all 4 locales.
- 39 new tests: `../tests/test_formatting.py` (the formatting module in
  isolation) and new `TestLongValuesDoNotBreakAlignment` /
  `TestExportResults` classes in `tests/test_pagination.py` — 361 tests
  total.

### Fixed
- `print_results_paginated()`'s console table no longer misaligns when a
  film title (or any other cell) is longer than its column: the value is
  now truncated with an ellipsis via `format_table()` instead of being
  printed in full and overflowing into the next column.

### Changed
- `app/utils/pagination.py` now delegates table rendering to
  `app.utils.formatting.format_table()` instead of hand-rolled f-string
  formatting. Behavior for normal-length values is unchanged; only the
  overflow case (see "Fixed" above) is different.

### Notes
- `app/services/stats_service.py`'s ~10 report tables still use their
  own hand-rolled formatting and were deliberately left untouched in
  this release — migrating them to `../app/utils/formatting.py` is a
  larger, separate effort with limited shared benefit (each report has
  a different, fairly fixed column layout) and is not currently planned
  as part of the 4.3.x series.

## [4.3.1] - 2026-08-25

Second release in the staged 4.3.x series (see [4.3.0](#430---2026-08-22)
for the full plan). This one adds in-memory caching for reference data.

### Added
- `list_genres()` and `range_years()` in `app/db/sql_connection.py` are
  now cached per-cursor via `functools.lru_cache`: within one CLI session
  (one long-lived cursor), each is queried from MySQL at most once,
  since both are reference data (the genre list, the min/max release
  year) that's read on every visit to the genre/year search flows but
  essentially never changes mid-session.
- Both functions gained an optional `force_refresh: bool = False`
  parameter to bypass the cache for a single call when needed.
- `clear_reference_data_cache()`: clears both caches at once — useful
  for tests, and for long-lived processes where the underlying data is
  known to have changed.
- Each call still returns a fresh `list` copy (never the cached object
  itself), so a caller mutating the returned list in place (e.g.
  sorting it) can't corrupt what later callers see.
- Tests for cache hits/misses, `force_refresh`, per-cursor isolation,
  copy-safety, and `clear_reference_data_cache()` — 322 tests total.
- `tests/conftest.py`: a new autouse fixture clears the reference-data
  cache before and after every test, alongside the existing
  language-reset fixture.

## [4.3.0] - 2026-08-22

This release is the first of a staged 4.3.x series focused on
performance and reliability groundwork, planned as 4.3.0 (this release,
DB indexes + config validation) → 4.3.1 (reference-data caching) →
4.3.2 (output formatting + export) → 4.3.3 (file-based logging) → 4.3.4
(test/CI hardening). See the README roadmap for the full plan.

### Added
- `../scripts/apply_indexes.py`: an idempotent script that adds the indexes
  backing every search filter used by the app —
  `category(name)`, `film(release_year)`, and a functional index on
  `film((LOWER(title)))` for MySQL, plus a MongoDB
  `(search_type: 1, timestamp: -1)` index for the log collection used by
  `app/services/stats_service.py`. Existing indexes are detected and
  skipped rather than erroring, so it's safe to re-run.
- `../migrations/4.3.0_add_indexes.sql`: a plain-SQL reference of exactly
  what the script above creates, for manual review/application.
- `Config.validate()` / `Config.missing_vars()` in `config.py`: checks
  that all required `.env` variables are present at startup and raises a
  `ConfigError` (listing the missing names) instead of letting a
  misconfigured `.env` surface as a confusing low-level pymysql/pymongo
  connection error several layers down.
- `main_menu()` now calls `Config.validate()` before attempting any
  database connection, and reports missing configuration via a new
  localized `config.missing_vars` message (added to all 4 locales).
- Tests for the new config validation (`../tests/test_config.py`), the
  index-application script (`../tests/test_apply_indexes.py`), and the new
  main-menu startup path (`TestMainMenuConfigValidation` in
  `tests/test_main_menu.py`) — 312 tests total.
- `FakeCursor.fetchone()` / `FakeCursor.commit()` and
  `FakeMongoCollection.create_index()` added to `tests/conftest.py` to
  support the above without needing a live database.

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