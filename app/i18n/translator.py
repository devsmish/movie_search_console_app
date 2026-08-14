import json
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"

SUPPORTED_LANGUAGES = ("en", "de", "ru", "uk")
_FALLBACK_LANGUAGE = "en"

_current_lang = _FALLBACK_LANGUAGE
_translations: dict[str, dict] = {}


def _load_locale(lang: str) -> dict:
    """
    Loads a single locale JSON file from disk.

    Args:
        lang (str): Language code (must be one of SUPPORTED_LANGUAGES).

    Returns:
        dict: Parsed translation dictionary for the given language.

    Raises:
        FileNotFoundError: If the locale file does not exist.
        json.JSONDecodeError: If the locale file contains invalid JSON.
    """
    path = _LOCALES_DIR / f"{lang}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def set_language(lang: str) -> None:
    """
    Sets the active application language.

    Loads (and caches) the requested locale file. Falls back to
    _FALLBACK_LANGUAGE if the requested language is not supported.
    The fallback locale is always loaded as well, so t() can gracefully
    fall back to it for any missing key.

    Args:
        lang (str): Language code, e.g. "en", "de", "ru", "uk".

    Returns:
        None
    """
    global _current_lang

    if lang not in SUPPORTED_LANGUAGES:
        lang = _FALLBACK_LANGUAGE

    if _FALLBACK_LANGUAGE not in _translations:
        _translations[_FALLBACK_LANGUAGE] = _load_locale(_FALLBACK_LANGUAGE)

    if lang not in _translations:
        _translations[lang] = _load_locale(lang)

    _current_lang = lang


def get_language() -> str:
    """
    Returns the currently active language code.
    """
    return _current_lang


def _lookup(d: dict, dotted_key: str) -> str | None:
    """
    Resolves a dot-separated key path inside a nested dict.

    Args:
        d (dict): The (nested) translation dictionary to search.
        dotted_key (str): Dot-separated path, e.g. "menu.main.header".

    Returns:
        str | None: The resolved string, or None if any part of the
        path is missing.
    """
    node = d
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def t(key: str, **kwargs) -> str:
    """
    Translates a dot-separated key into the currently active language.

    Falls back to the fallback language (English) if the key is missing
    in the active language, and returns a visibly-broken placeholder
    (e.g. "[[missing.key]]") if the key is missing everywhere, so that
    untranslated strings are easy to spot instead of crashing the app.

    Args:
        key (str): Dot-separated translation key, e.g. "menu.main.header".
        **kwargs: Values used to .format() placeholders in the string,
            e.g. t("pagination.results_found", total=42).

    Returns:
        str: The translated (and formatted) string.
    """
    if _current_lang not in _translations:
        set_language(_current_lang)

    text = _lookup(_translations[_current_lang], key)
    if text is None:
        text = _lookup(_translations.get(_FALLBACK_LANGUAGE, {}), key)
    if text is None:
        return f"[[{key}]]"

    try:
        return text.format(**kwargs) if kwargs else text
    except (KeyError, IndexError):
        return text


def banner(key: str, width: int = 90, **kwargs) -> str:
    """
    Builds a centered '=' banner line around a translated header string.

    Using a dynamically centered banner (rather than a hardcoded number of
    '=' characters) keeps the visual layout consistent regardless of how
    long the translated header text turns out to be in a given language.

    Args:
        key (str): Translation key for the header text.
        width (int, optional): Total width of the banner line. Defaults to 90.
        **kwargs: Passed through to t() for placeholder formatting.

    Returns:
        str: A single line like "===...=== HEADER TEXT ===...===".
    """
    text = f" {t(key, **kwargs)} "
    return text.center(width, "=")
