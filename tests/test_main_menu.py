from unittest.mock import MagicMock, patch

import app.menu.main_menu as main_menu_module
from app.menu.main_menu import main_menu
from config import ConfigError


def _patched(connection=None, mongo_collection=None):
    """
    Helper: patches get_connection/get_mongo_collection for main_menu(),
    and short-circuits Config.validate() to a no-op — these tests exercise
    menu routing/connection lifecycle, not configuration validation (see
    TestMainMenuConfigValidation below for that), and the test environment
    has no real .env, so an unpatched Config.validate() would always raise.
    """
    connection = connection or MagicMock()
    mongo_collection = mongo_collection or MagicMock()
    return (
        patch.object(main_menu_module, "get_connection", return_value=connection),
        patch.object(main_menu_module, "get_mongo_collection", return_value=mongo_collection),
        patch.object(main_menu_module.Config, "validate", return_value=None),
        connection,
    )


class TestMainMenuRouting:
    def test_option_1_opens_search_menu(self, monkeypatch):
        p1, p2, p3, connection = _patched()
        responses = iter(["1", "q", "q"])  # main->search, search->quit, main->quit
        with p1, p2, p3, patch.object(main_menu_module, "search_menu") as search_menu:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        search_menu.assert_called_once()

    def test_option_2_opens_stats_menu(self, monkeypatch):
        p1, p2, p3, connection = _patched()
        responses = iter(["2", "q"])
        with p1, p2, p3, patch.object(main_menu_module, "stats_menu") as stats_menu:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        stats_menu.assert_called_once()

    def test_q_exits_immediately(self, monkeypatch):
        p1, p2, p3, connection = _patched()
        with p1, p2, p3:
            monkeypatch.setattr("builtins.input", lambda prompt="": "q")
            main_menu()  # must return without error

    def test_empty_input_is_rejected_then_retried(self, monkeypatch, capsys):
        p1, p2, p3, connection = _patched()
        responses = iter(["", "q"])
        with p1, p2, p3:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        captured = capsys.readouterr()
        assert "Empty input is not allowed" in captured.out

    def test_invalid_choice_is_rejected_then_retried(self, monkeypatch, capsys):
        p1, p2, p3, connection = _patched()
        responses = iter(["9", "q"])
        with p1, p2, p3:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            main_menu()
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out


class TestMainMenuConnectionLifecycle:
    def test_connection_closed_on_normal_exit(self, monkeypatch):
        p1, p2, p3, connection = _patched()
        with p1, p2, p3:
            monkeypatch.setattr("builtins.input", lambda prompt="": "q")
            main_menu()
        connection.close.assert_called_once()

    def test_connection_closed_even_if_submenu_raises(self, monkeypatch):
        # Regression test: connections used to only close after the while
        # loop finished, so an unhandled exception mid-session left them
        # dangling. They must now close via try/finally regardless.
        p1, p2, p3, connection = _patched()
        with p1, p2, p3, patch.object(main_menu_module, "search_menu", side_effect=RuntimeError("boom")):
            monkeypatch.setattr("builtins.input", lambda prompt="": "1")
            try:
                main_menu()
            except RuntimeError:
                pass
        connection.close.assert_called_once()

    def test_startup_failure_is_reported_and_menu_never_shown(self, capsys):
        p3 = patch.object(main_menu_module.Config, "validate", return_value=None)
        with p3, patch.object(main_menu_module, "get_connection", side_effect=Exception("db unreachable")):
            main_menu()
        captured = capsys.readouterr()
        assert "db unreachable" in captured.out
        assert "MAIN MENU" not in captured.out


class TestMainMenuConfigValidation:
    """
    Regression tests for the 4.3.0 startup config check: a missing/misnamed
    .env variable should be reported clearly and stop the app before any
    connection is attempted, rather than surfacing as a confusing
    low-level pymysql/pymongo error.
    """

    def test_missing_config_is_reported_and_no_connection_is_attempted(self, capsys):
        with patch.object(
            main_menu_module.Config, "validate", side_effect=ConfigError(["MYSQL_HOST", "MONGO_URI"])
        ), patch.object(main_menu_module, "get_connection") as get_connection:
            main_menu()
        captured = capsys.readouterr()
        assert "MYSQL_HOST" in captured.out
        assert "MONGO_URI" in captured.out
        assert "MAIN MENU" not in captured.out
        get_connection.assert_not_called()

    def test_config_error_takes_priority_over_generic_startup_error_message(self, capsys):
        # ConfigError is caught by its own except clause (before the
        # generic `except Exception`), so it must produce the
        # config.missing_vars message, not the generic startup_error one.
        with patch.object(
            main_menu_module.Config, "validate", side_effect=ConfigError(["MONGO_DATABASE"])
        ):
            main_menu()
        captured = capsys.readouterr()
        assert "Missing required configuration" in captured.out
        assert "Startup error" not in captured.out
