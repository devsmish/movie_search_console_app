from app.utils.console_colors import red


class TestRed:
    def test_wraps_text_in_ansi_red_and_reset_codes(self):
        assert red("oops") == "\033[31moops\033[0m"

    def test_empty_string_still_gets_wrapped(self):
        assert red("") == "\033[31m\033[0m"

    def test_does_not_mutate_or_translate_the_text(self):
        text = "Ошибка: файл не найден"
        assert red(text) == f"\033[31m{text}\033[0m"

    def test_multiline_text_is_wrapped_as_a_whole(self):
        text = "line one\nline two"
        assert red(text) == f"\033[31m{text}\033[0m"
