import pandas as pd 
import re
from pdfminer.high_level import extract_text

# Import PDF
text = extract_text('C:\\Users\\fatogunt\\Downloads\\AA731NYC_ASMT.pdf')

# Split text into records
error_records = text.split('\n\n')  

# Process records by splitting based on the pipe ('|') character
parids = []
taxyrs = []  
jurs = []
procedures = []
errmsgs = []

# Process each record
record_lines = []
for record in error_records[1:]:  # Skip the first line (column titles)
    # Check if the line contains '-----', a date, or is empty; if yes, skip
    if '-----' in record or any(char.isdigit() for char in record) or not record.strip():
        print(f"Skipping record: {record}")
        continue
    
    # Concatenate lines until a complete record is obtained
    while '|' not in record:
        record += next(error_records[1:], '')  # Concatenate with the next line

    # Split the record into fields based on the pipe ('|') character
    fields = record.split('|')

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

# Create the DataFrame  
df = pd.DataFrame({
    'PARID': parids, 
    'TAXYR': taxyrs,
    'JUR': jurs,
    'PROCEDURE': procedures,  
    'ERRMSG': errmsgs
})

# Print the first few rows of the DataFrame, excluding records with incorrect structure
print(df[df['PARID'] != 'PARID'].head())

# Save DataFrame to CSV
df.to_csv('error_log.csv', index=False)
