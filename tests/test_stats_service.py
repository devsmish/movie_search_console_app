from tests.conftest import FakeMongoCollection
from app.services import stats_service
from app.services.stats_service import (
    activity_by_day_requests,
    avg_duration_requests,
    genre_co_occurrence_requests,
    last5_requests,
    search_type_breakdown_requests,
    success_rate_requests,
    top5_requests,
    top_genres_requests,
    year_range_popularity_requests,
    zero_result_requests,
)


class TestSeparatorWidthConstant:
    """
    Regression test for the 4.4.0 cleanup: every report's separator line
    must come from the shared SEPARATOR_WIDTH constant, not a hardcoded
    number repeated per report, so they can never drift out of sync.
    """

    def test_top5_report_separator_matches_the_constant(self, capsys, monkeypatch):
        monkeypatch.setattr(stats_service, "SEPARATOR_WIDTH", 20)
        top5_requests(FakeMongoCollection(aggregate_result=[{"_id": "keyword_x", "count": 1}]))
        captured = capsys.readouterr()
        assert "-" * 20 in captured.out
        assert "-" * 88 not in captured.out


class TestTop5Requests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        top5_requests(collection)
        captured = capsys.readouterr()
        assert "REPORT TOP-5 QUERIES" in captured.out

    def test_prints_each_row(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": "keyword_matrix", "count": 5},
                {"_id": "genre_comedy", "count": 3},
            ]
        )
        top5_requests(collection)
        captured = capsys.readouterr()
        assert "keyword_matrix" in captured.out
        assert "genre_comedy" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        top5_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "REPORT TOP-5 QUERIES" in captured.out
        assert "No data yet." in captured.out


class TestLast5Requests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        last5_requests(collection)
        captured = capsys.readouterr()
        assert "REPORT LAST-5 QUERIES" in captured.out

    def test_prints_row_details(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {
                    "query_key": "keyword_matrix",
                    "search_type": "keyword",
                    "results_count": 5,
                    "duration_ms": 12.345,
                }
            ]
        )
        last5_requests(collection)
        captured = capsys.readouterr()
        assert "keyword_matrix" in captured.out
        assert "keyword" in captured.out
        assert "12.345" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        last5_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestZeroResultRequests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        zero_result_requests(collection)
        captured = capsys.readouterr()
        assert "ZERO-RESULT QUERIES" in captured.out

    def test_prints_each_row(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": "keyword_nonexistent", "count": 7, "last_seen": "2026-08-01T00:00:00"},
            ]
        )
        zero_result_requests(collection)
        captured = capsys.readouterr()
        assert "keyword_nonexistent" in captured.out
        assert "7" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        zero_result_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestSearchTypeBreakdownRequests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        search_type_breakdown_requests(collection)
        captured = capsys.readouterr()
        assert "SEARCH TYPE BREAKDOWN" in captured.out

    def test_prints_each_type_with_computed_share(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": "keyword", "count": 3},
                {"_id": "genre", "count": 1},
            ]
        )
        search_type_breakdown_requests(collection)
        captured = capsys.readouterr()
        assert "keyword" in captured.out
        assert "genre" in captured.out
        # 3 out of 4 total = 75.0%
        assert "75.0%" in captured.out
        assert "25.0%" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        search_type_breakdown_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestAvgDurationRequests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        avg_duration_requests(collection)
        captured = capsys.readouterr()
        assert "AVERAGE DURATION BY SEARCH TYPE" in captured.out

    def test_prints_each_row(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": "keyword", "avg_duration_ms": 12.345, "count": 10},
            ]
        )
        avg_duration_requests(collection)
        captured = capsys.readouterr()
        assert "keyword" in captured.out
        assert "12.345" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        avg_duration_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestActivityByDayRequests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        activity_by_day_requests(collection)
        captured = capsys.readouterr()
        assert "SEARCH ACTIVITY BY DAY" in captured.out

    def test_prints_each_row(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": "2026-08-05", "count": 42},
            ]
        )
        activity_by_day_requests(collection)
        captured = capsys.readouterr()
        assert "2026-08-05" in captured.out
        assert "42" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        activity_by_day_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestSuccessRateRequests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        success_rate_requests(collection)
        captured = capsys.readouterr()
        assert "SUCCESS RATE BY SEARCH TYPE" in captured.out

    def test_prints_each_row(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": "keyword", "total": 10, "successful": 9, "success_rate_pct": 90.0},
            ]
        )
        success_rate_requests(collection)
        captured = capsys.readouterr()
        assert "keyword" in captured.out
        assert "90.0%" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        success_rate_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestYearRangePopularityRequests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        year_range_popularity_requests(collection)
        captured = capsys.readouterr()
        assert "POPULAR YEAR RANGES" in captured.out

    def test_prints_each_decade_row(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": 1990, "count": 12},
                {"_id": 2000, "count": 5},
            ]
        )
        year_range_popularity_requests(collection)
        captured = capsys.readouterr()
        assert "1990s" in captured.out
        assert "2000s" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        year_range_popularity_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestTopGenresRequests:
    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        top_genres_requests(collection)
        captured = capsys.readouterr()
        assert "TOP INDIVIDUAL GENRES" in captured.out

    def test_prints_each_genre_row(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"_id": "Action", "count": 15},
                {"_id": "Comedy", "count": 9},
            ]
        )
        top_genres_requests(collection)
        captured = capsys.readouterr()
        assert "Action" in captured.out
        assert "Comedy" in captured.out
        assert "15" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        top_genres_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out


