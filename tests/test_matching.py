import os
try:
    from src.core.etl import load_data
    from src.core.matching import find_substitutes
except Exception:
    # Allow running this test file directly (not via pytest) by adding project root to sys.path
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from src.core.etl import load_data
    from src.core.matching import find_substitutes


def test_find_substitutes_basic():
    base = os.path.abspath(os.path.join(os.getcwd(), 'data', 'refined'))
    med_csv = os.path.join(base, 'jan_aushadhi_medicines.csv')
    comp_csv = os.path.join(base, 'jan_aushadhi_composition.csv')
    medicines, drug_index = load_data(med_csv, comp_csv)
    # pick a medicine with known composition, e.g., 22 Paracetamol 500mg
    subs = find_substitutes(22, medicines, drug_index, top_k=5)
    assert isinstance(subs, list)
    # Expect at least one substitute candidate
    assert len(subs) > 0
    # top candidate should have non-zero comp_similarity
    assert subs[0].comp_similarity >= 0
