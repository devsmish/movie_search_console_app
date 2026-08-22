from unittest.mock import MagicMock, patch

import app.menu.stats_menu as stats_menu_module
from app.menu.stats_menu import stats_menu

ALL_REPORT_FUNCS = [
    "top5_requests",
    "last5_requests",
    "zero_result_requests",
    "search_type_breakdown_requests",
    "avg_duration_requests",
    "activity_by_day_requests",
    "success_rate_requests",
    "year_range_popularity_requests",
    "top_genres_requests",
    "genre_co_occurrence_requests",
]


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

    def test_option_3_calls_zero_result_requests(self, monkeypatch):
        responses = iter(["3", "q"])
        with patch.object(stats_menu_module, "zero_result_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_4_calls_search_type_breakdown_requests(self, monkeypatch):
        responses = iter(["4", "q"])
        with patch.object(stats_menu_module, "search_type_breakdown_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_5_calls_avg_duration_requests(self, monkeypatch):
        responses = iter(["5", "q"])
        with patch.object(stats_menu_module, "avg_duration_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_6_calls_activity_by_day_requests(self, monkeypatch):
        responses = iter(["6", "q"])
        with patch.object(stats_menu_module, "activity_by_day_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_7_calls_success_rate_requests(self, monkeypatch):
        responses = iter(["7", "q"])
        with patch.object(stats_menu_module, "success_rate_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_8_calls_year_range_popularity_requests(self, monkeypatch):
        responses = iter(["8", "q"])
        with patch.object(stats_menu_module, "year_range_popularity_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_9_calls_top_genres_requests(self, monkeypatch):
        responses = iter(["9", "q"])
        with patch.object(stats_menu_module, "top_genres_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_option_10_calls_genre_co_occurrence_requests(self, monkeypatch):
        responses = iter(["10", "q"])
        with patch.object(stats_menu_module, "genre_co_occurrence_requests") as report:
            monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
            stats_menu(MagicMock())
        report.assert_called_once()

    def test_q_returns_without_calling_any_report(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        patches = [patch.object(stats_menu_module, name) for name in ALL_REPORT_FUNCS]
        with patches[0] as p0, patches[1] as p1, patches[2] as p2, patches[3] as p3, \
             patches[4] as p4, patches[5] as p5, patches[6] as p6, patches[7] as p7, \
             patches[8] as p8, patches[9] as p9:
            stats_menu(MagicMock())
        for mock in (p0, p1, p2, p3, p4, p5, p6, p7, p8, p9):
            mock.assert_not_called()

    def test_keyboard_interrupt_returns_cleanly(self, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        stats_menu(MagicMock())  # must not raise

    def test_invalid_choice_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["99", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        stats_menu(MagicMock())
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out
