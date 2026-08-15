import datetime

from app.services.log_service import log_request


class TestLogRequestHappyPath:
    def test_inserts_one_document(self, fake_mongo_collection):
        log_request(fake_mongo_collection, "keyword", {"keyword": "matrix"}, 5, 12.3, True)
        assert len(fake_mongo_collection.inserted) == 1

    def test_document_contains_expected_fields(self, fake_mongo_collection):
        log_request(fake_mongo_collection, "genre", {"genre": "Comedy"}, 10, 4.5, True)
        doc = fake_mongo_collection.inserted[0]
        assert doc["search_type"] == "genre"
        assert doc["params"] == {"genre": "Comedy"}
        assert doc["results_count"] == 10
        assert doc["duration_ms"] == 4.5
        assert doc["success"] is True
        assert doc["query_key"] == "genre_Comedy"

    def test_timestamp_is_recorded_as_datetime(self, fake_mongo_collection):
        log_request(fake_mongo_collection, "keyword", {"keyword": "x"}, 0, 1.0, True)
        doc = fake_mongo_collection.inserted[0]
        assert isinstance(doc["timestamp"], datetime.datetime)

    def test_failed_search_is_logged_with_success_false(self, fake_mongo_collection):
        log_request(fake_mongo_collection, "keyword", {"keyword": "x"}, 0, 1.0, False)
        doc = fake_mongo_collection.inserted[0]
        assert doc["success"] is False


class TestLogRequestErrorHandling:
    def test_insert_failure_does_not_raise(self, capsys):
        class BrokenMongoCollection:
            def insert_one(self, doc):
                raise Exception("connection reset")

        # Should not raise; the function is expected to swallow the error.
        log_request(BrokenMongoCollection(), "keyword", {"keyword": "x"}, 0, 1.0, True)
        captured = capsys.readouterr()
        assert "LOG_REQUEST" in captured.out

    def test_query_key_build_failure_falls_back_to_unknown_query(self, fake_mongo_collection):
        # Missing the 'keyword' param that build_query_key needs for this
        # search_type still results in a logged document, just with the
        # 'unknown_query' fallback key rather than a crash.
        log_request(fake_mongo_collection, "keyword", {}, 0, 1.0, True)
        doc = fake_mongo_collection.inserted[0]
        assert doc["query_key"] == "unknown_query"
