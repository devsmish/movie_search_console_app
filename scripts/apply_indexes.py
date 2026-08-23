"""
Applies the performance indexes introduced in 4.3.0.

Idempotent: safe to run multiple times, and safe to run against a
database that already has some or all of these indexes — each one is
checked before creation and skipped (not re-created / not errored) if it
already exists.

MySQL indexes (see migrations/4.3.0_add_indexes.sql for the plain-SQL
reference of what this creates):
    idx_category_name      on category(name)
    idx_film_release_year  on film(release_year)
    idx_film_title_lower   on film((LOWER(title)))   -- MySQL 8.0.13+

MongoDB index:
    (search_type: 1, timestamp: -1) on the logs collection, backing the
    per-search-type statistics reports in app/services/stats_service.py.

Usage:
    python -m scripts.apply_indexes
"""
from app.db.sql_connection import get_connection
from app.db.mongo_connection import get_mongo_collection

MYSQL_INDEXES = [
    ("idx_category_name", "category", "(name)"),
    ("idx_film_release_year", "film", "(release_year)"),
    ("idx_film_title_lower", "film", "((LOWER(title)))"),
]


def _mysql_index_exists(cursor, table: str, index_name: str) -> bool:
    """
    Checks information_schema for an existing index, rather than relying
    on CREATE INDEX's error to detect it — MySQL doesn't support
    `CREATE INDEX IF NOT EXISTS`, so an upfront check is what makes this
    script safe to re-run.
    """
    cursor.execute(
        """
        SELECT COUNT(*) AS cnt FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
        """,
        (table, index_name),
    )
    row = cursor.fetchone()
    count = row["cnt"] if isinstance(row, dict) else row[0]
    return count > 0


def apply_mysql_indexes() -> None:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        for index_name, table, columns in MYSQL_INDEXES:
            if _mysql_index_exists(cursor, table, index_name):
                print(f"[mysql] {index_name} already exists on {table}, skipping")
                continue
            print(f"[mysql] creating {index_name} on {table}{columns} ...")
            try:
                cursor.execute(f"CREATE INDEX {index_name} ON {table} {columns}")
                connection.commit()
                print(f"[mysql] {index_name} created")
            except Exception as e:
                print(f"[mysql] failed to create {index_name}: {e}")
    finally:
        cursor.close()
        connection.close()


def apply_mongo_index() -> None:
    collection = get_mongo_collection()
    # create_index() is itself idempotent: calling it again with the same
    # key spec is a cheap no-op rather than an error or a duplicate index.
    name = collection.create_index([("search_type", 1), ("timestamp", -1)])
    print(f"[mongo] ensured index '{name}' on (search_type, timestamp)")


def main() -> None:
    apply_mysql_indexes()
    apply_mongo_index()


if __name__ == "__main__":
    main()
