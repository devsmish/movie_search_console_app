import pytest

from app.db import sql_queries


class TestKeywordQueryCaseHandling:
    """
    Regression test for a real bug: keyword_query used to compare
    UPPER(title) against an already-lowercased search pattern, which meant
    a keyword search could never match anything with letters in it.
    """

    def test_keyword_query_uses_lower_not_upper(self):
        assert "LOWER(f.title)" in sql_queries.keyword_query
        assert "UPPER(" not in sql_queries.keyword_query


class TestNoHardcodedSchema:
    """
    Regression test: queries used to hardcode a `sakila.` schema prefix,
    which silently ignored whatever MYSQL_DATABASE the user configured.
    """

    ALL_QUERIES = [
        sql_queries.keyword_query,
        sql_queries.genres_years_query,
        sql_queries.genres_query,
        sql_queries.years_query,
        sql_queries.genres_list,
        sql_queries.range_years_query,
    ]

    def test_no_query_references_sakila_schema_directly(self):
        for query in self.ALL_QUERIES:
            assert "sakila." not in query, f"Query still hardcodes schema: {query!r}"


class TestBuildKeywordQuery:
    """
    Tests for the dynamic multi-word/partial-word keyword query builder.
    """

    def test_single_word_matches_static_keyword_query(self):
        assert sql_queries.build_keyword_query(1) == sql_queries.keyword_query

    def test_uses_lower_not_upper(self):
        assert "LOWER(f.title)" in sql_queries.build_keyword_query(3)
        assert "UPPER(" not in sql_queries.build_keyword_query(3)

    def test_no_hardcoded_schema(self):
        assert "sakila." not in sql_queries.build_keyword_query(3)

    def test_placeholder_count_matches_word_count(self):
        for n in (1, 2, 3, 5, 10):
            assert sql_queries.build_keyword_query(n).count("%s") == n

    def test_conditions_are_joined_with_and(self):
        query = sql_queries.build_keyword_query(3)
        assert query.count(" AND ") == 2  # 3 conditions -> 2 "AND" joins

    def test_zero_word_count_raises_value_error(self):
        with pytest.raises(ValueError):
            sql_queries.build_keyword_query(0)

    def test_negative_word_count_raises_value_error(self):
        with pytest.raises(ValueError):
            sql_queries.build_keyword_query(-1)


class TestBuildGenresQuery:
    """
    Tests for the dynamic multi-genre query builder (OR/IN semantics:
    a film matches any of the selected genres).
    """

    def test_uses_in_clause(self):
        assert "IN (%s, %s, %s)" in sql_queries.build_genres_query(3)

    def test_no_hardcoded_schema(self):
        assert "sakila." not in sql_queries.build_genres_query(3)

    def test_placeholder_count_matches_genre_count(self):
        for n in (1, 2, 3, 5, 10):
            assert sql_queries.build_genres_query(n).count("%s") == n

    def test_zero_genre_count_raises_value_error(self):
        with pytest.raises(ValueError):
            sql_queries.build_genres_query(0)

    def test_negative_genre_count_raises_value_error(self):
        with pytest.raises(ValueError):
            sql_queries.build_genres_query(-1)


class TestBuildGenresYearsQuery:
    """
    Tests for the dynamic multi-genre + year-range query builder.
    """

    def test_uses_in_clause_and_year_range(self):
        query = sql_queries.build_genres_years_query(2)
        assert "IN (%s, %s)" in query
        assert "BETWEEN %s AND %s" in query

    def test_no_hardcoded_schema(self):
        assert "sakila." not in sql_queries.build_genres_years_query(3)

    def test_placeholder_count_is_genre_count_plus_two(self):
        for n in (1, 2, 3, 5):
            assert sql_queries.build_genres_years_query(n).count("%s") == n + 2

    def test_zero_genre_count_raises_value_error(self):
        with pytest.raises(ValueError):
            sql_queries.build_genres_years_query(0)


class TestQueriesAreParameterized:
    """
    Sanity check that queries taking user input use %s placeholders rather
    than string interpolation, since parameterized queries are what
    protects this app from SQL injection.
    """

    def test_keyword_query_uses_placeholder(self):
        assert "%s" in sql_queries.keyword_query

    def test_genres_query_uses_placeholder(self):
        assert "%s" in sql_queries.genres_query

    def test_years_query_uses_placeholders(self):
        assert sql_queries.years_query.count("%s") == 2

    def test_genres_years_query_uses_placeholders(self):
        assert sql_queries.genres_years_query.count("%s") == 3

    def test_genres_list_and_range_years_take_no_parameters(self):
        # These two queries have no user-supplied filters, so no
        # placeholders are expected.
        assert "%s" not in sql_queries.genres_list
        assert "%s" not in sql_queries.range_years_query
