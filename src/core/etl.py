from typing import Dict, Tuple, List
import pandas as pd
from dataclasses import dataclass


@dataclass
class CompositionItem:
    drug_id: int
    amount: float
    unit: str


@dataclass
class Medicine:
    medicine_id: int
    name: str
    price: float
    unit_size: str
    group_name: str
    category: str
    composition: List[CompositionItem]


def _parse_fraction(value: str) -> float:
    """Parse numbers like '125', '125/5', '25/1' -> numeric value."""
    if pd.isna(value):
        raise ValueError("Empty amount")
    s = str(value).strip()
    if '/' in s:
        num, denom = s.split('/')
        try:
            return float(num) / float(denom)
        except Exception:
            return float(num)
    try:
        return float(s)
    except Exception as e:
        raise


def _normalize_unit(amount: float, unit: str) -> Tuple[float, str]:
    """Convert common units to mg base where possible. Return (value_in_base, base_unit)."""
    if unit is None:
        return amount, ''
    u = unit.strip().lower()
    if u in ['mg']:
        return amount, 'mg'
    if u in ['g']:
        return amount * 1000.0, 'mg'
    if u in ['mcg', '\u00b5g', '\u00b5g/ml', '\u00b5g/1']:
        # micrograms -> mg
        return amount / 1000.0, 'mg'
    # for %w/w, %w/v, iu, mg/ml and other composite units, keep as-is
    return amount, u


def load_data(medicines_csv: str, composition_csv: str) -> Tuple[Dict[int, Medicine], Dict[int, List[Medicine]]]:
    """Load medicines and composition CSVs and return medicines map and drug->med index.

    - medicines_csv: path to jan_aushadhi_medicines.csv
    - composition_csv: path to jan_aushadhi_composition.csv
    """
    meds_df = pd.read_csv(medicines_csv)
    comp_df = pd.read_csv(composition_csv)

    medicines: Dict[int, Medicine] = {}
    drug_index: Dict[int, List[Medicine]] = {}

    # pre-group composition by medicine_id
    grouped = comp_df.groupby('medicine_id')

    for _, row in meds_df.iterrows():
        mid = int(row['medicine_id'])
        name = row.get('medicine_name', '')
        price = float(row.get('mrp', 0.0)) if not pd.isna(row.get('mrp', None)) else 0.0
        unit_size = row.get('unit_size', '')
        group_name = row.get('group_name', '')
        category = row.get('category', '')

        comp_items: List[CompositionItem] = []
        if mid in grouped.groups:
            for _, crow in grouped.get_group(mid).iterrows():
                try:
                    raw_amt = crow['amount']
                    parsed = _parse_fraction(raw_amt)
                    normalized_amt, normalized_unit = _normalize_unit(parsed, crow['unit'])
                    comp_items.append(CompositionItem(int(crow['drug_id']), normalized_amt, normalized_unit))
                except Exception:
                    # skip malformed composition rows
                    continue

        med = Medicine(medicine_id=mid, name=name, price=price, unit_size=unit_size, group_name=group_name, category=category, composition=comp_items)
        medicines[mid] = med

    # build inverted index
    for med in medicines.values():
        for c in med.composition:
            drug_index.setdefault(c.drug_id, []).append(med)

    return medicines, drug_index
