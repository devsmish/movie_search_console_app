import json
import os
from datetime import datetime

import pytest

from app.utils.formatting import (
    Column,
    default_export_filename,
    format_table,
    to_csv,
    to_json,
    write_export_file,
)


FILM_ROWS = [
    {"film_id": 1, "title": "Gone with the Wind", "name": "Drama", "release_year": 1939},
    {"film_id": 2, "title": "Matrix", "name": "Action", "release_year": 1999},
]

FILM_COLUMNS = [
    Column(key="film_id", header="Film_ID", max_width=8),
    Column(key="title", header="Title", max_width=10),
    Column(key="name", header="Genre", max_width=10),
    Column(key="release_year", header="Year", max_width=6, align="right"),
]


class TestFormatTable:
    def test_empty_rows_returns_empty_string(self):
        assert format_table([], FILM_COLUMNS) == ""

    def test_header_and_separator_are_present(self):
        table = format_table(FILM_ROWS, FILM_COLUMNS)
        lines = table.split("\n")
        assert "Film_ID" in lines[0]
        assert "Title" in lines[0]
        assert set(lines[1]) == {"-"}

    def test_contains_one_line_per_row_plus_header_and_separator(self):
        table = format_table(FILM_ROWS, FILM_COLUMNS)
        assert len(table.split("\n")) == 2 + len(FILM_ROWS)

    def test_short_values_are_not_truncated(self):
        table = format_table(FILM_ROWS, FILM_COLUMNS)
        assert "Matrix" in table

    def test_long_values_are_truncated_with_ellipsis(self):
        # "Gone with the Wind" is 19 chars, column max_width is 10.
        table = format_table(FILM_ROWS, FILM_COLUMNS)
        assert "Gone with the Wind" not in table
        assert "…" in table

    def test_truncation_keeps_every_row_the_same_width(self):
        # Regression test for the pre-4.3.2 bug: a long title used to
        # push a hand-formatted table out of alignment. Every data line
        # (and the header) must now be exactly the same length.
        rows = FILM_ROWS + [
            {"film_id": 3, "title": "A", "name": "X", "release_year": 2000}
        ]
        table = format_table(rows, FILM_COLUMNS)
        lines = table.split("\n")
        line_lengths = {len(line) for line in lines if set(line) != {"-"}}
        assert len(line_lengths) == 1

    def test_missing_key_renders_as_empty_string(self):
        rows = [{"film_id": 1}]
        table = format_table(rows, FILM_COLUMNS)
        # Should not raise, and should still produce a well-formed row.
        assert len(table.split("\n")) == 3

    def test_none_value_renders_as_empty_string_not_literal_none(self):
        rows = [{"film_id": 1, "title": None, "name": "Drama", "release_year": 2000}]
        table = format_table(rows, FILM_COLUMNS)
        assert "None" not in table

    def test_numbered_defaults_to_true_and_adds_row_numbers(self):
        table = format_table(FILM_ROWS, FILM_COLUMNS)
        lines = table.split("\n")
        assert lines[0].strip().startswith("#")
        assert lines[2].strip().startswith("1")
        assert lines[3].strip().startswith("2")

    def test_numbered_false_omits_row_number_column(self):
        table = format_table(FILM_ROWS, FILM_COLUMNS, numbered=False)
        lines = table.split("\n")
        assert not lines[0].strip().startswith("#")

    def test_right_alignment_pads_on_the_left(self):
        table = format_table(FILM_ROWS, FILM_COLUMNS)
        # release_year column is right-aligned with max_width=6.
        assert "  1939" in table or " 1939" in table

    def test_custom_num_header_is_used(self):
        table = format_table(FILM_ROWS, FILM_COLUMNS, num_header="No.")
        assert "No." in table.split("\n")[0]


