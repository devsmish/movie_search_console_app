from unittest.mock import MagicMock, patch

from app.db.mongo_connection import get_mongo_collection


class TestGetMongoCollection:
    def test_returns_the_configured_collection_on_success(self):
        fake_collection = MagicMock()
        fake_db = MagicMock()
        fake_db.__getitem__.return_value = fake_collection
        fake_client = MagicMock()
        fake_client.__getitem__.return_value = fake_db

        with patch("app.db.mongo_connection.MongoClient", return_value=fake_client):
            result = get_mongo_collection()

        assert result is fake_collection

    def test_pings_the_server_to_verify_connectivity(self):
        fake_client = MagicMock()

        with patch("app.db.mongo_connection.MongoClient", return_value=fake_client):
            get_mongo_collection()

        fake_client.admin.command.assert_called_once_with("ping")

    def test_wraps_connection_failure_in_exception(self):
        with patch("app.db.mongo_connection.MongoClient", side_effect=Exception("no route to host")):
            try:
                get_mongo_collection()
                assert False, "expected an Exception to be raised"
            except Exception as e:
                assert "no route to host" in str(e)

    def test_wraps_failed_ping_in_exception(self):
        fake_client = MagicMock()
        fake_client.admin.command.side_effect = Exception("server selection timeout")

        with patch("app.db.mongo_connection.MongoClient", return_value=fake_client):
            try:
                get_mongo_collection()
                assert False, "expected an Exception to be raised"
            except Exception as e:
                assert "server selection timeout" in str(e)
