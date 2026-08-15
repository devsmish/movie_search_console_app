import pytest

from tests.conftest import FakeCursor
from app.flows.years_flow import (
    DEFAULT_MIN_YEAR,
    get_available_year_range,
    get_year_range,
    show_years,
    years_flow,
)


class TestGetAvailableYearRange:
    def test_returns_min_and_max_from_database(self):
        cursor = FakeCursor(fetchall_result=[{"min_year": 1990, "max_year": 2020}])
        assert get_available_year_range(cursor) == (1990, 2020)

    def test_falls_back_when_query_raises(self):
        class BrokenCursor(FakeCursor):
            def execute(self, query, params=None):
                raise Exception("connection lost")

        result = get_available_year_range(BrokenCursor())
        assert result[0] == DEFAULT_MIN_YEAR

    def test_falls_back_when_result_is_empty(self):
        cursor = FakeCursor(fetchall_result=[])
        result = get_available_year_range(cursor)
        assert result[0] == DEFAULT_MIN_YEAR

    def test_falls_back_when_min_or_max_is_null(self):
        # This happens if the underlying table has no rows at all.
        cursor = FakeCursor(fetchall_result=[{"min_year": None, "max_year": None}])
        result = get_available_year_range(cursor)
        assert result[0] == DEFAULT_MIN_YEAR


class TestShowYears:
    def test_prints_the_given_range(self, capsys):
        show_years(1990, 2020)
        captured = capsys.readouterr()
        assert "1990" in captured.out
        assert "2020" in captured.out


class TestGetYearRange:
    def test_single_year_sets_start_equal_to_end(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "2005")
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2005, "end_year": 2005}

    def test_dash_separated_range(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "2000-2010")
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2000, "end_year": 2010}

    def test_slash_separated_range(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "2000/2010")
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2000, "end_year": 2010}

    def test_space_separated_range(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "2000 2010")
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2000, "end_year": 2010}

    def test_quit_returns_none(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        assert get_year_range(1990, 2020) is None

    def test_keyboard_interrupt_returns_none(self, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        assert get_year_range(1990, 2020) is None

    def test_start_after_end_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["2010-2000", "2000-2010"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2000, "end_year": 2010}
        captured = capsys.readouterr()
        assert "Start year cannot be greater" in captured.out

    def test_out_of_range_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["1900-1950", "2000-2010"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2000, "end_year": 2010}
        captured = capsys.readouterr()
        assert "Year out of range" in captured.out

    def test_malformed_range_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["2000-2005-2010", "2000-2010"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2000, "end_year": 2010}
        captured = capsys.readouterr()
        assert "correct format" in captured.out

    def test_non_numeric_input_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["not-a-year", "2005"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2005, "end_year": 2005}

    def test_empty_input_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["", "2005"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        result = get_year_range(1990, 2020)
        assert result == {"start_year": 2005, "end_year": 2005}
        captured = capsys.readouterr()
        assert "Empty input" in captured.out


class _RangeAwareCursor(FakeCursor):
    """Returns the DB year range for range_years_query, film rows otherwise."""

    def __init__(self, film_rows):
        super().__init__()
        self.film_rows = film_rows

    def fetchall(self):
        if self.last_query and "MIN(f.release_year)" in self.last_query:
            return [{"min_year": 1990, "max_year": 2025}]
        return self.film_rows


class TestYearsFlow:
    def test_valid_range_triggers_a_logged_search(self, fake_mongo_collection, monkeypatch):
        film_rows = [{"film_id": 1, "title": "X", "name": "Action", "release_year": 2000}]
        cursor = _RangeAwareCursor(film_rows)
        responses = iter(["1995-2005", "q"])  # year range, then pagination exit
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        years_flow(cursor, fake_mongo_collection)
        assert len(fake_mongo_collection.inserted) == 1
        assert fake_mongo_collection.inserted[0]["params"] == {"start_year": 1995, "end_year": 2005}

    def test_cancelling_year_range_skips_search(self, fake_mongo_collection, monkeypatch):
        cursor = _RangeAwareCursor([])
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        years_flow(cursor, fake_mongo_collection)
        assert fake_mongo_collection.inserted == []
