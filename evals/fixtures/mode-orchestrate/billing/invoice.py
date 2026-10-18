"""Invoice line paging and totals for the statement PDF.

Pages are 1-based: the statement renderer asks for page 1 first and keeps
going until it gets an empty page back.
"""

from __future__ import annotations

LINES_PER_PAGE = 10


def line_total(line: dict) -> int:
    """Total for one line in cents: quantity * unit price minus discount."""
    gross = line["qty"] * line["unit_cents"]
    return gross - line.get("discount_cents", 0)


def statement_total(lines: list[dict]) -> int:
    """Sum of all line totals in cents, independent of paging."""
    return sum(line_total(line) for line in lines)


def page_lines(lines: list, page: int, per_page: int = LINES_PER_PAGE) -> list:
    """Return the lines that belong on 1-based page `page`.

    page 1 -> lines[0:per_page], page 2 -> lines[per_page:2*per_page], ...
    An empty list means there are no more pages.
    """
    if page < 1:
        raise ValueError("page numbers start at 1")
    start = page * per_page
    end = start + per_page
    return lines[start:end]


def page_count(lines: list, per_page: int = LINES_PER_PAGE) -> int:
    """Number of pages needed to show every line."""
    if not lines:
        return 0
    return (len(lines) + per_page - 1) // per_page
