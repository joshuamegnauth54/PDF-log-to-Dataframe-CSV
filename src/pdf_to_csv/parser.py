import datetime
import logging
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

from pdfminer.high_level import extract_text

@dataclass
class Record:
    par_id: str
    tax_year: int
    jur: int
    procedure: str
    error: str

class AALog:
    date: datetime.date | None
    title: str
    records: list[Record]

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

def parse_row(raw: list[str]) -> tuple[Row, list[str]]:
    pass

"""Parse a PDF log into a CSV."""
def log_parser(path: Path):
    records: list[str] = extract_text(path).splitlines()

    # Process records by splitting on '|'
    parids: list[str] = []
    taxyrs: list[str] = []
    jurs: list[str] = []
    procedures: list[str] = []
    errmsgs: list[str] = []

    # Process each record after skipping the title row
    for record in records[1:]:
        # Skip "-----", dates, and empty rows
        if "-----" in record or any(char.isdigit() for char in record) or not record.strip():
            print(f"Skipping record: {record}")
            continue

        # Concatenate lines until a complete record is obtained
        while '|' not in record:
            record += next(records[1:], '')

        # Split the record into fields delimited with '|'
        fields: list[str] = record.split('|')

        # Check if the number of fields is correct (assuming at least 5 fields)
        if len(fields) >= 5:
            # Extract and process the fields
            parids.append(fields[0].strip())
            taxyrs.append(fields[1].strip())
            jurs.append(fields[2].strip())
            procedures.append(fields[3].strip())
            errmsgs.append(fields[4].strip())
        else:
            # Handle cases where the record does not match the expected structure
            print(f"Skipping record (incorrect structure): {record}")

        # TODO: Save to CSV

    print(f"parids: {parids}")
    print(f"taxyrs: {taxyrs}")
    print(f"jurs: {jurs}")
    print(f"procedures: {procedures}")
    print(f"errgmsg: {errmsgs}")

