# RxLens ML Module

This directory contains the Machine Learning logic for RxLens. It implements a content-based recommendation engine to find generic medicine equivalents for branded medicines.

## Structure

*   `data_loader.py`: Parses the `database/jan_aushadhi_medicines.sql` file to load medicine data.
*   `features.py`: Implements `ContentEmbedder` using TF-IDF vectorization to convert medicine names into numerical vectors.
*   `model.py`: Implements `MedicineMatcher` which uses Cosine Similarity to find the closest matches in the database for a given query.
*   `demo.py`: A demonstration script that loads data, trains the model, and runs sample queries.

## Usage

1.  **Install Dependencies:**
    ```bash
    pip install pandas numpy scikit-learn
    ```

2.  **Run Demo:**
    ```bash
    python src/ml/demo.py
    ```

    This will:
    - Load medicine data from the SQL dump.
    - Build the search index (TF-IDF matrix).
    - Run sample queries (e.g., "Dolo 650", "Augmentin").
    - Save the trained model to `src/ml/medicine_matcher.pkl`.

## Integration

To use this in the main application:
1.  Initialize `MedicineMatcher`.
2.  Load the saved model or retrain.
3.  Call `matcher.find_matches(query_string)`.

## Methodology

*   **Data Source:** Jan Aushadhi medicines list.
*   **Vectorization:** TF-IDF (Term Frequency-Inverse Document Frequency) on medicine names (unigrams, bigrams, trigrams).
*   **Similarity:** Cosine Similarity between the query vector and the database vectors.
