import json

import pytest

from app.i18n.translator import (
    SUPPORTED_LANGUAGES,
    _LOCALES_DIR,
    banner,
    get_language,
    set_language,
    t,
)


class TestSetLanguageAndGetLanguage:
    def test_default_language_is_english(self):
        # conftest's _reset_language autouse fixture already sets this,
        # but assert it explicitly as documentation of the default.
        set_language("en")
        assert get_language() == "en"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
    def test_all_supported_languages_can_be_set(self, lang):
        set_language(lang)
        assert get_language() == lang

    def test_unsupported_language_falls_back_to_english(self):
        set_language("fr")  # not in SUPPORTED_LANGUAGES
        assert get_language() == "en"


class TestTranslate:
    def test_resolves_simple_key(self):
        set_language("en")
        assert t("menu.main.header") == "MAIN MENU"

    def test_resolves_nested_key_in_another_language(self):
        set_language("ru")
        assert t("menu.main.header") == "ГЛАВНОЕ МЕНЮ"

    def test_same_key_differs_across_languages(self):
        set_language("de")
        de_text = t("menu.main.header")
        set_language("uk")
        uk_text = t("menu.main.header")
        assert de_text != uk_text

    def test_formats_placeholders(self):
        set_language("en")
        assert t("pagination.results_found", total=42) == "Results found: 42"

    def test_missing_key_returns_bracketed_placeholder(self):
        set_language("en")
        assert t("this.key.does.not.exist") == "[[this.key.does.not.exist]]"

    def test_missing_placeholder_kwarg_does_not_crash(self):
        # t() should degrade gracefully (return the unformatted template)
        # rather than raise, since a UI string should never crash the app.
        set_language("en")
        result = t("pagination.results_found")  # missing `total=`
        assert isinstance(result, str)

    def test_wrong_placeholder_kwarg_returns_unformatted_template(self):
        # Passing *some* kwargs, but not the one the template actually
        # needs, hits format()'s KeyError path rather than the "no kwargs
        # at all" shortcut — t() should still degrade gracefully.
        set_language("en")
        result = t("pagination.results_found", wrong_key="x")
        assert result == "Results found: {total}"

    def test_lazily_loads_a_language_not_yet_cached(self):
        # Directly simulates the internal cache not containing the active
        # language yet (e.g. if _current_lang were set some other way),
        # exercising t()'s lazy-load-on-demand branch.
        import app.i18n.translator as translator_module

        set_language("de")
        translator_module._translations.pop("de", None)
        result = t("menu.main.header")
        assert result == "HAUPTMENÜ"

    def test_key_present_in_active_language_is_not_taken_from_fallback(self):
        set_language("ru")
        assert t("errors.invalid_choice") == "Некорректный выбор. Попробуйте снова."


class TestBanner:
    def test_banner_contains_translated_text(self):
        set_language("en")
        result = banner("menu.main.header")
        assert "MAIN MENU" in result

    def test_banner_is_padded_to_requested_width(self):
        set_language("en")
        result = banner("menu.main.header", width=50)
        assert len(result) == 50

    def test_banner_uses_equals_signs_as_padding(self):
        set_language("en")
        result = banner("menu.main.header", width=40)
        assert result.startswith("=")
        assert result.endswith("=")

    def test_banner_adapts_to_longer_translated_text(self):
        # A longer header (e.g. German) should still produce a banner
        # of the exact requested width, not overflow it.
        set_language("de")
        result = banner("flows.genre.header", width=90)
        assert len(result) == 90


class TestLocaleFilesConsistency:
    """
    Guards against future edits to locales/*.json silently dropping or
    mistyping a key in one language but not the others.
    """

    def _flatten(self, d, prefix=""):
        keys = set()
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys |= self._flatten(v, full)
            else:
                keys.add(full)
        return keys

    @pytest.fixture
    def locale_keysets(self):
        keysets = {}
        for lang in SUPPORTED_LANGUAGES:
            with open(_LOCALES_DIR / f"{lang}.json", encoding="utf-8") as f:
                keysets[lang] = self._flatten(json.load(f))
        return keysets

    def test_all_locale_files_have_identical_key_sets(self, locale_keysets):
        base_lang, base_keys = next(iter(locale_keysets.items()))
        for lang, keys in locale_keysets.items():
            missing = base_keys - keys
            extra = keys - base_keys
            assert not missing, f"{lang}.json is missing keys present in {base_lang}.json: {missing}"
            assert not extra, f"{lang}.json has keys not present in {base_lang}.json: {extra}"

    def test_locale_files_are_non_empty(self, locale_keysets):
        for lang, keys in locale_keysets.items():
            assert len(keys) > 0, f"{lang}.json contains no translation keys"
