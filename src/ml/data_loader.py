import pandas as pd
import re
import os

def load_data(sql_path=None):
    """
    Parses the jan_aushadhi_medicines.sql file to extract medicine data.
    
    Args:
        sql_path (str): Path to the .sql file. If None, tries to locate it relative to this file.
        
    Returns:
        pd.DataFrame: DataFrame with columns ['medicine_id', 'medicine_name', 'unit_size', 'mrp', 'group_name', 'category']
    """
    if sql_path is None:
        # Default path relative to src/ml/data_loader.py -> ../../database/jan_aushadhi_medicines.sql
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sql_path = os.path.join(base_dir, 'database', 'jan_aushadhi_medicines.sql')

    if not os.path.exists(sql_path):
        raise FileNotFoundError(f"Database file not found at: {sql_path}")

    print(f"Loading data from {sql_path}...")
    
    data = []
    # Regex to capture VALUES (...). 
    # This is a basic parser and assumes a specific format from the mysqldump.
    # Pattern looks for: INSERT ... VALUES (id, 'name', 'unit', price, 'group', 'category');
    # We use a non-greedy match for strings to handle most cases. 
    # Note: parsing complex SQL with regex is fragile, but sufficient for this specific dump file.
    pattern = re.compile(r"VALUES\s*\((\d+),\s*'((?:[^']|'')*)',\s*'((?:[^']|'')*)',\s*([\d\.]+),\s*'((?:[^']|'')*)',\s*'((?:[^']|'')*)'\)")

    with open(sql_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith("INSERT IGNORE INTO"):
                match = pattern.search(line)
                if match:
                    # Extract groups and unescape SQL single quotes ('' -> ')
                    med_id = int(match.group(1))
                    name = match.group(2).replace("''", "'")
                    unit = match.group(3).replace("''", "'")
                    mrp = float(match.group(4))
                    group = match.group(5).replace("''", "'")
                    category = match.group(6).replace("''", "'")
                    
                    data.append({
                        'medicine_id': med_id,
                        'medicine_name': name,
                        'unit_size': unit,
                        'mrp': mrp,
                        'group_name': group,
                        'category': category
                    })
    
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} medicines.")
    return df

if __name__ == "__main__":
    try:
        df = load_data()
        print("Sample Data:")
        print(df.head())
        print(df.tail())
    except Exception as e:
        print(f"Error: {e}")
