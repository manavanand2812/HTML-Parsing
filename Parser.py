import pandas as pd
from bs4 import BeautifulSoup
import re

def extract_table(file_path, table_name):
   
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    
    table = soup.find("table")
    if not table:
        return []
    
    rows = table.find_all("tr")
    extracted_data = []
    
    # First row is the table title, if it exists
    table_title = rows[1].get_text(strip=True) if rows else None
    rows = rows[1:]  # Remove title row
    if table_name == 'table_62':
        table_title = ""
   
    
    # Extract Column Headers 
    headers = [cell.get_text(strip=True) for cell in rows[1].find_all(["td", "th"])]
    headers = [i for i in headers if i != "" and i != "In millions"]
    
    # Special case for table_62
    if table_name == "table_62":
        headers.append("2027 and thereafter")

    
    
    # Process Data Rows
    for row in rows[2:]:
        cells = [cell for cell in row.find_all("td") if cell.get_text(strip=True) != "$"]
        row_data = [cell.get_text(separator=" ", strip=True) for cell in cells]
        
        label = row_data[0] if len(row_data) > 0 else ""
        rowtext = " ".join(row_data[1:])
        
        rt = re.findall("\s*\$?\(?\s*[0-9\,\.]+\s*%?\s*\)?\s*|\s*\(?\s*\—+\s*%?\s*\)?\s*", rowtext)
        rt = [i if re.fullmatch("\s*\(?\s*[0-9\,\.]+\s*%?\s*\)?\s*", i) else " - %" for i in rt]
        rt = [i.strip(" ()") for i in rt]
        
        if len(rt) == len(headers):
            for i in range(len(headers)):
                extracted_data.append([table_name, label, table_title, headers[i], rt[i]])
        else:
            continue
    
    return extracted_data

# File paths and table names
files = {
    "table_9.html": "table_9",
    "table_12.html": "table_12",
    "table_62.html": "table_62"
}

# Parse and merge all tables
data = []
for file_path, table_name in files.items():
    data.extend(extract_table(file_path, table_name))

# Convert to DataFrame and save as CSV
df = pd.DataFrame(data, columns=["filename", "label", "tabletitle", "column header", "value"])
df.to_csv("parsed_tables.csv", index=False)

print("Parsing completed. CSV file saved as 'parsed_tables.csv'.")
