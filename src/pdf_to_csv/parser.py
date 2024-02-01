from pathlib import Path

from pdfminer.high_level import extract_text

"""Parse a PDF log into a CSV."""
def parse(path: Path):
    text: str = extract_text(path)
    records: list[str] = text.split("\n\n")

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

