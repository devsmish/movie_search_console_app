import pytest

from app.utils.input_utils import safe_input, build_query_key


class TestSafeInput:
    def test_returns_stripped_lowercased_value(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "  HeLLo  ")
        assert safe_input("prompt: ") == "hello"

    def test_shows_prompt_to_user(self, monkeypatch, capsys):
        seen_prompt = {}

        def fake_input(prompt=""):
            seen_prompt["value"] = prompt
            return "x"

        monkeypatch.setattr("builtins.input", fake_input)
        safe_input("Enter something: ")
        assert seen_prompt["value"] == "Enter something: "

    def test_empty_input_allowed_by_default(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        assert safe_input("prompt: ") == ""

    def test_empty_input_rejected_when_allow_empty_false(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        assert safe_input("prompt: ", allow_empty=False) is None

    def test_whitespace_only_input_counts_as_empty(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "   ")
        assert safe_input("prompt: ", allow_empty=False) is None

    def test_keyboard_interrupt_returns_none(self, monkeypatch, capsys):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        result = safe_input("prompt: ", interrupt_msg="Custom interrupt message")
        assert result is None

    def test_keyboard_interrupt_prints_custom_message(self, monkeypatch, capsys):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        safe_input("prompt: ", interrupt_msg="Custom interrupt message")
        captured = capsys.readouterr()
        assert "Custom interrupt message" in captured.out

    def test_keyboard_interrupt_uses_default_message_when_none_given(self, monkeypatch, capsys):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        safe_input("prompt: ")
        captured = capsys.readouterr()
        assert "Input interrupted by user" in captured.out


class TestBuildQueryKey:
    def test_keyword_query_key(self):
        assert build_query_key("keyword", {"keyword": "matrix"}) == "keyword_matrix"

    def test_genre_query_key_single_genre(self):
        assert build_query_key("genre", {"genres": ["Comedy"]}) == "genre_Comedy"

    def test_genre_query_key_multiple_genres(self):
        assert build_query_key("genre", {"genres": ["Comedy", "Action"]}) == "genre_Comedy+Action"

    def test_years_query_key(self):
        assert build_query_key(
            "years", {"start_year": 1990, "end_year": 2000}
        ) == "years_1990_2000"

    def test_genre_years_query_key_single_genre(self):
        assert build_query_key(
            "genre_years",
            {"genres": ["Action"], "start_year": 1990, "end_year": 2000},
        ) == "genre_years_Action_1990_2000"

    def test_genre_years_query_key_multiple_genres(self):
        assert build_query_key(
            "genre_years",
            {"genres": ["Action", "Comedy"], "start_year": 1990, "end_year": 2000},
        ) == "genre_years_Action+Comedy_1990_2000"

    def test_missing_required_key_returns_unknown_query(self, capsys):
        result = build_query_key("keyword", {})
        assert result == "unknown_query"

    def test_missing_required_key_prints_diagnostic(self, capsys):
        build_query_key("years", {"start_year": 1990})  # missing end_year
        captured = capsys.readouterr()
        assert "UNKNOWN_QUERY" in captured.out

    def test_unrecognized_search_type_returns_none(self):
        # Falls through all the if-branches without matching or raising.
        assert build_query_key("not_a_real_type", {}) is None
