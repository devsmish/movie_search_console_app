from unittest.mock import MagicMock, patch

from scripts import apply_indexes
from tests.conftest import FakeCursor, FakeMongoCollection


class TestApplyMysqlIndexes:
    def test_creates_all_indexes_when_none_exist(self):
        cursor = FakeCursor(fetchone_results=[{"cnt": 0}, {"cnt": 0}, {"cnt": 0}])
        connection = MagicMock()
        connection.cursor.return_value = cursor

        with patch.object(apply_indexes, "get_connection", return_value=connection):
            apply_indexes.apply_mysql_indexes()

        create_calls = [q for q, _ in cursor.execute_calls if q.startswith("CREATE INDEX")]
        assert len(create_calls) == 3
        assert any("idx_category_name" in q for q in create_calls)
        assert any("idx_film_release_year" in q for q in create_calls)
        assert any("idx_film_title_lower" in q for q in create_calls)

    def test_skips_indexes_that_already_exist(self):
        # All three information_schema checks report "already exists".
        cursor = FakeCursor(fetchone_results=[{"cnt": 1}, {"cnt": 1}, {"cnt": 1}])
        connection = MagicMock()
        connection.cursor.return_value = cursor

        with patch.object(apply_indexes, "get_connection", return_value=connection):
            apply_indexes.apply_mysql_indexes()

        create_calls = [q for q, _ in cursor.execute_calls if q.startswith("CREATE INDEX")]
        assert create_calls == []

    def test_creates_only_the_missing_indexes(self):
        # idx_category_name exists, the other two don't.
        cursor = FakeCursor(fetchone_results=[{"cnt": 1}, {"cnt": 0}, {"cnt": 0}])
        connection = MagicMock()
        connection.cursor.return_value = cursor

        with patch.object(apply_indexes, "get_connection", return_value=connection):
            apply_indexes.apply_mysql_indexes()

        create_calls = [q for q, _ in cursor.execute_calls if q.startswith("CREATE INDEX")]
        assert len(create_calls) == 2
        assert not any("idx_category_name" in q for q in create_calls)

    def test_closes_connection_and_cursor_even_if_a_create_fails(self):
        cursor = FakeCursor(fetchone_results=[{"cnt": 0}, {"cnt": 0}, {"cnt": 0}])
        cursor.execute_real = cursor.execute

        def flaky_execute(query, params=None):
            cursor.execute_real(query, params)
            if query.startswith("CREATE INDEX idx_category_name"):
                raise Exception("boom")

        cursor.execute = flaky_execute
        connection = MagicMock()
        connection.cursor.return_value = cursor

        with patch.object(apply_indexes, "get_connection", return_value=connection):
            apply_indexes.apply_mysql_indexes()  # must not raise

        connection.close.assert_called_once()


class TestApplyMongoIndex:
    def test_creates_search_type_timestamp_index(self):
        collection = FakeMongoCollection()

        with patch.object(apply_indexes, "get_mongo_collection", return_value=collection):
            apply_indexes.apply_mongo_index()

        assert collection.created_indexes == [[("search_type", 1), ("timestamp", -1)]]

    def test_is_idempotent_when_run_twice(self):
        # create_index() itself is idempotent against a real MongoDB
        # server; this just documents that calling it twice from our side
        # doesn't error or need any extra guard.
        collection = FakeMongoCollection()

        with patch.object(apply_indexes, "get_mongo_collection", return_value=collection):
            apply_indexes.apply_mongo_index()
            apply_indexes.apply_mongo_index()

        assert len(collection.created_indexes) == 2
        assert collection.created_indexes[0] == collection.created_indexes[1]


class TestMain:
    def test_main_applies_both_mysql_and_mongo_indexes(self):
        with patch.object(apply_indexes, "apply_mysql_indexes") as mysql_step, \
             patch.object(apply_indexes, "apply_mongo_index") as mongo_step:
            apply_indexes.main()

        mysql_step.assert_called_once()
        mongo_step.assert_called_once()
