from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np

class ContentEmbedder:
    def __init__(self):
        # TF-IDF Vectorizer
        # analyzer='word': tokens are words
        # ngram_range=(1, 3): Unigrams, bigrams, and trigrams (captured '500 mg', 'paracetamol 500')
        # stop_words='english': Remove common words
        self.vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english')
        
    def fit(self, corpus):
        """
        Fits the TF-IDF vectorizer on the list of medicine names/compositions.
        
        Args:
            corpus (list or pd.Series): Text data to learn vocabulary from.
        """
        print("Fitting TF-IDF vectorizer...")
        self.vectorizer.fit(corpus)
        
    def transform(self, text_data):
        """
        Transforms text data into TF-IDF vectors.
        
        Args:
            text_data (list or pd.Series or str): Text to transform.
            
        Returns:
            scipy.sparse.csr_matrix: TF-IDF matrix.
        """
        if isinstance(text_data, str):
            text_data = [text_data]
            
        return self.vectorizer.transform(text_data)

if __name__ == "__main__":
    # Test
    corpus = [
        "Paracetamol 500mg Tablets",
        "Aceclofenac 100mg and Paracetamol 325mg",
        "Amoxycillin 500mg Capsules"
    ]
    embedder = ContentEmbedder()
    embedder.fit(corpus)
    
    query = "Dolo 650"
    vector = embedder.transform(query)
    print(f"Query: '{query}'")
    print(f"Vector shape: {vector.shape}")
