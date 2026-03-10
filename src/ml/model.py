from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import pickle
import os

class MedicineMatcher:
    def __init__(self, embedder):
        """
        Args:
            embedder (ContentEmbedder): Instance of the feature engineer/embedder.
        """
        self.embedder = embedder
        self.tfidf_matrix = None
        self.medicines_df = None
        self.branded_df = None
        
    def train(self, generic_df, branded_df=None, text_column='search_text'):
        """
        Builds the validation matrix for the database.
        
        Args:
            generic_df (pd.DataFrame): DataFrame containing generic medicine data.
            branded_df (pd.DataFrame): DataFrame containing branded medicine data.
            text_column (str): Column to vectorise.
        """
        self.medicines_df = generic_df.reset_index(drop=True)
        if branded_df is not None:
            self.branded_df = branded_df.reset_index(drop=True)
            
        # Fit embedder on the corpus
        print("Fitting embedder...")
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
            
        search_query = query
        branded_info = None
        
        # Check if query matches a branded medicine
        if self.branded_df is not None:
            brand_match = self.branded_df[self.branded_df['brand_name'].str.lower() == query.lower()]
            if not brand_match.empty:
                search_query = brand_match.iloc[0]['composition']
                branded_info = brand_match.iloc[0].to_dict()
                
        # Vectorise query
        query_vec = self.embedder.transform(search_query)
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = cosine_sim.argsort()[-top_k:][::-1]
        
        # Retrieve results
        results = self.medicines_df.iloc[top_indices].copy()
        results['similarity_score'] = cosine_sim[top_indices]
        
        # Filter out zero-similarity matches
        results = results[results['similarity_score'] > 0.0]
        
        return results, branded_info

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump({
                'embedder': self.embedder,
                'tfidf_matrix': self.tfidf_matrix,
                'medicines_df': self.medicines_df,
                'branded_df': self.branded_df
            }, f)
            print(f"Model saved to {filepath}")
            
    @staticmethod
    def load(filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file {filepath} not found.")
            
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        matcher = MedicineMatcher(data['embedder'])
        matcher.tfidf_matrix = data['tfidf_matrix']
        matcher.medicines_df = data['medicines_df']
        matcher.branded_df = data.get('branded_df', None)
        return matcher
