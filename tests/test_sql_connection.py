from unittest.mock import MagicMock, patch

from app.db import sql_queries
from app.db.sql_connection import (
    MAX_KEYWORD_WORDS,
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


class TestKeywordsSearchMultiWord:
    """
    Tests for searching by several words or word-parts at once, e.g.
    "gone wind" matching "Gone with the Wind".
    """

    def test_splits_input_into_separate_terms(self, fake_cursor):
        keywords_search("gone wind", fake_cursor)
        assert fake_cursor.last_params == ("%gone%", "%wind%")

    def test_uses_a_query_with_one_condition_per_word(self, fake_cursor):
        keywords_search("gone wind", fake_cursor)
        assert fake_cursor.last_query == sql_queries.build_keyword_query(2)
        assert fake_cursor.last_query.count("%s") == 2

    def test_word_order_in_the_query_matches_input_order(self, fake_cursor):
        # (The DB itself treats all conditions as AND, so order doesn't
        # affect matching — this just documents the deterministic mapping
        # from input words to placeholders.)
        keywords_search("wind gone", fake_cursor)
        assert fake_cursor.last_params == ("%wind%", "%gone%")

    def test_collapses_multiple_spaces_between_words(self, fake_cursor):
        keywords_search("gone    wind", fake_cursor)
        assert fake_cursor.last_params == ("%gone%", "%wind%")

    def test_ignores_leading_and_trailing_whitespace(self, fake_cursor):
        keywords_search("  gone wind  ", fake_cursor)
        assert fake_cursor.last_params == ("%gone%", "%wind%")

    def test_deduplicates_repeated_words(self, fake_cursor):
        keywords_search("the the matrix", fake_cursor)
        assert fake_cursor.last_params == ("%the%", "%matrix%")

    def test_three_words_produce_three_and_joined_conditions(self, fake_cursor):
        keywords_search("the matrix reloaded", fake_cursor)
        assert fake_cursor.last_query.count(" AND ") == 2
        assert fake_cursor.last_params == ("%the%", "%matrix%", "%reloaded%")

    def test_word_can_be_a_partial_word(self, fake_cursor):
        # A single search term is still substring/partial matching, just
        # like before multi-word support was added.
        keywords_search("matr", fake_cursor)
        assert fake_cursor.last_params == ("%matr%",)


class TestKeywordsSearchWordCap:
    def test_caps_at_max_keyword_words(self, fake_cursor):
        words = " ".join(f"word{i}" for i in range(MAX_KEYWORD_WORDS + 5))
        keywords_search(words, fake_cursor)
        assert len(fake_cursor.last_params) == MAX_KEYWORD_WORDS

    def test_extra_words_beyond_the_cap_are_dropped_from_the_end(self, fake_cursor):
        words = " ".join(f"word{i}" for i in range(MAX_KEYWORD_WORDS + 2))
        keywords_search(words, fake_cursor)
        expected = tuple(f"%word{i}%" for i in range(MAX_KEYWORD_WORDS))
        assert fake_cursor.last_params == expected

    def test_exactly_at_the_cap_is_not_truncated(self, fake_cursor):
        words = " ".join(f"word{i}" for i in range(MAX_KEYWORD_WORDS))
        keywords_search(words, fake_cursor)
        assert len(fake_cursor.last_params) == MAX_KEYWORD_WORDS


class TestKeywordsSearchEmptyInput:
    def test_empty_string_returns_empty_list_without_querying(self, fake_cursor):
        result = keywords_search("", fake_cursor)
        assert result == []
        assert fake_cursor.last_query is None

    def test_whitespace_only_returns_empty_list_without_querying(self, fake_cursor):
        result = keywords_search("   ", fake_cursor)
        assert result == []
        assert fake_cursor.last_query is None


class TestListGenres:
    def test_executes_genre_list_query(self, fake_cursor):
        list_genres(fake_cursor)
        assert fake_cursor.last_query == sql_queries.genres_list

    def test_passes_no_params(self, fake_cursor):
        list_genres(fake_cursor)
        assert fake_cursor.last_params is None


class TestGenresSearch:
    def test_single_genre(self, fake_cursor):
        genres_search(fake_cursor, ["Comedy"])
        assert fake_cursor.last_query == sql_queries.build_genres_query(1)
        assert fake_cursor.last_params == ("Comedy",)

    def test_multiple_genres_use_in_clause(self, fake_cursor):
        genres_search(fake_cursor, ["Comedy", "Action"])
        assert "IN (%s, %s)" in fake_cursor.last_query
        assert fake_cursor.last_params == ("Comedy", "Action")

    def test_preserves_selection_order(self, fake_cursor):
        genres_search(fake_cursor, ["Action", "Comedy", "Drama"])
        assert fake_cursor.last_params == ("Action", "Comedy", "Drama")

    def test_deduplicates_repeated_genres(self, fake_cursor):
        genres_search(fake_cursor, ["Action", "Comedy", "Action"])
        assert fake_cursor.last_params == ("Action", "Comedy")

    def test_empty_list_returns_empty_without_querying(self, fake_cursor):
        result = genres_search(fake_cursor, [])
        assert result == []
        assert fake_cursor.last_query is None

    def test_caps_at_max_selected_genres(self, fake_cursor):
        from app.db.sql_connection import MAX_SELECTED_GENRES

        genres = [f"Genre{i}" for i in range(MAX_SELECTED_GENRES + 5)]
        genres_search(fake_cursor, genres)
        assert len(fake_cursor.last_params) == MAX_SELECTED_GENRES


class TestYearsSearch:
    def test_executes_years_query_with_range_params(self, fake_cursor):
        years_search(fake_cursor, 2000, 2010)
        assert fake_cursor.last_query == sql_queries.years_query
        assert fake_cursor.last_params == (2000, 2010)

    def test_uses_documented_defaults_when_omitted(self, fake_cursor):
        years_search(fake_cursor)
        assert fake_cursor.last_params == (1990, 2025)


class TestGenreYearsSearch:
    def test_single_genre(self, fake_cursor):
        genre_years_search(fake_cursor, ["Action"], 1995, 2005)
        assert fake_cursor.last_query == sql_queries.build_genres_years_query(1)
        assert fake_cursor.last_params == ("Action", 1995, 2005)

    def test_multiple_genres_use_in_clause_plus_year_range(self, fake_cursor):
        genre_years_search(fake_cursor, ["Action", "Comedy"], 1995, 2005)
        assert "IN (%s, %s)" in fake_cursor.last_query
        assert fake_cursor.last_params == ("Action", "Comedy", 1995, 2005)

    def test_deduplicates_repeated_genres(self, fake_cursor):
        genre_years_search(fake_cursor, ["Action", "Action"], 1995, 2005)
        assert fake_cursor.last_params == ("Action", 1995, 2005)

    def test_empty_list_returns_empty_without_querying(self, fake_cursor):
        result = genre_years_search(fake_cursor, [], 1995, 2005)
        assert result == []
        assert fake_cursor.last_query is None


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
