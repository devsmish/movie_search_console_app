from unittest.mock import patch

import app.main
from app.main import main


class TestMainWiring:
    def test_language_is_applied_and_menu_started_on_valid_choice(self):
        with patch.object(app.main, "choose_language", return_value="de") as choose, \
             patch.object(app.main, "set_language") as set_lang, \
             patch.object(app.main, "main_menu") as menu:
            main()
        choose.assert_called_once()
        set_lang.assert_called_once_with("de")
        menu.assert_called_once()

    def test_cancelling_language_choice_skips_the_menu(self):
        with patch.object(app.main, "choose_language", return_value=None), \
             patch.object(app.main, "set_language") as set_lang, \
             patch.object(app.main, "main_menu") as menu:
            main()
        set_lang.assert_not_called()
        menu.assert_not_called()


class TestForceUtf8Console:
    def test_does_not_raise_when_stream_lacks_reconfigure(self):
        class StreamWithoutReconfigure:
            pass

        with patch.object(app.main.sys, "stdout", StreamWithoutReconfigure()), \
             patch.object(app.main.sys, "stderr", StreamWithoutReconfigure()):
            app.main._force_utf8_console()  # must not raise