class TestToCsv:
    def test_header_row_uses_column_headers(self):
        csv_text = to_csv(FILM_ROWS, FILM_COLUMNS)
        assert csv_text.splitlines()[0] == "Film_ID,Title,Genre,Year"

    def test_one_data_row_per_input_row(self):
        csv_text = to_csv(FILM_ROWS, FILM_COLUMNS)
        assert len(csv_text.splitlines()) == 1 + len(FILM_ROWS)

    def test_long_values_are_not_truncated(self):
        csv_text = to_csv(FILM_ROWS, FILM_COLUMNS)
        assert "Gone with the Wind" in csv_text

    def test_values_with_commas_are_quoted(self):
        rows = [{"film_id": 1, "title": "Hello, World", "name": "Drama", "release_year": 2000}]
        csv_text = to_csv(rows, FILM_COLUMNS)
        assert '"Hello, World"' in csv_text

    def test_missing_key_renders_as_empty_cell(self):
        csv_text = to_csv([{"film_id": 1}], FILM_COLUMNS)
        assert csv_text.splitlines()[1] == "1,,,"

    def test_empty_rows_still_produces_a_header(self):
        csv_text = to_csv([], FILM_COLUMNS)
        assert csv_text.splitlines() == ["Film_ID,Title,Genre,Year"]


class TestToJson:
    def test_without_columns_includes_every_key_as_is(self):
        text = to_json(FILM_ROWS)
        data = json.loads(text)
        assert data == FILM_ROWS

    def test_with_columns_rekeys_to_headers(self):
        text = to_json(FILM_ROWS, FILM_COLUMNS)
        data = json.loads(text)
        assert data[0]["Film_ID"] == 1
        assert data[0]["Title"] == "Gone with the Wind"

    def test_with_columns_excludes_keys_not_listed(self):
        rows = [{"film_id": 1, "title": "X", "name": "Y", "release_year": 2000, "description": "secret"}]
        text = to_json(rows, FILM_COLUMNS)
        data = json.loads(text)
        assert "description" not in data[0]
        assert "Description" not in data[0]

    def test_non_json_native_values_use_str_fallback(self):
        rows = [{"film_id": 1, "title": "X", "name": "Y", "release_year": datetime(2026, 1, 1)}]
        text = to_json(rows)  # must not raise
        data = json.loads(text)
        assert "2026" in data[0]["release_year"]

    def test_empty_rows_renders_as_empty_array(self):
        assert json.loads(to_json([])) == []

    def test_output_is_valid_utf8_not_escaped(self):
        rows = [{"film_id": 1, "title": "Амели", "name": "Drama", "release_year": 2001}]
        text = to_json(rows)
        assert "Амели" in text  # not \u-escaped


class TestDefaultExportFilename:
    def test_uses_prefix_and_extension(self):
        name = default_export_filename("search_results", "csv", now=datetime(2026, 8, 22, 15, 30, 0))
        assert name == "search_results_20260822_153000.csv"

    def test_different_extensions_produce_different_names(self):
        now = datetime(2026, 8, 22, 15, 30, 0)
        csv_name = default_export_filename("search_results", "csv", now=now)
        json_name = default_export_filename("search_results", "json", now=now)
        assert csv_name != json_name
        assert csv_name.endswith(".csv")
        assert json_name.endswith(".json")


class TestWriteExportFile:
    def test_writes_the_given_text(self, tmp_path):
        filepath = str(tmp_path / "out.csv")
        write_export_file("a,b,c\n1,2,3\n", filepath)
        assert open(filepath, encoding="utf-8").read() == "a,b,c\n1,2,3\n"

    def test_creates_missing_parent_directories(self, tmp_path):
        filepath = str(tmp_path / "nested" / "dir" / "out.json")
        write_export_file("{}", filepath)
        assert os.path.exists(filepath)

    def test_returns_the_filepath(self, tmp_path):
        filepath = str(tmp_path / "out.csv")
        assert write_export_file("data", filepath) == filepath

    def test_overwrites_an_existing_file(self, tmp_path):
        filepath = str(tmp_path / "out.csv")
        write_export_file("first", filepath)
        write_export_file("second", filepath)
        assert open(filepath, encoding="utf-8").read() == "second"
