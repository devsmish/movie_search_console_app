import pytest

from app.services import search_service
from app.services.search_service import execute_search


@pytest.fixture(autouse=True)
def _silence_pagination(monkeypatch):
    """
    Search results are printed via print_results_paginated(), which calls
    input() when there's more than one page or any results at all with a
    "q"/nav prompt. Route it straight to "q" so these tests don't hang
    waiting on stdin and stay focused on execute_search's own behavior.
    """
    monkeypatch.setattr("builtins.input", lambda prompt="": "q")


class TestExecuteSearchHappyPath:
    def test_calls_search_func_and_logs_results(self, fake_mongo_collection):
        rows = [{"film_id": 1, "title": "X", "name": "Action", "release_year": 2000}]
        execute_search(
            search_func=lambda: rows,
            mongo_collection=fake_mongo_collection,
            search_type="keyword",
            params={"keyword": "x"},
        )
        assert len(fake_mongo_collection.inserted) == 1
        logged = fake_mongo_collection.inserted[0]
        assert logged["search_type"] == "keyword"
        assert logged["params"] == {"keyword": "x"}
        assert logged["results_count"] == 1
        assert logged["success"] is True

    def test_logs_zero_results_as_success(self, fake_mongo_collection):
        execute_search(
            search_func=lambda: [],
            mongo_collection=fake_mongo_collection,
            search_type="keyword",
            params={"keyword": "nonexistent"},
        )
        logged = fake_mongo_collection.inserted[0]
        assert logged["results_count"] == 0
        assert logged["success"] is True

    def test_duration_is_recorded_as_nonnegative_float(self, fake_mongo_collection):
        execute_search(
            search_func=lambda: [],
            mongo_collection=fake_mongo_collection,
            search_type="keyword",
            params={"keyword": "x"},
        )
        logged = fake_mongo_collection.inserted[0]
        assert isinstance(logged["duration_ms"], float)
        assert logged["duration_ms"] >= 0


class TestExecuteSearchErrorHandling:
    def test_search_func_exception_is_caught_and_logged_as_failure(self, fake_mongo_collection, capsys):
        def broken_search():
            raise Exception("query failed")

        execute_search(
            search_func=broken_search,
            mongo_collection=fake_mongo_collection,
            search_type="keyword",
            params={"keyword": "x"},
        )
        logged = fake_mongo_collection.inserted[0]
        assert logged["success"] is False
        assert logged["results_count"] == 0
        captured = capsys.readouterr()
        assert "EXECUTE_SEARCH" in captured.out

    def test_logging_failure_does_not_raise(self, capsys):
        class BrokenMongoCollection:
            def insert_one(self, doc):
                raise Exception("mongo is down")

        # Must not raise. Note: log_request() catches its own exceptions
        # internally (see test_log_service.py), so execute_search's own
        # try/except around log_request never actually fires here — this
        # test is about the overall call not raising, end to end.
        execute_search(
            search_func=lambda: [],
            mongo_collection=BrokenMongoCollection(),
            search_type="keyword",
            params={"keyword": "x"},
        )
        captured = capsys.readouterr()
        assert "LOG_REQUEST" in captured.out

    def test_pagination_failure_does_not_prevent_logging(self, fake_mongo_collection, monkeypatch, capsys):
        def broken_pagination(results):
            raise Exception("display crashed")

        monkeypatch.setattr(search_service, "print_results_paginated", broken_pagination)
        execute_search(
            search_func=lambda: [{"film_id": 1}],
            mongo_collection=fake_mongo_collection,
            search_type="keyword",
            params={"keyword": "x"},
        )
        # Logging should still have happened despite the display error.
        assert len(fake_mongo_collection.inserted) == 1
