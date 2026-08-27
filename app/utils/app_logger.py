"""
Rotating file logger for the app's own operational errors (search
failures, log-write failures, display/formatting failures, etc.).

This complements — it does not replace — the immediate, localized
console messages the user already sees for these same failures. The
console message is what a person watching the terminal needs right now;
this file is a persistent, greppable record (with a full traceback) that
survives past the current session, for after-the-fact debugging.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = "app.log"
MAX_BYTES = 1_000_000  # ~1 MB per log file before rotating
BACKUP_COUNT = 3       # keep app.log + 3 rotated backups (app.log.1, .2, .3)


def get_logger(
    name: str,
    log_dir: str | None = None,
    max_bytes: int | None = None,
    backup_count: int | None = None,
) -> logging.Logger:
    """
    Returns a logger configured with a rotating file handler.

    Idempotent: calling this more than once for the same `name` (e.g.
    from multiple modules that import each other, or repeated calls in
    the same process) never attaches a second handler — `logging`
    caches loggers by name, so the existing one is returned as-is.

    Args:
        name (str): Logger name, conventionally the caller's `__name__`.
        log_dir (str, optional): Directory to write the log file into.
            Defaults to LOG_DIR ("logs"). Only takes effect the first
            time this logger name is configured — see reset_logger()
            for tests that need to reconfigure an already-set-up logger.
        max_bytes (int, optional): Rotate once the file reaches this
            size. Defaults to MAX_BYTES.
        backup_count (int, optional): Number of rotated backups to keep.
            Defaults to BACKUP_COUNT.

    Returns:
        logging.Logger: A logger with a RotatingFileHandler attached,
        set to WARNING level (so routine info isn't logged, only actual
        problems), with propagation to the root logger disabled so
        nothing leaks onto the console via this path.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    target_dir = log_dir or LOG_DIR
    os.makedirs(target_dir, exist_ok=True)

    handler = RotatingFileHandler(
        os.path.join(target_dir, LOG_FILE),
        maxBytes=max_bytes if max_bytes is not None else MAX_BYTES,
        backupCount=backup_count if backup_count is not None else BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    logger.propagate = False
    return logger


def reset_logger(name: str) -> None:
    """
    Removes and closes every handler attached to the named logger, so a
    later get_logger() call for the same name reconfigures it from
    scratch (e.g. pointed at a different log_dir).

    Intended for tests. Production code has no reason to call this —
    each logger is meant to be configured once per process.

    Args:
        name (str): Logger name previously passed to get_logger().

    Returns:
        None
    """
    logger = logging.getLogger(name)
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
