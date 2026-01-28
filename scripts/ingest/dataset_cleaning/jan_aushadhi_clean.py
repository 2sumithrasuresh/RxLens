import csv
import re
from pathlib import Path

# ==================================================
# Paths
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent()

RAW_CSV = BASE_DIR / "data/raw/jan_aushadhi.csv"
REFINED_DIR = BASE_DIR / "data/refined"

REFINED_DIR.mkdir(parents=True, exist_ok=True)

DRUGS_CSV = REFINED_DIR / "drugs.csv"
MEDICINES_CSV = REFINED_DIR / "jan_aushadhi_medicines.csv"
COMPOSITION_CSV = REFINED_DIR / "jan_aushadhi_composition.csv"

# ==================================================
# Category keywords
# ==================================================
CATEGORY_KEYWORDS = {
    "tablet": "tablet",
    "tablets": "tablet",
    "capsule": "capsule",
    "capsules": "capsule",
    "injection": "injection",
    "syrup": "syrup",
    "spray": "spray",
    "gel": "gel",
    "cream": "cream",
    "ointment": "ointment",
    "solution": "solution",
    "drop": "drops",
    "drops": "drops"
}

CATEGORY_WORDS = set(CATEGORY_KEYWORDS.keys())

REDUNDANT_WORDS = {
    "and", "for", "with",
    "suspension", "resistant",
    "oral", "orally",
    "disintegrating",
    "paediatric", "pediatric"
}

# ==================================================
# Helpers (UNCHANGED)
# ==================================================
def remove_brackets(text: str) -> str:
    return re.sub(r'\([^)]*\)', '', text)


def normalize_percent_units(text: str) -> str:
    text = re.sub(r'%\s*w\s*/\s*w', '%w/w', text, flags=re.IGNORECASE)
    text = re.sub(r'%\s*w\s*/\s*v', '%w/v', text, flags=re.IGNORECASE)
    return text


def protect_percent_units(text: str) -> str:
    return (
        text.replace("%w/w", "__PERCENT_W_W__")
            .replace("%w/v", "__PERCENT_W_V__")
    )


def restore_percent_units(text: str) -> str:
    return (
        text.replace("__PERCENT_W_W__", "%w/w")
            .replace("__PERCENT_W_V__", "%w/v")
    )


def normalize_per_expressions(text: str) -> str:
    pattern = r'''
        (\d+(?:\.\d+)?)\s*
        (mg|mcg|g|gm|kg)\s*
        (?:per|/)\s*
        (\d+(?:\.\d+)?)?\s*
        (ml|l)
    '''

    def repl(m):
        a, au = m.group(1), m.group(2)
        b, bu = m.group(3) or "1", m.group(4)
        return f"{a}/{b} {au}/{bu}"

    return re.sub(pattern, repl, text, flags=re.IGNORECASE | re.VERBOSE)


def remove_noise_words(text: str) -> str:
    return " ".join(
        w for w in text.split()
        if w.lower() not in REDUNDANT_WORDS
        and w.lower() not in CATEGORY_WORDS
    )


def extract_category(text: str) -> str:
    t = text.lower()
    for k, v in CATEGORY_KEYWORDS.items():
        if k in t:
            return v
    return "unknown"


def extract_dosage_endpoints(text: str):
    pattern = r'''
        (\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?)\s*
        (
            mg/ml |
            g/l |
            mg |
            mcg |
            g |
            gm |
            kg |
            ml |
            l |
            iu |
            billion |
            %w/w |
            %w/v |
            %
        )
    '''
    return [
        (m.end(), m.group(1), m.group(2).lower())
        for m in re.finditer(pattern, text, flags=re.IGNORECASE | re.VERBOSE)
    ]


def normalize_drug_name(component: str) -> str:
    component = re.sub(
        r'\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?\s*\S+',
        '',
        component
    )
    words = [w for w in component.split() if w.lower() not in REDUNDANT_WORDS]
    return " ".join(words).strip(" ,+-")


def parse_composition(text: str):
    endpoints = extract_dosage_endpoints(text)
    results = []
    prev = 0

    for end, amount, unit in endpoints:
        part = text[prev:end]
        prev = end
        drug = normalize_drug_name(part)
        if drug:
            results.append((drug, amount, unit))
    return results

# ==================================================
# Write refined CSVs
# ==================================================
drug_id_map = {}
drug_id = 1
medicine_id = 1

with open(DRUGS_CSV, "w", newline="", encoding="utf-8") as df, \
     open(MEDICINES_CSV, "w", newline="", encoding="utf-8") as mf, \
     open(COMPOSITION_CSV, "w", newline="", encoding="utf-8") as cf:

    drugs_writer = csv.writer(df)
    meds_writer = csv.writer(mf)
    comp_writer = csv.writer(cf)

    drugs_writer.writerow(["drug_id", "drug_name"])
    meds_writer.writerow(["medicine_id", "medicine_name", "unit_size", "mrp", "group_name", "category"])
    comp_writer.writerow(["medicine_id", "drug_id", "amount", "unit"])

    with open(RAW_CSV, newline="", encoding="utf-8") as raw:
        reader = csv.DictReader(raw)

        for row in reader:
            raw_name = row["Generic Name"]
            category = extract_category(raw_name)

            t = remove_brackets(raw_name)
            t = normalize_percent_units(t)
            t = protect_percent_units(t)
            t = normalize_per_expressions(t)
            t = remove_noise_words(t)
            t = restore_percent_units(t)

            meds_writer.writerow([
                medicine_id,
                raw_name,
                row["Unit Size"],
                row["MRP"],
                row["Group Name"],
                category
            ])

            for drug, amount, unit in parse_composition(t):
                if drug not in drug_id_map:
                    drug_id_map[drug] = drug_id
                    drugs_writer.writerow([drug_id, drug])
                    drug_id += 1

                comp_writer.writerow([
                    medicine_id,
                    drug_id_map[drug],
                    amount,
                    unit
                ])

            medicine_id += 1

print("✅ Generated refined CSVs with amount + unit preserved (READY FOR REVIEW)")
