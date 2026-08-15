from unittest.mock import MagicMock, patch

import app.menu.stats_menu as stats_menu_module
from app.menu.stats_menu import stats_menu


class TestStatsMenuRouting:
    def test_option_1_calls_top5_requests(self, monkeypatch):
        responses = iter(["1", "q"])
        with patch.object(stats_menu_module, "top5_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_2_calls_last5_requests(self, monkeypatch):
        responses = iter(["2", "q"])
        with patch.object(stats_menu_module, "last5_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_q_returns_without_calling_any_report(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        with patch.object(stats_menu_module, "top5_requests") as top5, \
             patch.object(stats_menu_module, "last5_requests") as last5:
            stats_menu(MagicMock())
        top5.assert_not_called()
        last5.assert_not_called()

    def test_keyboard_interrupt_returns_cleanly(self, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        stats_menu(MagicMock())  # must not raise

    def test_invalid_choice_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["9", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        stats_menu(MagicMock())
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out
