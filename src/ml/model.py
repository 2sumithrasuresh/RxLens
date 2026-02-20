from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import pickle
import os
import warnings

# Suppress sklearn version warnings for pickle compatibility
warnings.filterwarnings('ignore', category=UserWarning)

class MedicineMatcher:
    def __init__(self, embedder):
        """
        Args:
            embedder (ContentEmbedder): Instance of the feature engineer/embedder.
        """
        self.embedder = embedder
        self.tfidf_matrix = None
        self.medicines_df = None
        
    def train(self, df, text_column='medicine_name'):
        """
        Builds the validation matrix for the database.
        
        Args:
            df (pd.DataFrame): DataFrame containing medicine data.
            text_column (str): Column to vectorise.
        """
        self.medicines_df = df.reset_index(drop=True)
        # Fit embedder on the corpus
        self.embedder.fit(self.medicines_df[text_column])
        # Transform the corpus
        print("Building search index...")
        self.tfidf_matrix = self.embedder.transform(self.medicines_df[text_column])
        
    def find_matches(self, query, top_k=5):
        """
        Finds the most similar medicines to the query.
        
        Args:
            query (str): The search text (e.g., brand name or composition).
            top_k (int): Number of results to return.
            
        Returns:
            pd.DataFrame: Top k matches with similarity scores.
        """
        if self.tfidf_matrix is None:
            raise ValueError("Model not trained. Call train() first.")
            
        # Vectorise query
        query_vec = self.embedder.transform(query)
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = cosine_sim.argsort()[-top_k:][::-1]
        
        # Retrieve results
        results = self.medicines_df.iloc[top_indices].copy()
        results['similarity_score'] = cosine_sim[top_indices]
        
        # Filter out zero-similarity matches
        results = results[results['similarity_score'] > 0.0]
        
        return results

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump({
                'embedder': self.embedder,
                'tfidf_matrix': self.tfidf_matrix,
                'medicines_df': self.medicines_df
            }, f)
            print(f"Model saved to {filepath}")
            
    @staticmethod
    def load(filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file {filepath} not found.")
        
        try:
            with open(filepath, 'rb') as f:
                # Attempt to load with protocol used during save
                data = pickle.load(f, encoding='utf-8')
            
            matcher = MedicineMatcher(data['embedder'])
            matcher.tfidf_matrix = data['tfidf_matrix']
            matcher.medicines_df = data['medicines_df']
            return matcher
        except Exception as e:
            # If unpickling fails, raise more informative error
            raise ValueError(f"Failed to load ML model: {str(e)}. The model may be corrupted or incompatible with the current scikit-learn version. Please retrain by running: python src/ml/demo.py")
