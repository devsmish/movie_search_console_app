from app.i18n.language_select import choose_language


class TestChooseLanguage:
    def test_option_1_selects_english(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "1")
        assert choose_language() == "en"

    def test_option_2_selects_german(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "2")
        assert choose_language() == "de"

    def test_option_3_selects_ukrainian(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "3")
        assert choose_language() == "uk"

    def test_option_4_selects_russian(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "4")
        assert choose_language() == "ru"

    def test_invalid_choice_is_rejected_then_retried(self, monkeypatch, capsys):
        responses = iter(["9", "1"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
        assert choose_language() == "en"
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out

    def test_keyboard_interrupt_returns_none(self, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_interrupt)
        assert choose_language() is None
