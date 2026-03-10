import pandas as pd
import re
import os

def load_data():
    """
    Loads all relevant medicine data from CSVs and the seed SQL file.
    
    Returns:
        tuple: (generic_medicines_df, generic_compositions_df, branded_medicines_df, branded_compositions_df, drugs_df)
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    refined_dir = os.path.join(base_dir, 'data', 'refined')
    db_dir = os.path.join(base_dir, 'database')
    
    # 1. Load CSVs
    drugs_df = pd.read_csv(os.path.join(refined_dir, 'drugs.csv'))
    gen_meds_df = pd.read_csv(os.path.join(refined_dir, 'jan_aushadhi_medicines.csv'))
    gen_comp_df = pd.read_csv(os.path.join(refined_dir, 'jan_aushadhi_composition.csv'))
    
    # 2. Parse seed_db.sql for branded medicines
    seed_sql_path = os.path.join(db_dir, 'seed_db.sql')
    branded_meds = []
    brand_comps = []
    
    with open(seed_sql_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Parse brand_medicines
    # INSERT INTO brand_medicines (brand_name, medicine_name) VALUES ('Crocin', 'Crocin Advance'), ...;
    brand_meds_match = re.search(r"INSERT INTO brand_medicines[^\(]*\([^\)]*\)\s*VALUES\s*(.*?);", content, re.DOTALL | re.IGNORECASE)
    if brand_meds_match:
        values_str = brand_meds_match.group(1)
        # Parse individual tuples
        tuples = re.findall(r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", values_str)
        for i, (brand_name, med_name) in enumerate(tuples):
            branded_meds.append({
                'medicine_id': i + 1,
                'brand_name': brand_name,
                'medicine_name': med_name
            })
            
    branded_meds_df = pd.DataFrame(branded_meds)
    
    # Parse brand_medicine_composition
    # INSERT INTO brand_medicine_composition VALUES (NULL, 1, 1, 500);
    brand_comp_matches = re.findall(r"INSERT INTO brand_medicine_composition VALUES\s*\(([^;]+)\);", content, re.IGNORECASE)
    for match in brand_comp_matches:
        # Match could contain multiple tuples like `NULL, 3, 3, 500), (NULL, 3, 4, 125`
        tuples = re.findall(r"(?:NULL|\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d\.]+)", match)
        for med_id, drug_id, amount in tuples:
            brand_comps.append({
                'medicine_id': int(med_id),
                'drug_id': int(drug_id),
                'amount': float(amount),
                'unit': 'mg' # Simplified unit for parsed SQL
            })
            
    branded_comps_df = pd.DataFrame(brand_comps)
    
    return gen_meds_df, gen_comp_df, branded_meds_df, branded_comps_df, drugs_df

def get_composition_strings(compositions_df, drugs_df):
    """
    Joins compositions with drugs and creates a string representation of ingredients.
    """
    merged = pd.merge(compositions_df, drugs_df, on='drug_id', how='left')
    merged['ingredient_str'] = merged['drug_name'].astype(str) + " " + merged['amount'].astype(str) + merged['unit'].astype(str)
    
    # Group by medicine_id
    grouped = merged.groupby('medicine_id')['ingredient_str'].apply(lambda x: ' + '.join(x)).reset_index()
    grouped.rename(columns={'ingredient_str': 'composition'}, inplace=True)
    return grouped

def build_searchable_dataset():
    """
    Builds the final datasets needed for the ML model.
    """
    gen_meds_df, gen_comp_df, branded_meds_df, branded_comps_df, drugs_df = load_data()
    
    # Get composition strings
    gen_comp_str = get_composition_strings(gen_comp_df, drugs_df)
    brand_comp_str = get_composition_strings(branded_comps_df, drugs_df)
    
    # Merge back to medicines
    generic_df = pd.merge(gen_meds_df, gen_comp_str, on='medicine_id', how='left')
    branded_df = pd.merge(branded_meds_df, brand_comp_str, on='medicine_id', how='left')
    
    # Fill NA compositions
    generic_df['composition'] = generic_df['composition'].fillna('')
    branded_df['composition'] = branded_df['composition'].fillna('')
    
    generic_df['search_text'] = generic_df['composition'] + " " + generic_df['medicine_name']
    
    return generic_df, branded_df

if __name__ == "__main__":
    try:
        generic_df, branded_df = build_searchable_dataset()
        print("Generic Meds Data:")
        print(generic_df[['medicine_name', 'composition']].head())
        print("\nBranded Meds Data:")
        print(branded_df.head())
    except Exception as e:
        print(f"Error: {e}")
