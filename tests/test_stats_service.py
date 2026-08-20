from tests.conftest import FakeMongoCollection
from app.services.stats_service import (
    activity_by_day_requests,
    avg_duration_requests,
    last5_requests,
    search_type_breakdown_requests,
    success_rate_requests,
    top5_requests,
    zero_result_requests,
)


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
