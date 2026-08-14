from app.i18n.language_select import choose_language
from app.i18n.translator import set_language
from app.menu.main_menu import main_menu
import sys


def _force_utf8_console() -> None:
    """
    Forces UTF-8 output encoding on stdout/stderr where possible.

    Cyrillic (ru/uk) and German umlauts (ä/ö/ü/ß) can render as garbled
    text or raise UnicodeEncodeError on Windows terminals, which often
    default to a legacy codepage (e.g. cp1252/cp866) instead of UTF-8.
    This is a no-op on platforms where the stream is already UTF-8 or
    doesn't support reconfigure() (e.g. when output is redirected to
    certain non-standard stream types).
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main() -> None:
    """
    Entry point of the application.

    Prompts the user to choose a UI language (English, German, Russian
    or Ukrainian) before anything else happens, configures the translator
    accordingly, then calls main_menu() to start the interactive console menu.

    Args:
        None

    Returns:
        None: This function does not return any value; it starts the program flow.
    """
    _force_utf8_console()
    lang = choose_language()
    if lang is None:
        return
    set_language(lang)
    main_menu()

if __name__ == "__main__":
    main()
