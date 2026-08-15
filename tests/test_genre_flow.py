import pytest

from tests.conftest import FakeCursor
from app.flows.genre_flow import genres_flow, get_genres

GENRES = [
    {"category_id": 1, "name": "Action"},
    {"category_id": 2, "name": "Comedy"},
]


class TestGetGenresHappyPath:
    def test_select_by_number(self, monkeypatch):
        cursor = FakeCursor(fetchall_result=GENRES)
        monkeypatch.setattr("builtins.input", lambda prompt="": "1")
        assert get_genres(cursor) == "Action"

    def test_select_by_name_case_insensitive(self, monkeypatch):
        cursor = FakeCursor(fetchall_result=GENRES)
        monkeypatch.setattr("builtins.input", lambda prompt="": "COMEDY")
        assert get_genres(cursor) == "Comedy"

    def test_only_queries_genres_once_per_call(self, monkeypatch):
        # Regression test: get_genres used to re-fetch the genre list from
        # the database on every failed retry inside the input loop.
        cursor = FakeCursor(fetchall_result=GENRES)
        responses = iter(["nonsense", "1"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        get_genres(cursor)
        assert len(cursor.execute_calls) == 1


class TestGetGenresCancellation:
    def test_quit_returns_none(self, monkeypatch):
        cursor = FakeCursor(fetchall_result=GENRES)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        assert get_genres(cursor) is None

    def test_keyboard_interrupt_returns_none(self, monkeypatch):
        cursor = FakeCursor(fetchall_result=GENRES)

        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        assert get_genres(cursor) is None


class TestGetGenresInvalidChoice:
    def test_invalid_number_is_rejected_then_retried(self, monkeypatch, capsys):
        cursor = FakeCursor(fetchall_result=GENRES)
        responses = iter(["99", "1"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        assert get_genres(cursor) == "Action"
        captured = capsys.readouterr()
        assert "Invalid genre" in captured.out

    def test_unknown_name_is_rejected_then_retried(self, monkeypatch, capsys):
        cursor = FakeCursor(fetchall_result=GENRES)
        responses = iter(["horror", "action"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        assert get_genres(cursor) == "Action"


class TestGetGenresErrorHandling:
    def test_db_error_while_loading_returns_none(self, capsys):
        class BrokenCursor(FakeCursor):
            def execute(self, query, params=None):
                raise Exception("db is down")

        assert get_genres(BrokenCursor()) is None
        captured = capsys.readouterr()
        assert "Error loading genres" in captured.out

    def test_malformed_genre_rows_return_none(self, capsys):
        cursor = FakeCursor(fetchall_result=[{"unexpected_key": "oops"}])
        assert get_genres(cursor) is None
        captured = capsys.readouterr()
        assert "Data structure error" in captured.out


class TestGenresFlow:
    def test_selecting_a_genre_triggers_a_logged_search(self, fake_mongo_collection, monkeypatch):
        cursor = FakeCursor(fetchall_result=GENRES)
        responses = iter(["1", "q", "q"])  # pick Action, exit pagination, quit flow
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        genres_flow(cursor, fake_mongo_collection)
        assert len(fake_mongo_collection.inserted) == 1
        assert fake_mongo_collection.inserted[0]["params"] == {"genre": "Action"}

    def test_quitting_immediately_performs_no_search(self, fake_mongo_collection, monkeypatch):
        cursor = FakeCursor(fetchall_result=GENRES)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        genres_flow(cursor, fake_mongo_collection)
        assert fake_mongo_collection.inserted == []
