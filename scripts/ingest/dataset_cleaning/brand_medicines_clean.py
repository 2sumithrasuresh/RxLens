import csv
import re
import os
from pathlib import Path

# ---------------------------------------------------
# PATH SETUP
# ---------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[3]

input_file = ROOT_DIR / "data/raw/test_brand_med_input.csv"

drugs_file = ROOT_DIR / "data/refined/drugs.csv"
brand_file = ROOT_DIR / "data/refined/brand_medicines.csv"
composition_file = ROOT_DIR / "data/refined/brand_medicine_composition.csv"

drugs_file.parent.mkdir(parents=True, exist_ok=True)


drug_map = {}
drug_counter = 1

medicine_counter = 1
composition_counter = 1

brand_rows = []
composition_rows = []
new_drugs = []


# ---------------------------------------------------
# LOAD EXISTING DRUGS IF FILE EXISTS
# ---------------------------------------------------

if os.path.exists(drugs_file):

    with open(drugs_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            drug_id = int(row[0])
            drug_name = row[1]

            drug_map[drug_name] = drug_id
            drug_counter = max(drug_counter, drug_id + 1)


# ---------------------------------------------------
# SALT PARSER
# ---------------------------------------------------

def parse_salt_composition(salt_string):

    results = []

    parts = salt_string.split("+")
    for part in parts:
        part = part.strip()

        match = re.match(r"([A-Za-z\s]+)\((.*?)\)", part)

        if match:
            drug = match.group(1).strip()
            value = match.group(2).strip()

            amount = None
            unit = None

            match_amount = re.match(r'(\d+)([a-zA-Z]+)(?:/(\d+)([a-zA-Z]+))?', value)

            if match_amount:

                num1 = match_amount.group(1)
                unit1 = match_amount.group(2)

                num2 = match_amount.group(3)
                unit2 = match_amount.group(4)

                if num2:
                    amount = f"{num1}/{num2}"
                    unit = f"{unit1}/{unit2}"
                else:
                    amount = num1
                    unit = unit1

            results.append((drug, amount, unit))

    return results


# ---------------------------------------------------
# READ MAIN DATASET
# ---------------------------------------------------

with open(input_file, newline='', encoding='utf-8') as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:

        medicine_id = medicine_counter
        medicine_counter += 1

        brand_rows.append([
            medicine_id,
            row["name"],
            row["manufacturer_name"],
            row["pack_size_label"],
            row["price"]
        ])

        compositions = parse_salt_composition(row["salt_composition"])

        for drug, amount, unit in compositions:

            if drug not in drug_map:
                drug_map[drug] = drug_counter
                new_drugs.append((drug_counter, drug))
                drug_counter += 1

            drug_id = drug_map[drug]

            composition_rows.append([
                composition_counter,
                medicine_id,
                drug_id,
                amount,
                unit
            ])

            composition_counter += 1


# ---------------------------------------------------
# WRITE / APPEND drugs.csv
# ---------------------------------------------------

mode = "a" if os.path.exists(drugs_file) else "w"

with open(drugs_file, mode, newline='', encoding='utf-8') as f:

    writer = csv.writer(f)

    if mode == "w":
        writer.writerow(["drug_id", "drug_name"])

    for drug_id, drug_name in new_drugs:
        writer.writerow([drug_id, drug_name])


# ---------------------------------------------------
# WRITE brand_medicines.csv
# ---------------------------------------------------

with open(brand_file, "w", newline='', encoding='utf-8') as f:

    writer = csv.writer(f)

    writer.writerow([
        "medicine_id",
        "medicine_name",
        "manufacturer_name",
        "pack_size",
        "price"
    ])

    writer.writerows(brand_rows)


# ---------------------------------------------------
# WRITE brand_medicine_composition.csv
# ---------------------------------------------------

with open(composition_file, "w", newline='', encoding='utf-8') as f:

    writer = csv.writer(f)

    writer.writerow([
        "id",
       "medicine_id",
        "drug_id",
        "amount",
        "unit"
    ])

    writer.writerows(composition_rows)


print("CSV files generated successfully.") 
