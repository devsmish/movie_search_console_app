"""
Shared output formatting for list[dict] data (search results, and
usable for any other tabular data in the app).

One place turns rows into a console table, CSV text, or JSON text, so
callers like `app/utils/pagination.py` and the results-export feature
share the exact same column definitions and truncation/escaping rules
instead of each hand-rolling its own f-string widths — which is what
previously let a long film title silently misalign the whole console
table (fixed here: values are truncated to each column's max_width
rather than left to overflow).
"""
import csv
import io
import json
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Column:
    """
    Describes one column shared across all three output formats.

    Args:
        key (str): The dict key this column reads from each row.
        header (str): Display header. Callers pass an already-translated
            string (via `t(...)`) so this module stays locale-agnostic.
        max_width (int, optional): Maximum characters shown in a console
            table before the value is truncated with an ellipsis.
            Ignored by to_csv()/to_json(), which always use the full
            value. Defaults to 30.
        align (str, optional): "left" or "right" alignment in a console
            table. Defaults to "left".
    """
    key: str
    header: str
    max_width: int = 30
    align: str = "left"


def _cell_text(row: dict, column: Column) -> str:
    """Reads a column's value out of a row as display text, defaulting
    missing/None values to an empty string rather than "None"."""
    value = row.get(column.key)
    return "" if value is None else str(value)


def _truncate(text: str, width: int) -> str:
    """
    Shortens `text` to at most `width` characters, replacing the last
    character with an ellipsis ('…') when it was cut, so a truncated
    value is visibly distinguishable from one that just happens to fill
    the column exactly.
    """
    if width <= 0 or len(text) <= width:
        return text
    if width == 1:
        return text[:1]
    return text[: width - 1] + "…"


def format_table(
    rows: list[dict],
    columns: list[Column],
    *,
    numbered: bool = True,
    num_header: str = "#",
) -> str:
    """
    Renders rows as a fixed-width plain-text console table: a header
    line, a separator line, then one line per row. Every column is
    truncated to its own `max_width`, so unlike naive f-string
    formatting, an unexpectedly long value can never push the table out
    of alignment — it's cut short with an ellipsis instead.

    Args:
        rows (list[dict]): Rows to render. Missing keys render as "".
        columns (list[Column]): Column definitions, in display order.
        numbered (bool, optional): If True, prepends a 1-based row-number
            column. Defaults to True.
        num_header (str, optional): Header text for that row-number
            column (already translated by the caller). Defaults to "#".

    Returns:
        str: Multi-line table text with no trailing newline, or an
        empty string if `rows` is empty (callers should print their own
        "nothing found" message in that case instead).
    """
    if not rows:
        return ""

    num_width = max(len(num_header), len(str(len(rows)))) if numbered else 0

    header_cells = []
    if numbered:
        header_cells.append(num_header.ljust(num_width))
    for col in columns:
        header_cells.append(_truncate(col.header, col.max_width).ljust(col.max_width))
    header_line = " | ".join(header_cells)

    lines = [header_line, "-" * len(header_line)]

    for i, row in enumerate(rows, start=1):
        cells = []
        if numbered:
            cells.append(str(i).ljust(num_width))
        for col in columns:
            text = _truncate(_cell_text(row, col), col.max_width)
            cells.append(text.rjust(col.max_width) if col.align == "right" else text.ljust(col.max_width))
        lines.append(" | ".join(cells))

    return "\n".join(lines)


def to_csv(rows: list[dict], columns: list[Column]) -> str:
    """
    Renders rows as CSV text (comma-separated, with a header row).

    Unlike format_table(), values are never truncated — CSV is meant for
    a spreadsheet or another program to consume, not to fit a terminal
    width. Standard CSV quoting (via the stdlib csv module) handles
    values containing commas, quotes, or newlines.

    Args:
        rows (list[dict]): Rows to render. Missing keys render as "".
        columns (list[Column]): Column definitions; `header` becomes the
            CSV header cell, `key` selects the value from each row.
            `max_width`/`align` are ignored here.

    Returns:
        str: CSV text (header + one line per row), using "\\r\\n" line
        endings as produced by the stdlib `csv` module.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([col.header for col in columns])
    for row in rows:
        writer.writerow([row.get(col.key, "") for col in columns])
    return buffer.getvalue()


def to_json(rows: list[dict], columns: list[Column] | None = None, *, indent: int = 2) -> str:
    """
    Renders rows as JSON text.

    Args:
        rows (list[dict]): Rows to render.
        columns (list[Column] | None, optional): If given, each output
            object only contains these columns, re-keyed from `key` to
            `header` (so the exported JSON uses the same human-readable
            field names as the console table/CSV). If omitted, every key
            in each row dict is included as-is, unchanged.
        indent (int, optional): JSON indentation level. Defaults to 2.

    Returns:
        str: Pretty-printed JSON text. Non-ASCII characters are kept
        as-is (not \\uXXXX-escaped). Values that aren't natively
        JSON-serializable (e.g. datetime) are rendered via str().
    """
    if columns:
        data = [{col.header: row.get(col.key) for col in columns} for row in rows]
    else:
        data = rows
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def default_export_filename(prefix: str, extension: str, now: datetime | None = None) -> str:
    """
    Builds a timestamped export filename, e.g. "search_results_20260822_153000.csv".

    Args:
        prefix (str): Filename prefix (e.g. "search_results").
        extension (str): File extension without a leading dot (e.g. "csv").
        now (datetime, optional): Timestamp to use. Defaults to
            datetime.now() — exposed as a parameter purely so callers/tests
            can pass a fixed value for deterministic output.

    Returns:
        str: The generated filename (no directory component).
    """
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def write_export_file(text: str, filepath: str) -> str:
    """
    Writes already-rendered text (from to_csv()/to_json()) to disk as
    UTF-8, creating any missing parent directories first.

    Args:
        text (str): File content to write.
        filepath (str): Destination path.

    Returns:
        str: The same `filepath`, for convenient chaining/printing.

    Raises:
        OSError: If the directory can't be created or the file can't be
            written (e.g. permissions). Left uncaught so callers can
            decide how to report it (matches how the rest of the app's
            search/log I/O surfaces errors).
    """
    parent = os.path.dirname(filepath)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return filepath
