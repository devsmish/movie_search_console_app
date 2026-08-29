"""
Minimal ANSI color helper for console output.

Centralizes the "print an error in red" pattern that was previously
duplicated ~26 times across app/flows, app/menu, and app/utils as
`f"\\033[31m{text}\\033[0m"`. One place to change the color (or how
errors are highlighted at all — e.g. adding a --no-color mode) instead
of hunting down every call site.
"""

_RED = "\033[31m"
_RESET = "\033[0m"


def red(text: str) -> str:
    """
    Wraps `text` in ANSI codes so it prints in red on a terminal that
    supports ANSI escape codes.

    Args:
        text (str): Text to colorize. Callers pass an already-translated
            string (via `t(...)`) where applicable — this function is
            purely a presentation wrapper and knows nothing about i18n.

    Returns:
        str: `text` wrapped in the red-foreground / reset ANSI codes,
        e.g. red("oops") == "\\033[31moops\\033[0m".
    """
    return f"{_RED}{text}{_RESET}"
