"""
Shared pytest fixtures for the movie_search test suite.

Two fakes are provided instead of real MySQL/MongoDB connections:
- FakeCursor / fake_cursor: mimics a pymysql DictCursor's .execute()/.fetchall(),
  recording the last query and params so tests can assert on them.
- FakeMongoCollection / fake_mongo_collection: mimics a pymongo Collection's
  .insert_one()/.aggregate(), recording inserted documents in memory.

These keep the test suite fast and dependency-free (no live database needed)
while still exercising the real application code paths.
"""
import datetime

import pytest

from app.i18n.translator import set_language


@pytest.fixture(autouse=True)
def _reset_language():
    """
    Resets the active UI language to English before and after every test,
    so tests don't leak language state into one another regardless of
    execution order.
    """
    set_language("en")
    yield
    set_language("en")


@pytest.fixture(autouse=True)
def _reset_reference_data_cache():
    """
    Clears the list_genres()/range_years() cache before and after every
    test. Each test typically gets its own `fake_cursor` instance, so the
    lru_cache (keyed by cursor identity) wouldn't normally leak data
    between tests either way — but clearing explicitly keeps this
    independent of that fixture-instance detail and avoids the cache
    growing unbounded across the whole test run.
    """
    from app.db.sql_connection import clear_reference_data_cache

    clear_reference_data_cache()
    yield
    clear_reference_data_cache()


class FakeCursor:
    """
    A minimal stand-in for a pymysql DictCursor.

    Records the last executed query/params and returns pre-configured
    fetchall() results, so tests can verify both what SQL was run and
    how the calling code handles the returned rows.
    """

    def __init__(self, fetchall_result=None, fetchone_results=None):
        self.fetchall_result = fetchall_result if fetchall_result is not None else []
        # A queue of results returned one-per-call by fetchone(), for tests
        # that issue several execute()+fetchone() pairs in sequence (e.g.
        # the information_schema existence checks in apply_indexes.py).
        # Falls back to {"cnt": 0} ("not found yet") once exhausted.
        self._fetchone_results = list(fetchone_results) if fetchone_results else []
        self.last_query = None
        self.last_params = None
        self.execute_calls = []

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params
        self.execute_calls.append((query, params))

    def fetchall(self):
        return self.fetchall_result

    def fetchone(self):
        if self._fetchone_results:
            return self._fetchone_results.pop(0)
        return {"cnt": 0}

    def commit(self):
        pass

    def close(self):
        pass


@pytest.fixture
def fake_cursor():
    """A FakeCursor with an empty default result set."""
    return FakeCursor()


class FakeMongoCollection:
    """
    A minimal in-memory stand-in for a pymongo Collection.

    - insert_one() appends the document to self.inserted (instead of
      writing to a real database).
    - aggregate() returns a pre-configured result list, ignoring the
      pipeline itself, since the tests exercising it care about how the
      calling code consumes the results, not about pipeline execution
      semantics (that's MongoDB's job, not ours to re-test).
    """

    def __init__(self, aggregate_result=None):
        self.inserted = []
        self.aggregate_result = aggregate_result if aggregate_result is not None else []
        self.created_indexes = []

    def insert_one(self, document):
        self.inserted.append(document)
        return type("InsertOneResult", (), {"inserted_id": "fake_id"})()

    def aggregate(self, pipeline):
        self.last_pipeline = pipeline
        return self.aggregate_result

    def create_index(self, keys, **kwargs):
        self.created_indexes.append(keys)
        # Mimics pymongo's real return value: a generated index name.
        return "_".join(f"{field}_{direction}" for field, direction in keys)


@pytest.fixture
def fake_mongo_collection():
    """A FakeMongoCollection with no pre-seeded aggregate results."""
    return FakeMongoCollection()


@pytest.fixture
def sample_film_row():
    """A single representative film row, shaped like the app's SQL queries return it."""
    return {
        "film_id": 1,
        "title": "TEST MOVIE",
        "name": "Action",
        "release_year": 2010,
        "description": "A test film used for unit testing.",
    }


@pytest.fixture
def frozen_now(monkeypatch):
    """
    Freezes datetime.datetime.now() to a fixed point in time for any module
    that does `import datetime` and calls `datetime.datetime.now()`.

    Returns a small helper object exposing `.apply_to(module)` so individual
    tests can freeze time in whichever module they're testing (e.g.
    app.utils.year_utils, app.services.search_service), and `.value` for the
    fixed instant itself.
    """
    fixed = datetime.datetime(2026, 1, 1, 12, 0, 0)

    class _Frozen(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed

    class _Helper:
        value = fixed

        def apply_to(self, module):
            monkeypatch.setattr(module.datetime, "datetime", _Frozen)

    return _Helper()
