"""
Backend API for RxLens medicine recommendation system
Provides RESTful endpoints for medicine search and alternative recommendations
Includes both composition-based and ML-based recommendation engines
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List, Tuple
from rapidfuzz import fuzz

from etl import load_data, Medicine, CompositionItem
from matching import find_substitutes, CandidateScore

# Import ML module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.model import MedicineMatcher

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Data paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'refined')
MEDICINES_CSV = os.path.join(DATA_DIR, 'jan_aushadhi_medicines.csv')
COMPOSITION_CSV = os.path.join(DATA_DIR, 'jan_aushadhi_composition.csv')

# Global cache for medicines and drug index
_medicines_cache: Dict[int, Medicine] = {}
_drug_index_cache: Dict[int, List[Medicine]] = {}
_cache_loaded = False

# ML Model cache
_ml_matcher: MedicineMatcher = None
_ml_medicines_df = None
_ml_model_loaded = False


def _load_cache():
    """Load data into cache"""
    global _medicines_cache, _drug_index_cache, _cache_loaded, _ml_matcher, _ml_medicines_df, _ml_model_loaded
    if not _cache_loaded:
        try:
            _medicines_cache, _drug_index_cache = load_data(MEDICINES_CSV, COMPOSITION_CSV)
            _cache_loaded = True
            print(f"Loaded {len(_medicines_cache)} medicines from database")
        except Exception as e:
            print(f"Error loading medicines: {e}")
            raise
    
    # Load ML model
    if not _ml_model_loaded:
        try:
            ml_model_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'medicine_matcher.pkl')
            if os.path.exists(ml_model_path):
                _ml_matcher = MedicineMatcher.load(ml_model_path)
                _ml_model_loaded = True
                print(f"Loaded ML model from {ml_model_path}")
            else:
                print(f"⚠️  ML model not found at {ml_model_path}. ML endpoints will not be available.")
                _ml_model_loaded = True  # Mark as attempted to avoid repeated tries
        except Exception as e:
            print(f"Warning: Could not load ML model: {e}")
            _ml_model_loaded = True


def _serialize_composition(composition):
    """Convert CompositionItem objects to serializable dict"""
    return [
        {
            'drug_id': c.drug_id,
            'amount': c.amount,
            'unit': c.unit
        }
        for c in composition
    ]


def _serialize_medicine(medicine: Medicine) -> dict:
    """Convert Medicine object to JSON-serializable dict"""
    return {
        'medicine_id': medicine.medicine_id,
        'name': medicine.name,
        'price': medicine.price,
        'unit_size': medicine.unit_size,
        'group_name': medicine.group_name,
        'category': medicine.category,
        'composition': _serialize_composition(medicine.composition)
    }


def _serialize_candidate_score(candidate: CandidateScore) -> dict:
    """Convert CandidateScore object to JSON-serializable dict"""
    return {
        'medicine': _serialize_medicine(candidate.medicine),
        'score': candidate.score,
        'comp_similarity': candidate.comp_similarity,
        'price_score': candidate.price_score
    }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'RxLens API'})


@app.route('/api/medicines', methods=['GET'])
def get_all_medicines():
    """
    GET endpoint to retrieve all medicines
    Optional query params:
    - limit: number of medicines to return (default: 100)
    - offset: pagination offset (default: 0)
    """
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        medicines_list = list(_medicines_cache.values())
        total = len(medicines_list)
        
        paginated = medicines_list[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'total': total,
            'count': len(paginated),
            'limit': limit,
            'offset': offset,
            'medicines': [_serialize_medicine(m) for m in paginated]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/medicines/<int:medicine_id>', methods=['GET'])
def get_medicine(medicine_id: int):
    """
    GET endpoint to retrieve a specific medicine by ID
    
    Args:
        medicine_id: ID of the medicine
    
    Returns:
        JSON with medicine details or error
    """
    try:
        if medicine_id not in _medicines_cache:
            return jsonify({
                'success': False,
                'error': f'Medicine with ID {medicine_id} not found'
            }), 404
        
        medicine = _medicines_cache[medicine_id]
        return jsonify({
            'success': True,
            'medicine': _serialize_medicine(medicine)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/search', methods=['POST'])
def search_medicines():
    """
    POST endpoint to search for medicines by name using fuzzy matching
    
    Request body:
    {
        'query': 'medicine name',
        'threshold': 60  (optional, default: 60)
    }
    
    Returns:
        JSON with matched medicine or error if no good match found
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: query'
            }), 400
        
        query = data.get('query', '').strip()
        threshold = data.get('threshold', 60)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        best_match = None
        best_score = 0
        
        # Fuzzy search through all medicines
        for med in _medicines_cache.values():
            score = fuzz.token_set_ratio(query.lower(), med.name.lower())
            if score > best_score:
                best_score = score
                best_match = med
        
        if best_score >= threshold and best_match:
            return jsonify({
                'success': True,
                'medicine': _serialize_medicine(best_match),
                'similarity_score': best_score
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No good match found (best match: {best_score}% similarity)',
                'best_match_score': best_score
            }), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/substitutes', methods=['POST'])
