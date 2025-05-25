import pandas as pd
from openpyxl import Workbook

# Your data string (truncated for brevity; replace ... with your actual data)
import campaignstring

data_string = campaignstring.globals

# Manually parsing the string to extract column names and row data
#headers = ["ID", "IDRestrictedTo", "Row", "Col", "Default", "Level", "PerkType", "Name", "Mods", "Description"]
rows = []
headers = []
skip = False
# Split the data string by lines and iterate through it
in_rows_section = False
in_cols_section = False
first_item_skip = False
current_row = []
for line in data_string.split('\n'):
    if '<Dictionary name="Cols"' in line:
      in_cols_section = True
    elif '<Simple value="' in line and in_cols_section: 
      value = line.split('"')[1]
      if skip == False:
        headers.append(value if value != 'Null' else None)
        skip = True
      else:
        skip = False
    elif '<Dictionary name="Rows"' in line:
      in_rows_section = True
      in_cols_section = False
    elif '<Item>' in line and in_rows_section:
      # Start of a new row
      first_item_skip = True
      if current_row:
          rows.append(current_row)
      current_row = []
    elif '</Item>' in line and in_rows_section:
      # End of a current row, append it if it's not empty
      if current_row:
          rows.append(current_row)
          print(current_row)
          current_row = []
    elif '<Simple value="' in line and in_rows_section:
      if not first_item_skip:
        # Extracting value from the line
        value = line.split('"')[1]
        current_row.append(value)
      else:
        first_item_skip = False
      
    elif "<Null />" in line and in_rows_section:
      current_row.append("")

print(headers)

# Make sure to capture the last row if any
if current_row:
    rows.append(current_row)

# Create a DataFrame
df = pd.DataFrame(rows, columns=headers)

# Write the DataFrame to an Excel file
excel_filename = "researchtree.xlsx"
df.to_excel(excel_filename, index=False, engine='openpyxl')

print(f"Data successfully written to {excel_filename}")
