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
