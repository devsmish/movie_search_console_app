from unittest.mock import MagicMock, patch

from app.db import sql_queries
from app.db.sql_connection import (
    genre_years_search,
    genres_search,
    get_connection,
    keywords_search,
    list_genres,
    range_years,
    years_search,
)


class TestKeywordsSearch:
    def test_executes_keyword_query(self, fake_cursor):
        keywords_search("Matrix", fake_cursor)
        assert fake_cursor.last_query == sql_queries.keyword_query

    def test_lowercases_keyword_and_wraps_in_wildcards(self, fake_cursor):
        keywords_search("MaTrIx", fake_cursor)
        assert fake_cursor.last_params == ("%matrix%",)

    def test_returns_cursor_fetchall_result(self, sample_film_row):
        from tests.conftest import FakeCursor

        cursor = FakeCursor(fetchall_result=[sample_film_row])
        result = keywords_search("test", cursor)
        assert result == [sample_film_row]


class TestListGenres:
    def test_executes_genre_list_query(self, fake_cursor):
        list_genres(fake_cursor)
        assert fake_cursor.last_query == sql_queries.genres_list

    def test_passes_no_params(self, fake_cursor):
        list_genres(fake_cursor)
        assert fake_cursor.last_params is None


class TestGenresSearch:
    def test_executes_genres_query_with_genre_param(self, fake_cursor):
        genres_search(fake_cursor, "Comedy")
        assert fake_cursor.last_query == sql_queries.genres_query
        assert fake_cursor.last_params == ("Comedy",)


class TestYearsSearch:
    def test_executes_years_query_with_range_params(self, fake_cursor):
        years_search(fake_cursor, 2000, 2010)
        assert fake_cursor.last_query == sql_queries.years_query
        assert fake_cursor.last_params == (2000, 2010)

    def test_uses_documented_defaults_when_omitted(self, fake_cursor):
        years_search(fake_cursor)
        assert fake_cursor.last_params == (1990, 2025)


class TestGenreYearsSearch:
    def test_executes_combined_query_with_all_params(self, fake_cursor):
        genre_years_search(fake_cursor, "Action", 1995, 2005)
        assert fake_cursor.last_query == sql_queries.genres_years_query
        assert fake_cursor.last_params == ("Action", 1995, 2005)


class TestRangeYears:
    def test_executes_range_years_query(self, fake_cursor):
        range_years(fake_cursor)
        assert fake_cursor.last_query == sql_queries.range_years_query

    def test_returns_min_and_max_year_row(self):
        from tests.conftest import FakeCursor

        cursor = FakeCursor(fetchall_result=[{"min_year": 1990, "max_year": 2025}])
        result = range_years(cursor)
        assert result == [{"min_year": 1990, "max_year": 2025}]


class TestGetConnection:
    def test_returns_connection_on_success(self):
        fake_connection = MagicMock()
        with patch("app.db.sql_connection.pymysql.connect", return_value=fake_connection):
            result = get_connection()
        assert result is fake_connection

    def test_pings_the_connection_with_reconnect(self):
        fake_connection = MagicMock()
        with patch("app.db.sql_connection.pymysql.connect", return_value=fake_connection):
            get_connection()
        fake_connection.ping.assert_called_once_with(reconnect=True)

    def test_wraps_connection_failure_in_exception(self):
        with patch("app.db.sql_connection.pymysql.connect", side_effect=Exception("refused")):
            try:
                get_connection()
                assert False, "expected an Exception to be raised"
            except Exception as e:
                assert "refused" in str(e)
