from unittest.mock import MagicMock, patch

import app.menu.search_menu as search_menu_module
from app.menu.search_menu import search_menu


class TestSearchMenuRouting:
    def test_option_1_calls_keyword_flow(self, monkeypatch):
        responses = iter(["1", "q"])
        with patch.object(search_menu_module, "keyword_flow") as flow:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            search_menu(MagicMock(), MagicMock())
        flow.assert_called_once()

    def test_option_2_calls_genres_flow(self, monkeypatch):
        responses = iter(["2", "q"])
        with patch.object(search_menu_module, "genres_flow") as flow:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            search_menu(MagicMock(), MagicMock())
        flow.assert_called_once()

    def test_option_3_calls_years_flow(self, monkeypatch):
        responses = iter(["3", "q"])
        with patch.object(search_menu_module, "years_flow") as flow:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            search_menu(MagicMock(), MagicMock())
        flow.assert_called_once()

    def test_option_4_calls_genre_years_flow(self, monkeypatch):
        responses = iter(["4", "q"])
        with patch.object(search_menu_module, "genre_years_flow") as flow:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            search_menu(MagicMock(), MagicMock())
        flow.assert_called_once()

    def test_q_returns_without_calling_any_flow(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        with patch.object(search_menu_module, "keyword_flow") as kw, \
             patch.object(search_menu_module, "genres_flow") as g, \
             patch.object(search_menu_module, "years_flow") as y, \
             patch.object(search_menu_module, "genre_years_flow") as gy:
            search_menu(MagicMock(), MagicMock())
        kw.assert_not_called()
        g.assert_not_called()
        y.assert_not_called()
        gy.assert_not_called()

    def test_keyboard_interrupt_returns_cleanly(self, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        search_menu(MagicMock(), MagicMock())  # must not raise

    def test_invalid_choice_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["9", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        search_menu(MagicMock(), MagicMock())
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out
