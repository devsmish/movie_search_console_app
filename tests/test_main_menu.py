from unittest.mock import MagicMock, patch

import app.menu.main_menu as main_menu_module
from app.menu.main_menu import main_menu


def _patched(connection=None, mongo_collection=None):
    """Helper: patches get_connection/get_mongo_collection for main_menu()."""
    connection = connection or MagicMock()
    mongo_collection = mongo_collection or MagicMock()
    return (
        patch.object(main_menu_module, "get_connection", return_value=connection),
        patch.object(main_menu_module, "get_mongo_collection", return_value=mongo_collection),
        connection,
    )


class TestMainMenuRouting:
    def test_option_1_opens_search_menu(self, monkeypatch):
        p1, p2, connection = _patched()
        responses = iter(["1", "q", "q"])  # main->search, search->quit, main->quit
        with p1, p2, patch.object(main_menu_module, "search_menu") as search_menu:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        search_menu.assert_called_once()

    def test_option_2_opens_stats_menu(self, monkeypatch):
        p1, p2, connection = _patched()
        responses = iter(["2", "q"])
        with p1, p2, patch.object(main_menu_module, "stats_menu") as stats_menu:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        stats_menu.assert_called_once()

    def test_q_exits_immediately(self, monkeypatch):
        p1, p2, connection = _patched()
        with p1, p2:
            monkeypatch.setattr("builtins.input", lambda prompt="": "q")
            main_menu()  # must return without error

    def test_empty_input_is_rejected_then_retried(self, monkeypatch, capsys):
        p1, p2, connection = _patched()
        responses = iter(["", "q"])
        with p1, p2:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        captured = capsys.readouterr()
        assert "Empty input is not allowed" in captured.out

    def test_invalid_choice_is_rejected_then_retried(self, monkeypatch, capsys):
        p1, p2, connection = _patched()
        responses = iter(["9", "q"])
        with p1, p2:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out


class TestMainMenuConnectionLifecycle:
    def test_connection_closed_on_normal_exit(self, monkeypatch):
        p1, p2, connection = _patched()
        with p1, p2:
            monkeypatch.setattr("builtins.input", lambda prompt="": "q")
            main_menu()
        connection.close.assert_called_once()

    def test_connection_closed_even_if_submenu_raises(self, monkeypatch):
        # Regression test: connections used to only close after the while
        # loop finished, so an unhandled exception mid-session left them
        # dangling. They must now close via try/finally regardless.
        p1, p2, connection = _patched()
        with p1, p2, patch.object(main_menu_module, "search_menu", side_effect=RuntimeError("boom")):
            monkeypatch.setattr("builtins.input", lambda prompt="": "1")
            try:
                main_menu()
            except RuntimeError:
                pass
        connection.close.assert_called_once()

    def test_startup_failure_is_reported_and_menu_never_shown(self, capsys):
        with patch.object(main_menu_module, "get_connection", side_effect=Exception("db unreachable")):
            main_menu()
        captured = capsys.readouterr()
        assert "db unreachable" in captured.out
        assert "MAIN MENU" not in captured.out
