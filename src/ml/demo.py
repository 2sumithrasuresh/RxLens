import sys
import os
import pandas as pd

# Add src to python path to allow imports if running from root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ml.data_loader import load_data
from ml.features import ContentEmbedder
from ml.model import MedicineMatcher

def main():
    print("---- Starting RxLens ML Demo (Medicine Matcher) ----")
    
    # 1. Load Data
    print("\n1. Loading Data from SQL dump...")
    try:
        df = load_data()
    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    # 2. Train Model (Build Index)
    print("\n2. Building Search Index...")
    embedder = ContentEmbedder()
    matcher = MedicineMatcher(embedder)
    matcher.train(df)
    
    # 3. Sample Queries
    queries = [
        "Paracetamol 500",
        "Dolo 650", 
        "Augmentin 625",
        "Amoxycillin",
        "Metformin 500",
        "Cough Syrup"
    ]
    
    print("\n3. Running Sample Queries...")
    for query in queries:
        print(f"\nQUERY: '{query}'")
        matches = matcher.find_matches(query, top_k=3)
        
        # Display results cleanly
        for idx, row in matches.iterrows():
            print(f"  - [{row['similarity_score']:.4f}] {row['medicine_name']} (MRP: {row['mrp']})")

    # 4. Save Model
    print("\n4. Saving Model...")
    model_path = os.path.join(os.path.dirname(__file__), 'medicine_matcher.pkl')
    matcher.save(model_path)
    
    print("\n---- Demo Complete ----")

if __name__ == "__main__":
    main()
