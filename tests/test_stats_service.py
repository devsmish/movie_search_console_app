from tests.conftest import FakeMongoCollection
from app.services.stats_service import last5_requests, top5_requests


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
