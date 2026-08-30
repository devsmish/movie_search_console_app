# movie_search_console_app
** educational project **

[![Tests](https://github.com/devsmish/movie_search_console_app/actions/workflows/tests.yml/badge.svg)](https://github.com/devsmish/movie_search_console_app/actions/workflows/tests.yml)

# 🎬 Movie Search Console App

A console-based application for searching movies with support for flexible filtering, search history tracking,
and analytical reports.

This project is built using a **functional programming approach** and demonstrates working with relational and 
non-relational databases, modular architecture, and CLI interaction design.

---

## 🚀 Features

### 🔍 Search Functionality

* Search movies by **keyword** — supports multiple words or partial words (e.g. "gone wind" matches "Gone with the Wind"), matched in any order
* Filter by **one or more genres** — select several at once (e.g. "1,3" or "action, comedy"); a film matches if it belongs to any of them
* Filter by **years**
* Search by **year or range of years**
* Combined search (**genre + year range**)

### 📊 Statistics & Analytics

* Top 5 most popular search queries
* Last 5 recent search queries
* **Zero-result queries** — searches that found nothing, the most direct
  signal of a catalog gap or a mistyped/misspelled term
* **Search type breakdown** — how often keyword/genre/years/genre+years
  searches are used, with each type's share of the total
* **Average duration by search type** — which kind of search is heaviest
  on the database
* **Search activity by day** — searches per calendar day (last 14 days
  with activity)
* **Success rate by search type** — % of searches that executed without
  an internal error (independent of whether they found any results)
* **Popular year ranges by decade** — which decades get searched most
* **Top individual genres** — genre popularity independent of which other
  genres it was combined with in a given search
* **Genre co-occurrence** — which pairs of genres are most often searched
  together (e.g. Action + Comedy)
* Query performance tracking (execution time, result count)

### 🗄 Data Management

* **MySQL** — the main source of data on films
* **MongoDB** — storing query history and analytics

### 🧠 Additional Functionality

* Pagination for search results
* Input validation and error handling
* Query logging with metadata:

  * timestamp
  * parameters
  * execution time
  * success status

### 🌍 Multi-language UI

* Supported languages: **English, Deutsch, Русский, Українська**
* Language is selected once, right at startup, before any menu is shown
* All menu text, prompts, and error messages are localized; movie titles,
  genres, and descriptions come from the Sakila dataset and are **not**
  translated (they stay in the source data's original language)

### 📤 Export search results

* From any paginated search-results screen, press **[e]** to export the
  full result set (all pages, not just the one on screen) to **CSV** or
  **JSON**
* Files are written to `exports/` with a timestamped name, e.g.
  `exports/search_results_20260826_153000.csv`
* Console tables, CSV, and JSON export all share the same column
  definitions via `../app/utils/formatting.py`, so they stay consistent —
  and a long title can no longer misalign the console table, since
  values are now truncated to fit instead of overflowing

### 🪵 Operational error logging

* Search failures, result-display failures, and MongoDB log-write
  failures are still reported on the console as before — and are now
  **also** written, with a full traceback, to a rotating file log at
  `logs/app.log` (via `app/utils/app_logger.py`)
* The log file rotates at ~1 MB, keeping 3 backups (`app.log.1`–`.3`),
  so it never grows unbounded
* Console output stays the same for a person watching the terminal;
  the file is for after-the-fact debugging once the session has ended

---

## 🏗 Project Structure

The project has been refactored into a modular and scalable architecture, separating responsibilities across distinct layers. This improves readability, maintainability, and prepares the codebase for future extensions (such as OOP or API integration).

```bash
app/
│
├── main.py                   # Application entry point
│
├── i18n/                      # Internationalization (multi-language UI)
│   ├── translator.py         # t() / set_language() / banner() helpers
│   ├── language_select.py    # Startup language picker (shown before translator is set)
│   └── locales/              # One JSON dictionary per supported language
│       ├── en.json
│       ├── de.json
│       ├── ru.json
│       └── uk.json
│
├── db/                       # Data access layer (database interaction)
│   ├── sql_connection.py     # MySQL connection setup
│   ├── sql_queries.py        # SQL queries for movie search
│   ├── mongo_connection.py   # MongoDB connection setup
│   └── mongo_queries.py      # Aggregation pipelines for analytics
│
├── menu/                     # CLI interface (user interaction layer)
│   ├── main_menu.py          # Main application menu
│   ├── search_menu.py        # Search options menu
│   └── stats_menu.py         # Statistics menu
│
├── flows/                    # Application flows (user scenarios)
│   ├── keyword_flow.py       # Keyword search logic
│   ├── genre_flow.py         # Genre-based search
│   ├── years_flow.py         # Year/range search
│   └── genre_years_flow.py   # Combined search (genre + years)
│
├── services/                 # Business logic layer
│   ├── search_service.py     # Search execution & orchestration
│   ├── log_service.py        # Logging search requests (MongoDB)
│   └── stats_service.py      # Statistics and reporting logic
│
├── utils/                    # Utility functions (helpers)
│   ├── app_logger.py         # Rotating file logger for operational errors (logs/app.log)
│   ├── console_colors.py     # Shared red() helper for console error messages
│   ├── formatting.py         # Shared table/CSV/JSON rendering, used by pagination.py
│   ├── input_utils.py        # Safe input handling & validation
│   ├── pagination.py         # Paginated console output + results export (CSV/JSON)
│   └── year_utils.py         # Year normalization & parsing

tests/                         # Pytest unit test suite (see "Testing" below)
├── conftest.py               # Shared fixtures: fake cursor, fake Mongo collection
├── test_*.py                 # One test module per app module, mirroring app/

scripts/                       # One-off maintenance scripts (not part of the interactive CLI)
├── apply_indexes.py           # Idempotently applies the 4.3.0 MySQL + MongoDB indexes

migrations/                    # Plain-SQL reference for schema/index changes
├── 4.3.0_add_indexes.sql

.github/workflows/              # CI: runs the pytest suite on push/PR
├── tests.yml

config.py                      # Env-based configuration + Config.validate() startup check
```

---

### 🧠 Architectural Overview

The application follows a **layered structure**, where each module has a clear responsibility:

* **menu/** → handles user interaction (CLI interface)
* **flows/** → defines user scenarios and orchestrates actions
* **services/** → contains core business logic
* **db/** → responsible for all database operations
* **utils/** → reusable helper functions
* **i18n/** → 4-language translates

---

### ✅ Benefits of This Structure

* 📌 Clear separation of concerns
* 🔧 Easier debugging and testing
* 📦 Scalable and extensible architecture
* 🌐 Multi-language UI already implemented (v2.0.0)

---

💡 This structure reflects a transition from a monolithic script to a **production-like modular design**, making the project easier to maintain and evolve.


---

## ⚙️ Technologies Used

* **Python 3.14**
* **MySQL** (relational database)
* **MongoDB** (NoSQL database)
* **PyMySQL** (MySQL connector)
* **pymongo** (MongoDB driver)
* **pytest** (Unit-tests)

---

## ▶️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/devsmish/movie_search_console_app.git
cd movie_search_console_app
```

---

### 2. Create and configure `.env` or `config.py`

Example configuration:

```python
class Config:
    MYSQL_HOST = "localhost"
    MYSQL_USER = "your_user"
    MYSQL_PASSWORD = "your_password"
    MYSQL_DATABASE = "sakila"

    MONGO_URI = "mongodb://localhost:27017/"
    MONGO_DATABASE = "movie_search"
    MONGO_COLLECTION = "logs"
```

---

### 3. Install dependencies

```bash
pip install pymysql pymongo
```

---

### 4. Run the application

```bash
python app/main.py
```
If a required variable is missing from `.env`, the app now stops with a
clear message listing exactly which ones (instead of a low-level
pymysql/pymongo connection error). If a search, display, or logging
error occurs during a session, a full traceback is written to
`logs/app.log` in addition to the console message.

---

### 5. (Recommended) Apply performance indexes

Search filters on `category.name`, `film.release_year`, and
`LOWER(f.title)` benefit from indexes that aren't there by default in a
stock Sakila install. Run once, idempotently:

```bash
python -m scripts.apply_indexes
```

See `../migrations/4.3.0_add_indexes.sql` for the plain-SQL reference of
what this creates.

---

## ✅ Testing

The project has a pytest-based unit test suite (384 tests, ~99% coverage of
the `app/` package) that runs entirely against fakes/mocks — no live MySQL
or MongoDB instance is required.

The full suite runs automatically on every push/PR via GitHub Actions
(see the badge at the top of this file, and
`../.github/workflows/tests.yml`), across Python 3.11–3.14.

### Run the test suite

```bash
pytest
```

### Run with a coverage report

```bash
pytest --cov=app --cov-report=term-missing
```

### What's covered

* Pure utility functions (`year_utils`, `input_utils`)
* The i18n layer (`translator.py`, `language_select.py`), including a
  check that all 4 locale JSON files define exactly the same set of keys
* SQL query strings and the query-execution wrapper functions
  (`../app/db/sql_connection.py`), via a fake cursor, including the
  `list_genres()`/`range_years()` reference-data cache
* MongoDB connection/query helpers, via a fake collection
* All search flows (`keyword`, `genre`, `years`, `genre_years`) — happy
  path, cancellation, `Ctrl+C`, and invalid-input retry loops
* `execute_search`, `log_request`, and the statistics reports, including
  that failures are written to the rotating file log (`app_logger.py`)
  in addition to the console message
* Pagination navigation and edge cases (first/last page, invalid
  commands), the shared `formatting.py` table/CSV/JSON renderers, and
  the results-export feature
* Menu routing (`main_menu`, `search_menu`, `stats_menu`), including a
  regression test that DB connections close via `try/finally` even if a
  submenu raises an unhandled exception, and that missing `.env`
  configuration is reported before any connection is attempted
* The application entry point (`app/main.py`): UTF-8 console setup
  (including its fallback paths) and the language-selection → menu
  wiring
* SQL query strings, query-builder functions (`build_keyword`, `build_genres`, 
  `build_genres_years`), and dynamic validation rules (`count >= 1`)

Tests live under `tests/`, with shared fixtures (fake cursor, fake Mongo
collection, frozen-time helper) in `../tests/conftest.py`.

---

## 🧪 Example Usage

```text
MAIN MENU
1. Search movies
2. View statistics
Q. Exit
```

---

## 📈 Example Logged Data (MongoDB)

A keyword search:

```json
{
  "timestamp": "2026-03-30T12:00:00",
  "search_type": "keyword",
  "params": { "keyword": "gone wind" },
  "results_count": 1,
  "duration_ms": 15.3,
  "success": true,
  "query_key": "keyword_gone wind"
}
```

A combined genre(s) + year-range search, selecting multiple genres at once:

```json
{
  "timestamp": "2026-03-30T12:05:00",
  "search_type": "genre_years",
  "params": {
      "genres": ["Action", "Comedy"],
      "start_year": 1990,
      "end_year": 2025
  },
  "results_count": 87,
  "duration_ms": 9.7,
  "success": true,
  "query_key": "genre_years_Action+Comedy_1990_2025"
}
```

---

## 🧩 Architecture Notes

This version is implemented using a **functional approach**:

* Business logic is split into reusable functions
* Search flows are isolated and modular
* Logging and execution are abstracted via helper functions

This design provides:

* simplicity
* predictability
* ease of debugging

---

## 🔮 Roadmap



### 🏁 v1.0.0

* Stable functional architecture

### 🐛 v1.0.1

* Bug fixes, connection reliability, encoding fixes, and workflow consistency

### 🌍 v2.0.0

* Internationalization (multi-language support)

### 📊 v3.0.0

* Unit-testing

### 📊 v4.0.0

* Multi-word search

### 📊 v4.1.0

* Multi-genre search

### 📊 v4.2.0

* Advanced analytics and reporting

### 🔧 v4.3.0

* MySQL indexes for `category.name`, `film.release_year`, and
  `LOWER(film.title)`, plus a MongoDB `(search_type, timestamp)` index,
  applied idempotently via `python -m scripts.apply_indexes`
* Startup configuration validation: missing/misnamed `.env` variables are
  now reported clearly before any DB connection is attempted

### 🔧 v4.3.1

* In-memory caching of rarely-changing reference data (`list_genres()`,
  `range_years()`) with an opt-out `force_refresh` flag and an explicit
  `clear_reference_data_cache()` for when the underlying data is known
  to have changed mid-session

### 🔧 v4.3.2

* New `../app/utils/formatting.py` module: shared `Column` definitions and
  `format_table()` / `to_csv()` / `to_json()` renderers, so the console
  table, CSV export, and JSON export all stay consistent
* Fixed a long-standing bug where a film title longer than the
  hand-rolled column width would misalign the console results table —
  values are now truncated (with an ellipsis) to fit their column
  instead of overflowing
* New results-export feature: press **[e]** on any paginated
  search-results screen to export the full result set to CSV or JSON
  under `exports/`

### 🔧 v4.3.3

* New `app/utils/app_logger.py`: a rotating file logger (`logs/app.log`,
  ~1 MB per file, 3 backups) for the app's own operational errors
* Search failures, result-display failures, and MongoDB log-write
  failures in `app/services/search_service.py` and
  `app/services/log_service.py` are now also written to that file (with
  a full traceback) alongside the existing console message

### 🔧 v4.3.4

* Added test coverage for `app/main.py`: UTF-8 console setup (including
  its `AttributeError`/`ValueError` fallback paths, and that one stream
  failing doesn't block the other) and the language-selection → menu
  wiring (including the cancel path)
* New `../.github/workflows/tests.yml`: runs the full pytest suite on every
  push/PR to `main`, across Python 3.11, 3.12, and 3.13
* README `Tests` badge and an updated `Testing` section reflecting the
  current suite (384 tests, ~99% coverage)

This closes out the 4.3.x series that started in 4.3.0 — see the
entries above for the full set of changes (DB indexes, config
validation, reference-data caching, shared output formatting + export,
rotating file logging, and now test/CI hardening).

### 🔧 v4.4.0

* New `app/utils/console_colors.py`: a shared `red()` helper, replacing
  ~26 duplicated `f"\033[31m{text}\033[0m"` occurrences across
  `app/flows`, `app/menu`, and `app/utils`
* New `SEPARATOR_WIDTH` constant in `app/services/stats_service.py`,
  replacing 10 occurrences of a hardcoded `"-" * 88`
* Removed a stray ANSI color code baked into an internal
  `ValueError` message in `app/utils/year_utils.py` that was never
  actually shown to the user (the exception is always caught and
  replaced with a translated message by the caller)
* No behavior change — console output is byte-identical to before

### 🔐 v5.0.0

* Basic user authentication

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

## 📄 License / Data Source

This project is open-source and available under the MIT License.

This project uses the Sakila sample database, a standard MySQL example dataset for learning and testing.
The database is licensed under the BSD 3-Clause License, which allows free use, modification, and distribution.
Source: https://dev.mysql.com/doc/sakila/en/sakila-license.html
