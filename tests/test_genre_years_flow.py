from tests.conftest import FakeCursor
from app.flows.genre_years_flow import genre_years_flow

GENRES = [
    {"category_id": 1, "name": "Action"},
    {"category_id": 2, "name": "Comedy"},
]


class _MultiQueryCursor(FakeCursor):
    """
    A fake cursor that returns different canned results depending on which
    query is executed, so a single test can exercise get_genres(),
    get_available_year_range(), and the final genre_years_search() in one
    realistic pass through genre_years_flow().
    """

    def __init__(self, film_rows):
        super().__init__()
        self.film_rows = film_rows

    def execute(self, query, params=None):
        super().execute(query, params)

    def fetchall(self):
        if "category_id, name FROM category" in self.last_query:
            return GENRES
        if "MIN(f.release_year)" in self.last_query:
            return [{"min_year": 1990, "max_year": 2025}]
        return self.film_rows


class TestGenreYearsFlow:
    def test_full_happy_path_logs_a_search(self, fake_mongo_collection, monkeypatch):
        film_rows = [{"film_id": 1, "title": "X", "name": "Action", "release_year": 2000}]
        cursor = _MultiQueryCursor(film_rows)

        # genre selection "1", year range "1995-2005", then pagination "q"
        responses = iter(["1", "1995-2005", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

        genre_years_flow(cursor, fake_mongo_collection)

        assert len(fake_mongo_collection.inserted) == 1
        logged = fake_mongo_collection.inserted[0]
        assert logged["search_type"] == "genre_years"
        assert logged["params"] == {"genres": ["Action"], "start_year": 1995, "end_year": 2005}

    def test_multiple_genres_are_passed_through_to_the_search(self, fake_mongo_collection, monkeypatch):
        film_rows = [{"film_id": 1, "title": "X", "name": "Action", "release_year": 2000}]
        cursor = _MultiQueryCursor(film_rows)

        # genre selection "1,2" (Action + Comedy), year range, pagination exit
        responses = iter(["1,2", "1995-2005", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

        genre_years_flow(cursor, fake_mongo_collection)

        logged = fake_mongo_collection.inserted[0]
        assert logged["params"] == {"genres": ["Action", "Comedy"], "start_year": 1995, "end_year": 2005}
        assert logged["query_key"] == "genre_years_Action+Comedy_1995_2005"
        # The final genre_years_search() call should carry both genre names
        # plus the year range as params, in that order.
        assert cursor.last_params == ("Action", "Comedy", 1995, 2005)

    def test_cancelling_genre_selection_skips_search(self, fake_mongo_collection, monkeypatch):
        cursor = _MultiQueryCursor([])
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")  # quits genre selection
        genre_years_flow(cursor, fake_mongo_collection)
        assert fake_mongo_collection.inserted == []

    def test_cancelling_year_range_skips_search(self, fake_mongo_collection, monkeypatch):
        cursor = _MultiQueryCursor([])
        responses = iter(["1", "q"])  # picks genre, then quits year range
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        genre_years_flow(cursor, fake_mongo_collection)
        assert fake_mongo_collection.inserted == []
