from app.utils.input_utils import safe_input

_LANGUAGE_OPTIONS = {
    "1": "en",
    "2": "de",
    "3": "uk",
    "4": "ru",
}

_PROMPT = """
Choose language / Wählen Sie die Sprache / Виберіть мову / Выберите язык:
1. English
2. Deutsch
3. Українська
4. Русский"""

_INVALID = "Invalid choice / Ungültige Auswahl / Невірний вибір / Неверный выбор. Try again / Versuchen Sie es \
erneut / Спробуйте ще раз / Попробуйте снова."

_INTERRUPTED = "Program closed / Programm geschlossen / Програму закрито / Программа закрыта."


def choose_language() -> str | None:
    """
    Prompts the user to pick one of the 4 supported UI languages.

    Shown once, at the very start of the application, before the
    translator has been configured — so every string here is written
    out in all supported languages simultaneously.

    Returns:
        str | None: A language code from SUPPORTED_LANGUAGES ("en", "de",
        "ru", "uk"), or None if the user interrupted the prompt
        (e.g. via Ctrl+C).
    """
    while True:
        print(_PROMPT)
        choice = safe_input("> ", interrupt_msg=_INTERRUPTED)
        if choice is None:
            return None
        if choice in _LANGUAGE_OPTIONS:
            return _LANGUAGE_OPTIONS[choice]
        print(_INVALID)
