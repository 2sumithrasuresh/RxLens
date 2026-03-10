import sys
import os
import pandas as pd

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ml.data_loader import build_searchable_dataset
from ml.features import ContentEmbedder
from ml.model import MedicineMatcher

def main():
    print("---- RxLens Interactive Tester ----")
    model_path = os.path.join(os.path.dirname(__file__), 'medicine_matcher.pkl')
    
    matcher = None
    
    # Try to load existing model
    if os.path.exists(model_path):
        print(f"Loading saved model from {model_path}...")
        try:
            matcher = MedicineMatcher.load(model_path)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Will retrain model.")
            matcher = None
    
    # Train if not loaded
    if matcher is None:
        print("Loading data and training model...")
        try:
            generic_df, branded_df = build_searchable_dataset()
            embedder = ContentEmbedder()
            matcher = MedicineMatcher(embedder)
            matcher.train(generic_df, branded_df)
            print("Model trained.")
        except Exception as e:
            print(f"Critical Error: {e}")
            return

    print("\n------------------------------------------------")
    print("Type a medicine name to find generic equivalents.")
    print("Type 'exit' or 'quit' to stop.")
    print("------------------------------------------------")

    while True:
        try:
            query = input("\nEnter medicine name: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query:
                continue
                
            matches, branded_info = matcher.find_matches(query, top_k=5)
            
            if branded_info:
                 print(f"\n[ Brand Matched: '{branded_info['brand_name']}' - '{branded_info['medicine_name']}' ]")
                 print(f"[ Composition Used for Search: {branded_info['composition']} ]")

            if matches.empty:
                print(f"\nNo matches found for '{query}'.")
                continue
                
            print(f"\nTop {len(matches)} Matches for '{query}':")
            for idx, row in matches.iterrows():
                print(f"  - {row['medicine_name']}")
                print(f"    Similarity: {row['similarity_score']:.4f}")
                print(f"    MRP: ₹{row['mrp']}")
                print(f"    Unit: {row['unit_size']}")
                print("    ---")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error processing query: {e}")

    print("\nGoodbye!")

if __name__ == "__main__":
    main()