def get_substitutes():
    """
    POST endpoint to find substitute medicines for a given medicine
    
    Request body:
    {
        'medicine_id': 123,  (required)
        'top_k': 5  (optional, default: 10)
    }
    
    Returns:
        JSON with list of substitute medicines ranked by score
    """
    try:
        data = request.get_json()
        
        if not data or 'medicine_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: medicine_id'
            }), 400
        
        medicine_id = data.get('medicine_id')
        top_k = data.get('top_k', 10)
        
        if medicine_id not in _medicines_cache:
            return jsonify({
                'success': False,
                'error': f'Medicine with ID {medicine_id} not found'
            }), 404
        
        # Get substitutes
        substitutes = find_substitutes(medicine_id, _medicines_cache, _drug_index_cache, top_k=top_k)
        
        return jsonify({
            'success': True,
            'medicine_id': medicine_id,
            'count': len(substitutes),
            'substitutes': [_serialize_candidate_score(s) for s in substitutes]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/analyze-prescription', methods=['POST'])
def analyze_prescription():
    """
    POST endpoint to analyze a full prescription for multiple medicines
    
    Request body:
    {
        'medicines': ['Paracetamol', 'Aspirin'],  (required)
        'top_k': 5  (optional, default: 5)
    }
    
    Returns:
        JSON with analysis results for all medicines
    """
    try:
        data = request.get_json()
        
        if not data or 'medicines' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: medicines'
            }), 400
        
        medicines_list = data.get('medicines', [])
        top_k = data.get('top_k', 5)
        
        if not isinstance(medicines_list, list) or len(medicines_list) == 0:
            return jsonify({
                'success': False,
                'error': 'medicines must be a non-empty list'
            }), 400
        
        results = {}
        
        for med_name in medicines_list:
            med_name = str(med_name).strip()
            if not med_name:
                continue
            
            # Search for the medicine
            best_match = None
            best_score = 0
            
            for med in _medicines_cache.values():
                score = fuzz.token_set_ratio(med_name.lower(), med.name.lower())
                if score > best_score:
                    best_score = score
                    best_match = med
            
            if best_score >= 60 and best_match:
                # Find substitutes
                substitutes = find_substitutes(best_match.medicine_id, _medicines_cache, _drug_index_cache, top_k=top_k)
                results[med_name] = {
                    'status': 'found',
                    'original_medicine': _serialize_medicine(best_match),
                    'similarity_score': best_score,
                    'substitutes': [_serialize_candidate_score(s) for s in substitutes]
                }
            else:
                results[med_name] = {
                    'status': 'not_found',
                    'error': f'No good match found (best: {best_score}% match)',
                    'best_match_score': best_score
                }
        
        # Calculate summary
        found_count = sum(1 for r in results.values() if r['status'] == 'found')
        not_found_count = len(results) - found_count
        total_alternatives = sum(len(r.get('substitutes', [])) for r in results.values() if r['status'] == 'found')
        
        return jsonify({
            'success': True,
            'summary': {
                'total_medicines': len(results),
                'found_count': found_count,
                'not_found_count': not_found_count,
                'total_alternatives': total_alternatives
            },
            'results': results
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============= ML-BASED ENDPOINTS =============

@app.route('/api/ml/search', methods=['POST'])
def ml_search():
    """
    ML-based medicine search using TF-IDF + Cosine Similarity
    More flexible than fuzzy matching, handles synonyms better
    
    Request body:
    {
        'query': 'medicine name or description',
        'top_k': 5  (optional, default: 5)
    }
    
    Returns:
        JSON with matched medicines ranked by TF-IDF similarity
    """
    try:
        if not _ml_matcher:
            return jsonify({
                'success': False,
                'error': 'ML model not loaded. Using fuzzy matching instead.'
            }), 503
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: query'
            }), 400
        
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Get matches from ML model
        matches_df = _ml_matcher.find_matches(query, top_k=top_k)
        
        if matches_df.empty:
            return jsonify({
                'success': False,
                'error': 'No matches found for the query'
            }), 404
        
        # Convert to serializable format
        results = []
        for idx, row in matches_df.iterrows():
            results.append({
                'medicine_id': int(row['medicine_id']),
                'name': row['medicine_name'],
                'price': float(row['mrp']),
                'unit_size': row['unit_size'],
                'group_name': row['group_name'],
                'category': row['category'],
                'similarity_score': float(row['similarity_score'])
            })
        
        return jsonify({
            'success': True,
            'method': 'TF-IDF (ML)',
            'query': query,
            'count': len(results),
            'matches': results
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/ml/compare', methods=['POST'])
def ml_compare():
    """
    Compare results from both fuzzy matching and ML-based search
    Useful for understanding which method works better for different queries
    
    Request body:
    {
        'query': 'medicine name',
        'top_k': 5  (optional, default: 5)
    }
    
    Returns:
        JSON with results from both methods for comparison
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: query'
            }), 400
        
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        comparison = {
            'query': query,
            'methods': {}
        }
        
        # Method 1: Fuzzy Matching (existing)
        try:
            best_match = None
            best_score = 0
            
            for med in _medicines_cache.values():
                score = fuzz.token_set_ratio(query.lower(), med.name.lower())
                if score > best_score:
                    best_score = score
                    best_match = med
            
            if best_score >= 60 and best_match:
                comparison['methods']['fuzzy_matching'] = {
                    'status': 'success',
                    'medicine': _serialize_medicine(best_match),
                    'similarity_score': best_score
                }
            else:
                comparison['methods']['fuzzy_matching'] = {
                    'status': 'no_match',
                    'best_score': best_score
                }
        except Exception as e:
            comparison['methods']['fuzzy_matching'] = {'status': 'error', 'error': str(e)}
        
        # Method 2: ML-based Search
        try:
            if _ml_matcher:
                matches_df = _ml_matcher.find_matches(query, top_k=3)
                if not matches_df.empty:
                    ml_results = []
                    for idx, row in matches_df.iterrows():
                        ml_results.append({
                            'medicine_id': int(row['medicine_id']),
                            'name': row['medicine_name'],
                            'price': float(row['mrp']),
                            'similarity_score': float(row['similarity_score'])
                        })
                    comparison['methods']['ml_tfidf'] = {
                        'status': 'success',
                        'matches': ml_results
                    }
                else:
                    comparison['methods']['ml_tfidf'] = {
                        'status': 'no_match'
                    }
            else:
                comparison['methods']['ml_tfidf'] = {
                    'status': 'unavailable',
                    'reason': 'ML model not loaded'
                }
        except Exception as e:
            comparison['methods']['ml_tfidf'] = {'status': 'error', 'error': str(e)}
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found. Use /api/* endpoints or /api/health for health check'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Load data before starting server
    _load_cache()
    
    # Run Flask app
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True
    )