class TestGenreCoOccurrenceRequests:
    """
    Unlike the other reports, this one does its counting in plain Python
    (see the comment on genre_combinations_raw in mongo_queries.py for
    why), so these tests exercise that counting logic directly rather
    than just checking that a pre-aggregated result gets printed.
    """

    def test_prints_report_header(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        genre_co_occurrence_requests(collection)
        captured = capsys.readouterr()
        assert "GENRE CO-OCCURRENCE" in captured.out

    def test_counts_a_single_pair(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[{"genres": ["Action", "Comedy"]}])
        genre_co_occurrence_requests(collection)
        captured = capsys.readouterr()
        assert "Action + Comedy" in captured.out
        assert "| 1" in captured.out

    def test_counts_repeated_pair_across_documents(self, capsys):
        collection = FakeMongoCollection(
            aggregate_result=[
                {"genres": ["Action", "Comedy"]},
                {"genres": ["Comedy", "Action"]},  # same pair, different entry order
            ]
        )
        genre_co_occurrence_requests(collection)
        captured = capsys.readouterr()
        assert "Action + Comedy" in captured.out
        assert "| 2" in captured.out
        # Should NOT appear as two separate rows for "Action + Comedy" and
        # "Comedy + Action" — they're the same pair regardless of order.
        assert captured.out.count("Comedy + Action") == 0

    def test_expands_three_genres_into_three_pairs(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[{"genres": ["Action", "Comedy", "Drama"]}])
        genre_co_occurrence_requests(collection)
        captured = capsys.readouterr()
        assert "Action + Comedy" in captured.out
        assert "Action + Drama" in captured.out
        assert "Comedy + Drama" in captured.out

    def test_deduplicates_repeated_genre_within_one_document(self, capsys):
        # A malformed/duplicate entry like ["Action", "Action", "Comedy"]
        # should still only count as one Action-Comedy pair.
        collection = FakeMongoCollection(aggregate_result=[{"genres": ["Action", "Action", "Comedy"]}])
        genre_co_occurrence_requests(collection)
        captured = capsys.readouterr()
        assert "Action + Comedy" in captured.out
        assert "| 1" in captured.out

    def test_handles_empty_result_without_crashing(self, capsys):
        collection = FakeMongoCollection(aggregate_result=[])
        genre_co_occurrence_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out

    def test_document_with_only_one_unique_genre_after_dedup_yields_no_pairs(self, capsys):
        # Defensive case: a malformed doc like ["Action", "Action"] passes
        # the ".genres.1 exists" filter (it has 2 array elements) but
        # de-duplicates down to a single genre, so it contributes zero
        # pairs. If it's the *only* document, the report should fall back
        # to the "no data" message rather than printing an empty table.
        collection = FakeMongoCollection(aggregate_result=[{"genres": ["Action", "Action"]}])
        genre_co_occurrence_requests(collection)  # must not raise
        captured = capsys.readouterr()
        assert "No data yet." in captured.out
