# movie_search_console_app
** educational project **

# 🎬 Movie Search Console App

A console-based application for searching movies with support for flexible filtering, search history tracking,
and analytical reports.

This project is built using a **functional programming approach** and demonstrates working with relational and 
non-relational databases, modular architecture, and CLI interaction design.

---

## 🚀 Features

### 🔍 Search Functionality

* Search movies by **keyword**
* Filter by **genre**
* Filter by **years**
* Search by **year or range of years**
* Combined search (**genre + year range**)

### 📊 Statistics & Analytics

* Top 5 most popular search queries
* Last 5 recent search queries
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
│   ├── input_utils.py        # Safe input handling & validation
│   ├── pagination.py         # Paginated output for results
│   └── year_utils.py         # Year normalization & parsing
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

```json
{
  "timestamp": "2026-03-30T12:00:00",
  "search_type": "keyword",
  "params": {
      "keyword": "action",
      "genre": "action",
      "start_year": 1990,
      "end_year":  2025},
  "results_count": 42,
  "duration_ms": 15.3,
  "success": true,
  "query_key": "keyword_action"
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

### 📊 v2.1.0

* Unit-testing

### 📊 v2.2.0

* Advanced analytics and reporting

### 🔧 v2.3.0

* Project restructuring (modular architecture)
* Improved documentation (docstrings)

### 🔐 v3.0.0

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
