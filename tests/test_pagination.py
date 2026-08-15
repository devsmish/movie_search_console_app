import pytest

from app.utils.pagination import print_results_paginated


def make_rows(n):
    return [
        {"film_id": i, "title": f"Movie {i}", "name": "Action", "release_year": 2000 + i}
        for i in range(1, n + 1)
    ]


class TestEmptyResults:
    def test_prints_nothing_found_message(self, capsys, monkeypatch):
        # No input() call should even happen, since the function returns
        # immediately for an empty result set.
        monkeypatch.setattr("builtins.input", lambda prompt="": pytest.fail("input() should not be called"))
        print_results_paginated([])
        captured = capsys.readouterr()
        assert "Nothing found!" in captured.out


class TestSinglePage:
    def test_shows_result_count(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        print_results_paginated(make_rows(3), page_size=10)
        captured = capsys.readouterr()
        assert "Results found: 3" in captured.out

    def test_lists_all_rows_when_fewer_than_page_size(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        print_results_paginated(make_rows(3), page_size=10)
        captured = capsys.readouterr()
        assert "Movie 1" in captured.out
        assert "Movie 2" in captured.out
        assert "Movie 3" in captured.out

    def test_quit_command_exits_cleanly(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        print_results_paginated(make_rows(1), page_size=10)
        captured = capsys.readouterr()
        assert "Exit viewing results" in captured.out


class TestMultiplePages:
    def test_next_page_shows_second_page_rows(self, capsys, monkeypatch):
        # Page 1 shows rows 1-2, "n" advances to page 2 which shows row 3,
        # then "q" exits.
        responses = iter(["n", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(3), page_size=2)
        captured = capsys.readouterr()
        assert "Movie 3" in captured.out

    def test_cannot_go_past_last_page(self, capsys, monkeypatch):
        # "n" on the last page is an unavailable command, not a crash.
        responses = iter(["n", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(1), page_size=10)
        captured = capsys.readouterr()
        assert "Unavailable command" in captured.out

    def test_previous_page_navigates_back(self, capsys, monkeypatch):
        responses = iter(["n", "p", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(3), page_size=2)
        captured = capsys.readouterr()
        # After going to page 2 and back to page 1, row "Movie 1" should
        # have been printed again.
        assert captured.out.count("Movie 1") == 2

    def test_cannot_go_before_first_page(self, capsys, monkeypatch):
        responses = iter(["p", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(3), page_size=2)
        captured = capsys.readouterr()
        assert "Unavailable command" in captured.out


class TestInvalidCommand:
    def test_unknown_command_shows_error_and_reprompts(self, capsys, monkeypatch):
        responses = iter(["zzz", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(1), page_size=10)
        captured = capsys.readouterr()
        assert "Unavailable command" in captured.out


class TestKeyboardInterrupt:
    def test_ctrl_c_exits_without_crashing(self, capsys, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        print_results_paginated(make_rows(1), page_size=10)  # must not raise
        captured = capsys.readouterr()
        assert "Exit viewing results" in captured.out
