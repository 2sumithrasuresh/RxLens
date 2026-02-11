from dataclasses import dataclass
from typing import List, Dict, Tuple, Iterable
try:
    from .etl import CompositionItem, Medicine, load_data
except Exception:
    # allow running as a script (no package) by adding the current package dir to sys.path
    import sys, os
    pkg_dir = os.path.abspath(os.path.dirname(__file__))
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)
    from etl import CompositionItem, Medicine, load_data


@dataclass
class CandidateScore:
    medicine: Medicine
    score: float
    comp_similarity: float
    price_score: float


def composition_signature(composition: Iterable[CompositionItem]) -> frozenset:
    """Return canonical signature as frozenset of (drug_id, rounded_amount, unit)"""
    sig = set()
    for c in composition:
        # round to reasonable precision
        amt = round(float(c.amount), 6)
        sig.add((int(c.drug_id), amt, c.unit or ''))
    return frozenset(sig)


def composition_similarity(sig_a: frozenset, sig_b: frozenset, dose_tol: float = 0.05) -> float:
    """Compute a simple similarity between two composition signatures (0..1).

    Strategy:
      - If exact set equality -> 1.0
      - Otherwise count drug-level matches where unit matches and dose within tolerance
      - Score = matched_count / max(len(a), len(b))
    """
    a = set(sig_a)
    b = set(sig_b)
    if a == b:
        return 1.0
    matches = 0
    for da in a:
        for db in b:
            if da[0] == db[0] and da[2] == db[2]:
                da_amt = da[1]
                db_amt = db[1]
                if max(da_amt, db_amt, 1e-9) == 0:
                    continue
                if abs(da_amt - db_amt) <= dose_tol * max(da_amt, db_amt, 1e-9):
                    matches += 1
    denom = max(len(a), len(b))
    return matches / denom if denom > 0 else 0.0


def find_candidates_by_ingredients(drug_index: Dict[int, List[Medicine]], query_comp: List[CompositionItem]) -> List[Medicine]:
    # Use medicine_id to deduplicate since Medicine is not hashable
    med_ids = set()
    med_by_id: Dict[int, Medicine] = {}
    for c in query_comp:
        for m in drug_index.get(c.drug_id, []):
            if m.medicine_id not in med_ids:
                med_ids.add(m.medicine_id)
                med_by_id[m.medicine_id] = m
    return list(med_by_id.values())


def rank_candidates(ref_med: Medicine, candidates: List[Medicine], weights: Dict[str, float] = None, top_k: int = 10) -> List[CandidateScore]:
    if weights is None:
        weights = {'comp': 0.7, 'price': 0.3}
    ref_sig = composition_signature(ref_med.composition)
    scored: List[CandidateScore] = []
    for c in candidates:
        c_sig = composition_signature(c.composition)
        s_comp = composition_similarity(ref_sig, c_sig)
        # price_score: lower price -> higher score, bounded [0,1]
        price_score = 1.0 - min(1.0, (c.price / max(ref_med.price, 1e-9)))
        score = weights['comp'] * s_comp + weights['price'] * price_score
        scored.append(CandidateScore(medicine=c, score=score, comp_similarity=s_comp, price_score=price_score))
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:top_k]


def find_substitutes(medicine_id: int, medicines: Dict[int, Medicine], drug_index: Dict[int, List[Medicine]], top_k: int = 10) -> List[CandidateScore]:
    if medicine_id not in medicines:
        return []
    ref = medicines[medicine_id]
    candidates = find_candidates_by_ingredients(drug_index, ref.composition)
    # exclude the reference itself
    candidates = [c for c in candidates if c.medicine_id != ref.medicine_id]
    ranked = rank_candidates(ref, candidates, top_k=top_k)
    return ranked


if __name__ == '__main__':
    # quick demo using package CSVs relative to the repository root (this file's location)
    import os, sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    refined_dir = os.path.join(project_root, 'data', 'refined')
    med_csv = os.path.join(refined_dir, 'jan_aushadhi_medicines.csv')
    comp_csv = os.path.join(refined_dir, 'jan_aushadhi_composition.csv')
    if not (os.path.exists(med_csv) and os.path.exists(comp_csv)):
        print(f"Data files not found. Expected at: {med_csv} and {comp_csv}")
        sys.exit(1)

    medicines, drug_index = load_data(med_csv, comp_csv)
    # pick paracetamol tablet id 22 as example
    if 22 in medicines:
        subs = find_substitutes(22, medicines, drug_index, top_k=5)
        if not subs:
            print("No substitutes found for medicine id 22")
        for s in subs:
            print(f"{s.medicine.medicine_id}\t{s.medicine.name}\tscore={s.score:.3f}\tsim={s.comp_similarity:.3f}\tprice_score={s.price_score:.3f}")
