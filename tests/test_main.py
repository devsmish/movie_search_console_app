from unittest.mock import MagicMock, patch

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

    def test_console_is_forced_to_utf8_before_anything_else(self):
        # _force_utf8_console() must run first, so a garbled/non-UTF-8
        # terminal never gets a chance to mangle the language prompt or
        # main menu that come right after it.
        calls = []
        with patch.object(app.main, "_force_utf8_console", side_effect=lambda: calls.append("utf8")), \
             patch.object(app.main, "choose_language", side_effect=lambda: calls.append("choose") or "en"), \
             patch.object(app.main, "set_language"), \
             patch.object(app.main, "main_menu"):
            main()
        assert calls == ["utf8", "choose"]

    def test_force_utf8_console_runs_even_when_language_choice_is_cancelled(self):
        with patch.object(app.main, "_force_utf8_console") as force_utf8, \
             patch.object(app.main, "choose_language", return_value=None), \
             patch.object(app.main, "main_menu"):
            main()
        force_utf8.assert_called_once()


class TestForceUtf8Console:
    def test_does_not_raise_when_stream_lacks_reconfigure(self):
        class StreamWithoutReconfigure:
            pass

        with patch.object(app.main.sys, "stdout", StreamWithoutReconfigure()), \
             patch.object(app.main.sys, "stderr", StreamWithoutReconfigure()):
            app.main._force_utf8_console()  # must not raise

    def test_does_not_raise_when_reconfigure_raises_value_error(self):
        # Some non-standard stream types (e.g. certain redirected/piped
        # streams) raise ValueError from reconfigure() rather than
        # lacking the method entirely — both must be swallowed.
        class StreamThatRejectsReconfigure:
            def reconfigure(self, **kwargs):
                raise ValueError("reconfigure not supported on this stream")

        with patch.object(app.main.sys, "stdout", StreamThatRejectsReconfigure()), \
             patch.object(app.main.sys, "stderr", StreamThatRejectsReconfigure()):
            app.main._force_utf8_console()  # must not raise

    def test_reconfigures_stdout_with_utf8_and_replace(self):
        fake_stdout = MagicMock()
        fake_stderr = MagicMock()
        with patch.object(app.main.sys, "stdout", fake_stdout), \
             patch.object(app.main.sys, "stderr", fake_stderr):
            app.main._force_utf8_console()
        fake_stdout.reconfigure.assert_called_once_with(encoding="utf-8", errors="replace")

    def test_reconfigures_stderr_with_utf8_and_replace(self):
        fake_stdout = MagicMock()
        fake_stderr = MagicMock()
        with patch.object(app.main.sys, "stdout", fake_stdout), \
             patch.object(app.main.sys, "stderr", fake_stderr):
            app.main._force_utf8_console()
        fake_stderr.reconfigure.assert_called_once_with(encoding="utf-8", errors="replace")

    def test_stderr_is_still_reconfigured_if_stdout_reconfigure_fails(self):
        # One stream failing must not short-circuit the other.
        fake_stdout = MagicMock()
        fake_stdout.reconfigure.side_effect = ValueError("nope")
        fake_stderr = MagicMock()
        with patch.object(app.main.sys, "stdout", fake_stdout), \
             patch.object(app.main.sys, "stderr", fake_stderr):
            app.main._force_utf8_console()  # must not raise
        fake_stderr.reconfigure.assert_called_once_with(encoding="utf-8", errors="replace")
