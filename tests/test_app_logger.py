import glob
import os

from app.utils.app_logger import get_logger, reset_logger


class TestGetLogger:
    def test_creates_the_log_directory_if_missing(self, tmp_path):
        log_dir = str(tmp_path / "nested" / "logs")
        try:
            get_logger("test.creates_dir", log_dir=log_dir)
            assert os.path.isdir(log_dir)
        finally:
            reset_logger("test.creates_dir")

    def test_creates_a_log_file_on_first_write(self, tmp_path):
        log_dir = str(tmp_path)
        try:
            logger = get_logger("test.creates_file", log_dir=log_dir)
            logger.error("something broke")
            assert os.path.exists(os.path.join(log_dir, "app.log"))
        finally:
            reset_logger("test.creates_file")

    def test_logged_message_appears_in_the_file(self, tmp_path):
        log_dir = str(tmp_path)
        try:
            logger = get_logger("test.message_content", log_dir=log_dir)
            logger.error("mongo connection reset")
            content = open(os.path.join(log_dir, "app.log"), encoding="utf-8").read()
            assert "mongo connection reset" in content
            assert "ERROR" in content
        finally:
            reset_logger("test.message_content")

    def test_repeated_calls_with_the_same_name_do_not_add_duplicate_handlers(self, tmp_path):
        log_dir = str(tmp_path)
        try:
            logger1 = get_logger("test.idempotent", log_dir=log_dir)
            logger2 = get_logger("test.idempotent", log_dir=log_dir)
            assert logger1 is logger2
            assert len(logger1.handlers) == 1
        finally:
            reset_logger("test.idempotent")

    def test_repeated_calls_do_not_duplicate_log_lines(self, tmp_path):
        log_dir = str(tmp_path)
        try:
            get_logger("test.no_dupe_lines", log_dir=log_dir)
            logger = get_logger("test.no_dupe_lines", log_dir=log_dir)
            logger.error("one problem")
            content = open(os.path.join(log_dir, "app.log"), encoding="utf-8").read()
            assert content.count("one problem") == 1
        finally:
            reset_logger("test.no_dupe_lines")

    def test_info_level_messages_are_not_written(self, tmp_path):
        # Only WARNING and above should reach the file — this is for
        # operational errors, not routine activity logging.
        log_dir = str(tmp_path)
        try:
            logger = get_logger("test.warning_level", log_dir=log_dir)
            logger.info("just fyi")
            logger.error("actual problem")
            content = open(os.path.join(log_dir, "app.log"), encoding="utf-8").read()
            assert "just fyi" not in content
            assert "actual problem" in content
        finally:
            reset_logger("test.warning_level")

    def test_does_not_propagate_to_root_logger(self, tmp_path, capsys):
        # Propagation must be off, so nothing from this logger leaks
        # onto the console via a default root StreamHandler.
        log_dir = str(tmp_path)
        try:
            logger = get_logger("test.no_propagate", log_dir=log_dir)
            logger.error("should stay in the file only")
            captured = capsys.readouterr()
            assert "should stay in the file only" not in captured.out
            assert "should stay in the file only" not in captured.err
        finally:
            reset_logger("test.no_propagate")

    def test_exc_info_includes_traceback(self, tmp_path):
        log_dir = str(tmp_path)
        try:
            logger = get_logger("test.traceback", log_dir=log_dir)
            try:
                raise ValueError("boom")
            except ValueError as e:
                logger.error("failed: %s", e, exc_info=True)
            content = open(os.path.join(log_dir, "app.log"), encoding="utf-8").read()
            assert "Traceback" in content
            assert "ValueError: boom" in content
        finally:
            reset_logger("test.traceback")


class TestRotation:
    def test_rotates_once_the_file_exceeds_max_bytes(self, tmp_path):
        log_dir = str(tmp_path)
        name = "test.rotation"
        try:
            logger = get_logger(name, log_dir=log_dir, max_bytes=200, backup_count=2)
            for i in range(50):
                logger.error("padding message number %s to grow the file", i)
            rotated = glob.glob(os.path.join(log_dir, "app.log.*"))
            assert len(rotated) > 0
        finally:
            reset_logger(name)

    def test_keeps_at_most_backup_count_rotated_files(self, tmp_path):
        log_dir = str(tmp_path)
        name = "test.rotation_limit"
        try:
            logger = get_logger(name, log_dir=log_dir, max_bytes=200, backup_count=2)
            for i in range(200):
                logger.error("padding message number %s to grow the file", i)
            rotated = glob.glob(os.path.join(log_dir, "app.log.*"))
            assert len(rotated) <= 2
        finally:
            reset_logger(name)


class TestResetLogger:
    def test_allows_reconfiguration_with_a_different_log_dir(self, tmp_path):
        first_dir = str(tmp_path / "first")
        second_dir = str(tmp_path / "second")
        name = "test.reconfigure"
        try:
            logger = get_logger(name, log_dir=first_dir)
            logger.error("goes to first dir")
            reset_logger(name)

            logger = get_logger(name, log_dir=second_dir)
            logger.error("goes to second dir")

            assert "goes to first dir" in open(os.path.join(first_dir, "app.log"), encoding="utf-8").read()
            assert "goes to second dir" in open(os.path.join(second_dir, "app.log"), encoding="utf-8").read()
        finally:
            reset_logger(name)

    def test_is_a_no_op_for_a_logger_that_was_never_configured(self):
        reset_logger("test.never_configured")  # must not raise
