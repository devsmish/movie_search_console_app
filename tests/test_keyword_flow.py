from app.flows.keyword_flow import input_keyword, keyword_flow


class TestInputKeyword:
    def test_returns_stripped_lowercased_keyword(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "  MATRIX  ")
        assert input_keyword() == "matrix"

    def test_keyboard_interrupt_returns_none(self, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        assert input_keyword() is None


class TestKeywordFlow:
    def test_valid_keyword_triggers_a_logged_search(self, fake_cursor, fake_mongo_collection, monkeypatch):
        responses = iter(["matrix", "q", "q"])  # keyword, pagination exit, then quit flow
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        keyword_flow(fake_cursor, fake_mongo_collection)
        assert len(fake_mongo_collection.inserted) == 1
        assert fake_mongo_collection.inserted[0]["params"] == {"keyword": "matrix"}

    def test_quit_immediately_performs_no_search(self, fake_cursor, fake_mongo_collection, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        keyword_flow(fake_cursor, fake_mongo_collection)
        assert fake_mongo_collection.inserted == []

    def test_empty_keyword_is_rejected_then_retried(self, fake_cursor, fake_mongo_collection, monkeypatch, capsys):
        responses = iter(["", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        keyword_flow(fake_cursor, fake_mongo_collection)
        captured = capsys.readouterr()
        assert "Empty selection" in captured.out
        assert fake_mongo_collection.inserted == []

    def test_ctrl_c_cancels_the_flow(self, fake_cursor, fake_mongo_collection, monkeypatch, capsys):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        keyword_flow(fake_cursor, fake_mongo_collection)
        captured = capsys.readouterr()
        assert "Return to search menu" in captured.out
        assert fake_mongo_collection.inserted == []
