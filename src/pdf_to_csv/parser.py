import datetime
import logging
from typing import Self
import regex as re
from dataclasses import dataclass
from pathlib import Path

from pdfminer.high_level import extract_text

DASH_MATCHER: re.Pattern = re.compile("^-+$")


@dataclass
class Record:
    par_id: str
    tax_year: int | None
    jur: int | None
    procedure: str
    error: str


@dataclass
class AALog:
    date: datetime.date | None
    title: str
    records: list[Record]

    def to_csv(self: Self):
        raise NotImplementedError()


@dataclass
class Header:
    date: datetime.date | None
    title: str


def parse_header(raw: list[str]) -> tuple[Header, list[str]]:
    if not len(raw):
        raise RuntimeError("Empty raw logs")

    header: list[str] = raw[0].split()

    # Title case because the month is all caps in the log
    date_parts: str = header[0].title()
    date: None | datetime.date = None
    try:
        date = datetime.datetime.strptime(date_parts, "%d-%b-%Y").date()
    except Exception as e:
        logging.warn(f"Couldn't parse date: {e}")

    title: str = ""
    for piece in header:
        if piece[0] and piece[0].isalpha() and not piece.startswith("PAGE"):
            title += piece

    parsed: Header = Header(date, title)
    return (parsed, raw[1:])


def parse_row(raw: list[str]) -> tuple[Record | None, list[str]]:
    for i, line in enumerate(raw):
        line = line.strip()

        # Skip empty
        if not line:
            continue

        # Split by pipe for columns, strip whitespace,
        # and skip columns that are all dashes
        columns: list[str] = [
            s.strip() for s in line.split("|") if not DASH_MATCHER.match(s)
        ]
        if len(columns) != 5 and not any(columns):
            continue

        # Skip header
        col_titles: list[str] = ["parid", "taxyr", "jur", "procedure", "errmsg"]
        for col, title in zip(columns, col_titles):
            col = col.strip().lower()
            if col != title:
                break

        # Skip butchered column with page number
        # if

        tax_year: int | None = None
        jur: int | None = None

        try:
            tax_year = int(columns[1])
            jur = int(columns[2])
        except ValueError:
            pass

        return (Record(columns[0], tax_year, jur, columns[3], columns[4]), raw[i + 1 :])

    # Raw is exhausted therefore there are no more valid rows
    return (None, [])


"""Parse a PDF log into a CSV."""


def log_parser(path: Path) -> AALog:
    raw: list[str] = extract_text(path).split("|")

    header: Header
    (header, raw) = parse_header(raw)

    # Try to parse each row
    rows: list[Record] = []
    while raw:
        row: Record | None = None
        (row, new_raw) = parse_row(raw)
        raw = new_raw

        if row:
            rows.append(row)

    if raw:
        logging.warning("Extra data found after parsing completed")
        logging.debug(f"Extra data: {raw}")

    if not rows:
        logging.warning("Parser deserialized zero rows")

    return AALog(header.date, header.title, rows)
