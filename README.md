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

---

## 🏗 Project Structure

```bash
app/
│
├── main.py                # Entry point of the application
│
├── func_menu.py          # CLI menus, user interaction, flows
│
├── sql_connection.py     # MySQL connection and queries
├── mongo_connection.py   # MongoDB connection and analytics
│
├── mongo_queries.py      # Aggregation pipelines for statistics
│
├── config.py             # Configuration (DB credentials, settings)
```

> ⚠️ Note: In upcoming releases, the project structure will be refactored into a layered architecture (menu / flows / 
> services / utils).

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
python main.py
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

### 🔧 v0.10.0

* Project restructuring (modular architecture)
* Improved documentation (docstrings)

### 🌍 v0.11.0

* Internationalization (multi-language support)

### 🔐 v0.12.0

* Basic user authentication

### 📊 v0.14.0

* Advanced analytics and reporting

### 🏁 v1.0.0

* Stable functional architecture

### 🔄 v2.0.0

* Transition to Object-Oriented Programming (OOP)

### 🎨 v3.0.0

* UI layer (graphical interface)

### 🎨 v4.0.0

* UI layer (web interface)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

## 📄 License / Data Source

This project is open-source and available under the MIT License.

This project uses the Sakila sample database, a standard MySQL example dataset for learning and testing.
The database is licensed under the BSD 3-Clause License, which allows free use, modification, and distribution.
Source: https://dev.mysql.com/doc/sakila/en/sakila-license.html
