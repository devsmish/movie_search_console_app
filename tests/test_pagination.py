import json
import os

import pytest

import app.utils.pagination as pagination_module
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


class TestLongValuesDoNotBreakAlignment:
    # Regression tests for the pre-4.3.2 bug: a title longer than the
    # hand-rolled column width used to push the console table out of
    # alignment. format_table() now truncates instead.
    def test_long_title_is_truncated_not_left_to_overflow(self, capsys, monkeypatch):
        rows = [{"film_id": 1, "title": "A" * 60, "name": "Drama", "release_year": 2000}]
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        print_results_paginated(rows, page_size=10)
        captured = capsys.readouterr()
        assert "A" * 60 not in captured.out
        assert "…" in captured.out

    def test_every_table_line_has_the_same_width(self, capsys, monkeypatch):
        rows = make_rows(2) + [{"film_id": 3, "title": "X" * 80, "name": "Y", "release_year": 2001}]
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        print_results_paginated(rows, page_size=10)
        captured = capsys.readouterr()
        table_lines = [
            line for line in captured.out.split("\n")
            if line and ("Film_ID" in line or line.strip().startswith(tuple("123")) or set(line) == {"-"})
        ]
        widths = {len(line) for line in table_lines}
        assert len(widths) == 1


class TestExportResults:
    def test_export_option_is_shown_in_navigation(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        print_results_paginated(make_rows(1), page_size=10)
        captured = capsys.readouterr()
        assert "Export results" in captured.out

    def test_csv_export_writes_a_file_and_confirms(self, capsys, monkeypatch, tmp_path):
        monkeypatch.setattr(pagination_module, "EXPORT_DIR", str(tmp_path))
        responses = iter(["e", "csv", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(2), page_size=10)
        captured = capsys.readouterr()

        assert "Exported 2 results" in captured.out
        written = list(tmp_path.iterdir())
        assert len(written) == 1
        assert written[0].suffix == ".csv"
        content = written[0].read_text(encoding="utf-8")
        assert "Movie 1" in content
        assert "Movie 2" in content

    def test_json_export_writes_valid_json(self, monkeypatch, tmp_path):
        monkeypatch.setattr(pagination_module, "EXPORT_DIR", str(tmp_path))
        responses = iter(["e", "json", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(2), page_size=10)

        written = list(tmp_path.iterdir())
        assert len(written) == 1
        data = json.loads(written[0].read_text(encoding="utf-8"))
        assert len(data) == 2

    def test_export_includes_all_pages_not_just_current_page(self, monkeypatch, tmp_path):
        monkeypatch.setattr(pagination_module, "EXPORT_DIR", str(tmp_path))
        # 3 rows, page_size=2 -> "e" is issued while still on page 1.
        responses = iter(["e", "csv", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(3), page_size=2)

        written = list(tmp_path.iterdir())
        content = written[0].read_text(encoding="utf-8")
        assert "Movie 1" in content
        assert "Movie 2" in content
        assert "Movie 3" in content

    def test_invalid_format_shows_error_and_does_not_write_a_file(self, capsys, monkeypatch, tmp_path):
        monkeypatch.setattr(pagination_module, "EXPORT_DIR", str(tmp_path))
        responses = iter(["e", "xml", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(1), page_size=10)
        captured = capsys.readouterr()

        assert "Invalid format" in captured.out
        assert list(tmp_path.iterdir()) == []

    def test_export_then_continues_browsing_afterwards(self, capsys, monkeypatch, tmp_path):
        # After a successful export, the pagination loop must keep
        # running (re-show the current page) rather than exiting.
        monkeypatch.setattr(pagination_module, "EXPORT_DIR", str(tmp_path))
        responses = iter(["e", "csv", "n", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        print_results_paginated(make_rows(3), page_size=2)
        captured = capsys.readouterr()
        assert "Movie 3" in captured.out  # reached page 2 after exporting

    def test_ctrl_c_during_format_prompt_cancels_export_cleanly(self, capsys, monkeypatch, tmp_path):
        monkeypatch.setattr(pagination_module, "EXPORT_DIR", str(tmp_path))
        responses = iter(["e"])

        def fake_input(prompt=""):
            value = next(responses, None)
            if value is None:
                raise KeyboardInterrupt
            return value

        monkeypatch.setattr("builtins.input", fake_input)
        print_results_paginated(make_rows(1), page_size=10)  # must not raise
        assert list(tmp_path.iterdir()) == []
